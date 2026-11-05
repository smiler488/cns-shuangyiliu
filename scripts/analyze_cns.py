# -*- coding: utf-8 -*-
"""Count CNS papers per Double First-Class university and list the zero-paper schools.

Calibers
  A (strict):     first author's first-listed institution
  B (first-all):  all institutions of the first author
  C (first+corr): union of B and the corresponding authors' institutions

Institutions are matched to schools by OpenAlex ID first, then by name
against HOSPITAL_PARENT (affiliated hospitals are counted for their parent
university).

--cls decides who gets the OpenAlex institution "Center for Life Sciences"
(the Peking University-Tsinghua University joint centre):
  tsinghua  Tsinghua only (default; this is what the published numbers use)
  none      nobody
  both      Peking University and Tsinghua University
With --cls none, Tsinghua drops from 98 to 55 (A) and from 293 to 259 (C);
Peking University is unchanged.

Usage:  python scripts/analyze_cns.py [--cls tsinghua|none|both] [--out FILE]

Liangchao Deng (邓良超), MIT License
"""
import argparse
import collections
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
WORKS = DATA / "works_cns.jsonl"
MAPF = DATA / "school_openalex_map.json"
OUTDIR = DATA

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

CLS_NAME = "Center for Life Sciences"
CLS_POLICY = {
    "tsinghua": {"清华大学"},
    "none": set(),
    "both": {"清华大学", "北京大学"},
}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--cls", choices=sorted(CLS_POLICY), default="tsinghua",
                    help="attribution of the PKU-Tsinghua Center for Life Sciences (default: tsinghua)")
    ap.add_argument("--out", default=str(OUTDIR / "cns_result.json"), help="result JSON")
    args = ap.parse_args(argv)
    cls_schools = CLS_POLICY[args.cls]

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

    def resolve(inst_name, inst_id):
        """Set of 双一流 schools an institution counts for (usually 0 or 1)."""
        if inst_id in id2school:
            return {id2school[inst_id]}
        if inst_name == CLS_NAME:
            return set(cls_schools)
        if inst_name:
            # Name match in both directions: OpenAlex often lists a hospital
            # without its university ("Huashan Hospital"), so a short name
            # contained in a curated key also counts.
            low = inst_name.lower()
            for hname, parent in HOSPITAL_PARENT.items():
                if hname.lower() in low or low in hname.lower():
                    return {parent} if parent else set()
        return set()

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
            schools_A |= resolve(iname, iid)

        # Caliber B: all first-author insts
        for iid, iname in first_insts:
            schools_B |= resolve(iname, iid)

        # Caliber C: first + corr
        schools_C = set(schools_B)
        # Corresponding-author institutions: older data files store IDs only,
        # so a name is looked up in corr_insts (newer fetches) or first_insts.
        names = {iid: iname for iid, iname in (w.get("corr_insts") or []) + first_insts}
        for cid in corr_ids:
            if cid in id2school:
                schools_C.add(id2school[cid])
            elif cid in names:
                schools_C |= resolve(names[cid], cid)

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
    }, open(args.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"saved {args.out} (--cls {args.cls})")

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
