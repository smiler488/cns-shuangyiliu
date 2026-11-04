# -*- coding: utf-8 -*-
"""Fetch CNS (Cell/Nature/Science) articles with Chinese participation, 2022-02-14 .. 2026-11-03.

Saves a slim JSONL with first-author institution info + corresponding flags.
"""
import json, os, time, requests, sys

KEY = os.environ.get("OPENALEX_API_KEY", "")  # optional; without it OpenAlex allows a lower polite-pool rate
BASE = "https://api.openalex.org"
OUT = r"C:\Users\micro\OneDrive\WechatOfficial\downloads\cns_stats\works_cns.jsonl"
STATE = r"C:\Users\micro\OneDrive\WechatOfficial\downloads\cns_stats\fetch_state.json"

ISSNS = {
    "Nature": ["0028-0836", "1476-4687"],
    "Science": ["0036-8075", "1095-9203"],
    "Cell": ["0092-8674", "1097-4172"],
}

def get(path, **params):
    params["api_key"] = KEY
    for attempt in range(5):
        r = requests.get(BASE + path, params=params, timeout=60)
        if r.status_code == 200:
            return r.json()
        if r.status_code == 429:
            wait = 5 * (attempt + 1)
            print(f"429, sleep {wait}s", flush=True)
            time.sleep(wait)
            continue
        print("ERR", r.status_code, r.text[:300], flush=True)
        r.raise_for_status()
    raise RuntimeError("too many retries")

def resolve_sources():
    ids = {}
    for jname, issns in ISSNS.items():
        found = set()
        for issn in issns:
            res = get("/sources", filter=f"issn:{issn}", per_page=5).get("results", [])
            for s in res:
                found.add((s["id"], s["display_name"], s.get("host_organization_name")))
        ids[jname] = sorted(found)
        print(jname, "->", ids[jname], flush=True)
    return ids

def main():
    src = resolve_sources()
    sid2journal = {}
    for jname, lst in src.items():
        for sid, disp, host in lst:
            # keep only the canonical journal, not related journals with same issn family
            if jname.lower() in disp.lower():
                sid2journal[sid] = jname
    print("sid2journal:", sid2journal, flush=True)
    all_sids = sorted(sid2journal.keys())

    sid_or = "|".join(s.split("/")[-1] for s in all_sids)
    filt = ",".join([
        f"primary_location.source.id:{sid_or}",
        "from_publication_date:2022-02-14",
        "to_publication_date:2026-11-03",
        "type:article",
        "authorships.institutions.country_code:cn",
    ])
    select = "id,doi,title,publication_date,authorships,primary_location"

    cursor = "*"
    total_done = 0
    with open(OUT, "w", encoding="utf-8") as fo:
        while True:
            data = get("/works", filter=filt, select=select, per_page=100, cursor=cursor)
            results = data.get("results", [])
            meta = data.get("meta", {})
            if total_done == 0:
                print("total count:", meta.get("count"), flush=True)
            for w in results:
                rec = {
                    "id": w["id"],
                    "doi": w.get("doi"),
                    "title": w.get("title"),
                    "pub": w.get("publication_date"),
                    "journal": sid2journal.get(((w.get("primary_location") or {}).get("source") or {}).get("id") or "", "?"),
                }
                auths = w.get("authorships") or []
                if auths:
                    a0 = auths[0]
                    rec["first_author"] = (a0.get("author") or {}).get("display_name")
                    rec["first_pos"] = a0.get("author_position")
                    rec["first_insts"] = [(i.get("id"), i.get("display_name")) for i in (a0.get("institutions") or [])]
                    rec["first_inst_ids"] = [i.get("id") for i in (a0.get("institutions") or [])]
                else:
                    rec["first_inst_ids"] = []
                rec["corr_inst_ids"] = []
                for a in auths:
                    if a.get("is_corresponding"):
                        rec["corr_inst_ids"] += [i.get("id") for i in (a.get("institutions") or [])]
                fo.write(json.dumps(rec, ensure_ascii=False) + "\n")
            total_done += len(results)
            cursor = meta.get("next_cursor")
            print(f"done {total_done}/{meta.get('count')}", flush=True)
            if not cursor or not results:
                break
            time.sleep(0.2)
    print("saved", OUT, "total", total_done, flush=True)

if __name__ == "__main__":
    main()
