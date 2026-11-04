# -*- coding: utf-8 -*-
"""Map 147 Double First-Class universities to OpenAlex institution IDs."""
import json, os, time, sys, requests

API = "https://api.openalex.org/institutions"
SCHOOLS_FILE = r"C:\Users\micro\OneDrive\WechatOfficial\downloads\cns_stats\shuangyiliu_147.txt"
OUT = r"C:\Users\micro\OneDrive\WechatOfficial\downloads\cns_stats\school_openalex_map.json"

# Manual search-term overrides for tricky names
OVERRIDES = {
    "中国科学院大学": "University of Chinese Academy of Sciences",
    "北京协和医学院": "Peking Union Medical College",
    "国防科技大学": "National University of Defense Technology",
    "海军军医大学": "Naval Medical University",
    "空军军医大学": "Air Force Medical University",
    "上海体育大学": "Shanghai University of Sport",
    "中国矿业大学": "China University of Mining and Technology",
    "中国矿业大学(北京)": "China University of Mining and Technology, Beijing",
    "中国石油大学(华东)": "China University of Petroleum (East China)",
    "中国石油大学(北京)": "China University of Petroleum, Beijing",
    "中国地质大学(武汉)": "China University of Geosciences, Wuhan",
    "中国地质大学(北京)": "China University of Geosciences, Beijing",
}

def search_inst(term):
    r = requests.get(API, params={"search": term, "filter": "country_code:cn", "per-page": 5}, timeout=30)
    r.raise_for_status()
    return r.json().get("results", [])

def main():
    schools = [l.strip() for l in open(SCHOOLS_FILE, encoding="utf-8") if l.strip()]
    print(f"schools: {len(schools)}")
    out = {}
    for name in schools:
        term = OVERRIDES.get(name, name)
        try:
            res = search_inst(term)
        except Exception as e:
            out[name] = {"error": str(e)}
            continue
        cands = [{"id": r["id"], "display_name": r["display_name"],
                  "ror": r.get("ror"), "works_count": r.get("works_count"),
                  "alts": (r.get("display_name_alternatives") or [])[:4]} for r in res[:3]]
        out[name] = {"search_term": term, "candidates": cands}
        print(f"{name}: {[(c['id'].split('/')[-1], c['display_name']) for c in cands[:2]]}")
        time.sleep(0.12)
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("saved", OUT)

if __name__ == "__main__":
    main()
