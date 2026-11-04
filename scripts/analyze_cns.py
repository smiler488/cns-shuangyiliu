# -*- coding: utf-8 -*-
"""Analyze fetched CNS works: count per-school first-unit papers, build zero-list.

Calibers:
  A (strict):  first author's FIRST-listed institution
  B (first-all): all institutions of the first author
  C (first+corr): union of first-author and corresponding-author institutions
"""
import json, os, collections, re, sys

WORKS = r"C:\Users\micro\OneDrive\WechatOfficial\downloads\cns_stats\works_cns.jsonl"
MAPF = r"C:\Users\micro\OneDrive\WechatOfficial\downloads\cns_stats\school_openalex_map.json"
OUTDIR = r"C:\Users\micro\OneDrive\WechatOfficial\downloads\cns_stats"

# hospital -> parent university (manually curated for major affiliated hospitals)
HOSPITAL_PARENT = {
    # Sichuan University
    "West China Hospital, Sichuan University": "四川大学",
    "West China Second University Hospital, Sichuan University": "四川大学",
    "West China School of Stomatology, Sichuan University": "四川大学",
    # Peking Union Medical College
    "Peking Union Medical College Hospital": "北京协和医学院",
    "Peking Union Medical College": "北京协和医学院",
    "Chinese Academy of Medical Sciences": "北京协和医学院",
    # Peking University
    "Peking University First Hospital": "北京大学",
    "Peking University People's Hospital": "北京大学",
    "Peking University Third Hospital": "北京大学",
    "Peking University Sixth Hospital": "北京大学",
    "Peking University Shougang Hospital": "北京大学",
    # Tsinghua
    "Tsinghua University-Peking University Joint Center for Life Sciences": "清华大学",
    # Fudan
    "Huashan Hospital, Fudan University": "复旦大学",
    "Zhongshan Hospital, Fudan University": "复旦大学",
    "Fudan University Shanghai Cancer Center": "复旦大学",
    "Children's Hospital of Fudan University": "复旦大学",
    "Eye and ENT Hospital of Fudan University": "复旦大学",
    "Shanghai Obstetrics and Gynecology Hospital of Fudan University": "复旦大学",
    # SJTU
    "Renji Hospital, Shanghai Jiao Tong University": "上海交通大学",
    "Ruijin Hospital, Shanghai Jiao Tong University": "上海交通大学",
    "Xinhua Hospital, Shanghai Jiao Tong University": "上海交通大学",
    "Shanghai Jiao Tong University School of Medicine": "上海交通大学",
    "Shanghai Ninth People's Hospital, Shanghai Jiao Tong University School of Medicine": "上海交通大学",
    "Shanghai Sixth People's Hospital, Shanghai Jiao Tong University": "上海交通大学",
    # Zhejiang
    "First Affiliated Hospital, Zhejiang University School of Medicine": "浙江大学",
    "Sir Run Run Shaw Hospital": "浙江大学",
    "Women's Hospital, Zhejiang University School of Medicine": "浙江大学",
    "Zhejiang University School of Medicine": "浙江大学",
    # Sun Yat-sen
    "First Affiliated Hospital, Sun Yat-sen University": "中山大学",
    "Sun Yat-sen University Cancer Center": "中山大学",
    "Zhongshan Ophthalmic Center, Sun Yat-sen University": "中山大学",
    "Third Affiliated Hospital, Sun Yat-sen University": "中山大学",
    "Sixth Affiliated Hospital, Sun Yat-sen University": "中山大学",
    # Central South
    "Xiangya Hospital, Central South University": "中南大学",
    "Second Xiangya Hospital, Central South University": "中南大学",
    "Third Xiangya Hospital, Central South University": "中南大学",
    # Shandong
    "Qilu Hospital of Shandong University": "山东大学",
    "Second Hospital of Shandong University": "山东大学",
    # Zhejiang Chinese Medical / others
    "Tongji Hospital, Tongji Medical College, Huazhong University of Science and Technology": "华中科技大学",
    "Union Hospital, Tongji Medical College, Huazhong University of Science and Technology": "华中科技大学",
    "Wuhan Union Hospital": "华中科技大学",
    # Nanjing
    "First Affiliated Hospital of Nanjing Medical University": "南京医科大学",
    "Nanjing Drum Tower Hospital": "南京大学",
    "Affiliated Hospital of Nantong University": None,  # not 211
    # Wuhan
    "Renmin Hospital of Wuhan University": "武汉大学",
    "Zhongnan Hospital of Wuhan University": "武汉大学",
    # Harbin
    "First Affiliated Hospital of Harbin Medical University": None,  # Harbin Medical Univ not 双一流
    # Jilin
    "First Hospital of Jilin University": "吉林大学",
    "Second Hospital of Jilin University": "吉林大学",
    # Xian
    "First Affiliated Hospital of Xi'an Jiaotong University": "西安交通大学",
    "Second Affiliated Hospital of Xi'an Jiaotong University": "西安交通大学",
    # Chongqing
    "First Affiliated Hospital of Chongqing Medical University": None,
    # Tianjin
    "Tianjin Medical University General Hospital": "天津医科大学",
    "Tianjin Medical University Cancer Institute and Hospital": "天津医科大学",
    # Xuzhou / China Univ Mining
    "Affiliated Hospital of Xuzhou Medical University": None,
    # Southern Medical (formerly First Military Medical) - not 双一流
    "Nanfang Hospital, Southern Medical University": None,
    # Air Force / Navy
    "Tangdu Hospital, Air Force Medical University": "空军军医大学",
    "Xijing Hospital, Air Force Medical University": "空军军医大学",
    "Changhai Hospital, Naval Medical University": "海军军医大学",
    "Changzheng Hospital, Naval Medical University": "海军军医大学",
    # Southeast
    "Zhongda Hospital, Southeast University": "东南大学",
    # Soochow
    "First Affiliated Hospital of Soochow University": "苏州大学",
    # Xiamen
    "First Affiliated Hospital of Xiamen University": "厦门大学",
    # Zhengzhou
    "First Affiliated Hospital of Zhengzhou University": "郑州大学",
    "Second Affiliated Hospital of Zhengzhou University": "郑州大学",
    "Third Affiliated Hospital of Zhengzhou University": "郑州大学",
    # Nanchang
    "First Affiliated Hospital of Nanchang University": "南昌大学",
    # China Agricultural
    "China Agricultural University": "中国农业大学",
    # CAS institutes -> no school (excluded from 双一流 count)
    "Chinese Academy of Sciences": None,
}

