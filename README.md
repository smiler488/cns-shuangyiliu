# cns-shuangyiliu

English | [中文](README.zh-CN.md)

Counts of Cell, Nature and Science research articles per university for China's 147 "Double First-Class" (双一流) universities, from 14 February 2022 to 3 November 2026. The repository has the raw OpenAlex records, the institution mapping, the scripts and the results, so every number can be recomputed or recounted with a different rule.

Of 3,166 CNS articles with at least one Chinese institution in this window, 120 of the 147 universities have at least one paper as first unit and 27 have none. I wrote this up in a WeChat article (《双一流CNS发文统计：120所发文、27所挂零》, account @smiler488) and put the data here so that readers can check it.

## Ask an AI assistant

Paste this into an assistant that can read web pages:

```text
Please follow https://raw.githubusercontent.com/smiler488/cns-shuangyiliu/main/install.md and use the cns-shuangyiliu data to answer my question.
```

## Contents

| Path | What it is |
|---|---|
| `data/works_cns.jsonl` | one line per article: DOI, title, date, journal, first-author institutions, corresponding-author institution IDs |
| `data/school_openalex_map.json` | the 147 universities and their OpenAlex institution candidates |
| `data/shuangyiliu_147.txt` | list of the 147 universities (Ministry of Education, 2022) |
| `data/cns_result.json` | counts per university under three rules, by year and journal, plus the zero list |
| `scripts/map_institutions.py` | builds the institution mapping |
| `scripts/fetch_cns.py` | downloads the articles from OpenAlex |
| `scripts/analyze_cns.py` | counts and writes `cns_result.json` |

## Counting rules

- **C, first author + corresponding author** (main table): a university counts a paper if it appears among the first author's institutions or the corresponding authors' institutions. Chinese ranking reports usually use this rule.
- **A, strict**: only the first author's first-listed institution.
- **B, first author, all institutions**: any institution of the first author.

Rankings differ between rules. The University of Chinese Academy of Sciences, for example, has 365 papers under C but 2 under A, because its authors usually list a CAS institute first. Always say which rule a number comes from.

Affiliated hospitals are counted for their parent university (`HOSPITAL_PARENT` in `analyze_cns.py`). CAS institutes are not counted for any university.

## Reproduce

```bash
pip install -r requirements.txt
python scripts/analyze_cns.py            # recount from data/ (no network)
python scripts/map_institutions.py       # optional: rebuild the mapping
python scripts/fetch_cns.py              # optional: download again (set OPENALEX_EMAIL)
```

`analyze_cns.py` reproduces the published `cns_result.json` byte for byte.

## Known caveat: the Center for Life Sciences

OpenAlex has an institution called "Center for Life Sciences", the joint centre of Peking University and Tsinghua University. The name matching assigns it to Tsinghua, and the published numbers include that. The centre is shared, so the choice matters:

| `--cls` | Tsinghua A / C | Peking University A / C |
|---|---|---|
| `tsinghua` (published) | 98 / 293 | 150 / 251 |
| `none` | 55 / 259 | 150 / 251 |
| `both` | 98 / 293 | 193 / 296 |

Run `python scripts/analyze_cns.py --cls none --out other.json` to get the alternative counts. No other university changes.

## Other limits

- OpenAlex affiliation parsing is not perfect. Missing or wrong affiliations go straight into the counts.
- For corresponding authors, the 2026 data file stores only institution IDs. A hospital that is not in the ID map is therefore missed on the corresponding-author side. New downloads store names as well.
- Paper counts say nothing about the quality of a discipline. Please do not use them that way.

Cross-check: the top 20 under rule C agree with the 2024 Gaoji yearbook and the 2026 Qingta report.

## Sources

- [OpenAlex](https://openalex.org) (CC0)
- Ministry of Education list of the second round of Double First-Class universities (教研函〔2022〕1号)

## Citation

See [`CITATION.cff`](CITATION.cff). Please quote the counting rule and the time window with any number.

## License

Code and derived data: MIT, see [LICENSE](LICENSE). OpenAlex records are CC0. Liangchao Deng (邓良超).
