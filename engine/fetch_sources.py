#!/usr/bin/env python3
"""Fetch archival images from Openverse and the NASA Image Library, with
the same licence discipline as fetch_commons.py: every downloaded file
lands in photos.json with credit, licence and source page recorded, and a
non-free licence is refused unless --allow-nonfree is passed.

photos.json entries name their source one of three ways (entries with a
plain "url" or "commons" key belong to fetch_commons.py):

  {"id": "P07", "kind": "photo", "openverse": "<openverse image uuid>"}
  {"id": "P08", "kind": "photo", "nasa": "<nasa_id>"}
  {"id": "P09", "kind": "photo", "openverse_search": "apollo 11 launch"}

  python3 fetch_sources.py get --project my-film
  python3 fetch_sources.py search openverse "wright brothers"
  python3 fetch_sources.py search nasa "apollo 11 launch"

NASA-produced imagery is public domain under NASA's media policy; the
ledger records the producing centre as credit and keeps the item's own
metadata page as the source, so any third-party exception stays traceable.
"""
import argparse, json, pathlib, re, sys, urllib.parse, urllib.request

UA = "angela-cinematic/1.3 (+https://github.com/dukangalex/angela-cinematic)"
FREE = re.compile(r"public domain|^pd\b|^pd-|cc0|cc[- ]by(?!.*\bnc\b)(?!.*\bnd\b)", re.I)
OV = "https://api.openverse.org/v1/images/"
NASA = "https://images-api.nasa.gov"


def get_json(url, tries=4):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # upstream 504s are routine; back off and retry
            last = e
            import time
            time.sleep(2 * (i + 1))
    raise last


def download(url, dst):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=300) as r, open(dst, "wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)


def ov_record(item):
    lic = (item.get("license") or "").upper()
    return dict(url=item["url"], source=item.get("foreign_landing_url") or item.get("detail_url", ""),
                credit=item.get("creator") or item.get("source") or "Openverse contributor",
                license=f"CC {lic}" if lic and not lic.startswith("CC") else (lic or "unknown"),
                license_url=item.get("license_url") or "")


def resolve_openverse(entry):
    if entry.get("openverse"):
        return ov_record(get_json(OV + urllib.parse.quote(entry["openverse"]) + "/"))
    q = urllib.parse.urlencode({"q": entry["openverse_search"], "page_size": 1,
                                "license_type": "all", "filter_dead": "false"})
    res = get_json(OV + "?" + q).get("results", [])
    if not res:
        raise RuntimeError(f"openverse: no result for {entry['openverse_search']!r}")
    return ov_record(res[0])


def resolve_nasa(entry):
    nid = entry["nasa"]
    meta = get_json(f"{NASA}/search?nasa_id={urllib.parse.quote(nid)}")
    items = meta.get("collection", {}).get("items", [])
    if not items:
        raise RuntimeError(f"nasa: no metadata for {nid!r}")
    data = items[0].get("data", [{}])[0]
    assets = get_json(f"{NASA}/asset/{urllib.parse.quote(nid)}").get("collection", {}).get("items", [])
    jpgs = [a["href"] for a in assets if a["href"].lower().endswith((".jpg", ".jpeg"))]
    if not jpgs:
        raise RuntimeError(f"nasa: no jpg asset for {nid!r}")
    big = max(jpgs, key=lambda u: ("orig" in u, "large" in u, len(u)))
    center = data.get("center", "")
    return dict(url=big, source=f"https://images.nasa.gov/details/{nid}",
                credit=f"NASA/{center}" if center else "NASA",
                license="Public domain", license_url="https://www.nasa.gov/nasa-brand-center/images-and-media/")


def cmd_get(a):
    proj = pathlib.Path(a.project)
    pj = proj / "photos.json"
    doc = json.loads(pj.read_text(encoding="utf-8"))
    photos_dir = proj / "assets" / "photos"
    photos_dir.mkdir(parents=True, exist_ok=True)
    done = 0
    for e in doc.get("photos", []):
        if e.get("file") or not ("openverse" in e or "openverse_search" in e or "nasa" in e):
            continue
        try:
            rec = resolve_openverse(e) if ("openverse" in e or "openverse_search" in e) else resolve_nasa(e)
        except Exception as ex:
            print(f"{e['id']}: FAILED to resolve ({ex}); entry left for a later run")
            continue
        ok = bool(FREE.search(rec["license"]))
        if not ok and not a.allow_nonfree:
            print(f"{e['id']}: REFUSED licence {rec['license']!r} (pass --allow-nonfree to own it)")
            continue
        name = f"{e['id']}_{pathlib.Path(urllib.parse.urlparse(rec['url']).path).name or 'image.jpg'}"
        try:
            download(rec["url"], photos_dir / name)
        except Exception as ex:
            print(f"{e['id']}: FAILED to download ({ex}); entry left for a later run")
            continue
        e.update(file=name, source=rec["source"], credit=rec["credit"],
                 license=rec["license"], license_url=rec["license_url"], license_ok=ok)
        pj.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
        done += 1
        print(f"{e['id']}: {name} ({rec['license']}, credit {rec['credit']})")
    print(f"fetched {done} file(s); ledger updated in {pj}")


def cmd_search(a):
    if a.source == "openverse":
        q = urllib.parse.urlencode({"q": a.query, "page_size": 8, "license_type": "all"})
        for r in get_json(OV + "?" + q).get("results", []):
            print(f"{r['id']}  CC {r.get('license', '?').upper():10s} {r.get('title', '')[:70]}")
    else:
        q = urllib.parse.urlencode({"q": a.query, "media_type": "image", "page_size": 8})
        for it in get_json(f"{NASA}/search?{q}").get("collection", {}).get("items", []):
            d = it.get("data", [{}])[0]
            print(f"{d.get('nasa_id', '?'):28s} {d.get('title', '')[:70]}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("get"); g.add_argument("--project", required=True)
    g.add_argument("--allow-nonfree", action="store_true"); g.set_defaults(fn=cmd_get)
    s = sub.add_parser("search"); s.add_argument("source", choices=["openverse", "nasa"])
    s.add_argument("query"); s.set_defaults(fn=cmd_search)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