def load_schools():
    schools = {}
    m = json.load(open(MAPF, encoding="utf-8"))
    for name, v in m.items():
        cands = v.get("candidates", [])
        if cands:
            schools[name] = cands[0]["id"]
    return schools

def main():
    id2school = {}
    for name, oid in load_schools().items():
        id2school[oid] = name

    works = [json.loads(l) for l in open(WORKS, encoding="utf-8")]
    print(f"total works with CN participation: {len(works)}")

    # Build counts
    calA = collections.Counter()  # strict: first author first-listed inst
    calB = collections.Counter()  # first author all insts
    calC = collections.Counter()  # first + corr union
    per_year = collections.defaultdict(collections.Counter)  # calC per year
    per_journal = collections.defaultdict(collections.Counter)
    zero_evidence = {}  # school -> list of works (for appendix)

    def resolve(inst_name, inst_id):
        """Map an institution to a 双一流 school name or None."""
        if inst_id in id2school:
            return id2school[inst_id]
        # try fuzzy hospital match
        if inst_name:
            for hname, parent in HOSPITAL_PARENT.items():
                if hname.lower() in (inst_name or "").lower() or (inst_name or "").lower() in hname.lower():
                    return parent
        return None

    for w in works:
        year = w.get("pub", "")[:4]
        journal = w.get("journal", "?")
        first_insts = w.get("first_insts") or []  # list of (id, name)
        corr_ids = set(w.get("corr_inst_ids") or [])

        schools_A = set()
        schools_B = set()
        schools_C = set()

        # Caliber A: first listed first-author inst
        if first_insts:
            iid, iname = first_insts[0]
            s = resolve(iname, iid)
            if s:
                schools_A.add(s)

        # Caliber B: all first-author insts
        for iid, iname in first_insts:
            s = resolve(iname, iid)
            if s:
                schools_B.add(s)

        # Caliber C: first + corr
        schools_C = set(schools_B)
        # corr insts: we only have IDs, need names; approximate via id2school direct
        for cid in corr_ids:
            if cid in id2school:
                schools_C.add(id2school[cid])
            else:
                # try to find name in first_insts
                for iid, iname in first_insts:
                    if iid == cid:
                        s = resolve(iname, iid)
                        if s:
                            schools_C.add(s)

        for s in schools_A:
            calA[s] += 1
        for s in schools_B:
            calB[s] += 1
        for s in schools_C:
            calC[s] += 1
            per_year[s][year] += 1
            per_journal[s][journal] += 1

    # Build full 147-school table
    all_schools = list(load_schools().keys())
    rows = []
    for s in all_schools:
        rows.append({
            "school": s,
            "calA_strict": calA.get(s, 0),
            "calB_firstall": calB.get(s, 0),
            "calC_firstcorr": calC.get(s, 0),
            "by_year": dict(per_year.get(s, {})),
            "by_journal": dict(per_journal.get(s, {})),
        })
    rows.sort(key=lambda r: -r["calC_firstcorr"])

    zero = [r["school"] for r in rows if r["calC_firstcorr"] == 0]
    nonzero = [r for r in rows if r["calC_firstcorr"] > 0]

    # Save
    json.dump({
        "total_works": len(works),
        "rows": rows,
        "zero_schools": zero,
        "nonzero_count": len(nonzero),
        "zero_count": len(zero),
    }, open(f"{OUTDIR}/cns_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # Print summary
    print(f"\n=== {len(nonzero)} 双一流有CNS第一单位论文, {len(zero)} 所零发表 ===\n")
    print(f"{'学校':<20} {'严格A':>6} {'一作全B':>8} {'一作+通讯C':>10}")
    for r in rows[:50]:
        print(f"{r['school']:<20} {r['calA_strict']:>6} {r['calB_firstall']:>8} {r['calC_firstcorr']:>10}")
    print(f"\n--- 零发表双一流 ({len(zero)} 所) ---")
    for s in zero:
        print(" ", s)

if __name__ == "__main__":
    main()
