# cns-shuangyiliu

[English](README.md) | 中文

[![CI](https://github.com/smiler488/cns-shuangyiliu/actions/workflows/test.yml/badge.svg)](https://github.com/smiler488/cns-shuangyiliu/actions/workflows/test.yml) [![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) ![Python 3.8+](https://img.shields.io/badge/Python_3.8%2B-informational)
统计 147 所"双一流"高校在 2022-02-14 至 2026-11-03 期间以第一单位发表的 Cell / Nature / Science（CNS）研究论文。仓库里有 OpenAlex 原始记录、机构映射、脚本和统计结果，每个数字都能复算，也能换一种口径重新统计。

在这个时间窗口内，有中国机构参与的 CNS 论文共 3166 篇。147 所双一流高校里，120 所至少有一篇第一单位论文，27 所为零。相关分析写在公众号文章《双一流CNS发文统计：120所发文、27所挂零》（@smiler488）里，数据放在这里供读者核对。

## 交给 AI 助手

把下面这句话发给能读网页的 AI 助手：

```text
请根据 https://raw.githubusercontent.com/smiler488/cns-shuangyiliu/main/install.md，使用 cns-shuangyiliu 的统计数据回答问题。
```

## 目录

| 路径 | 内容 |
|---|---|
| `data/works_cns.jsonl` | 每行一篇论文：DOI、标题、日期、期刊、一作机构、通讯作者机构 ID |
| `data/school_openalex_map.json` | 147 所高校及其在 OpenAlex 中的候选机构 |
| `data/shuangyiliu_147.txt` | 147 所高校名单（教育部 2022 年公布） |
| `data/cns_result.json` | 三种口径下各校发文数、分年份和分期刊的计数，以及零发表名单 |
| `scripts/map_institutions.py` | 生成机构映射 |
| `scripts/fetch_cns.py` | 从 OpenAlex 抓取论文 |
| `scripts/analyze_cns.py` | 统计并写出 `cns_result.json` |

## 口径

- **C：一作 + 通讯**（主表）：学校出现在第一作者或通讯作者的任一署名机构中，就记一篇。国内排名报告通常用这个口径。
- **A：严格口径**：只看第一作者的第一署名机构。
- **B：一作全口径**：第一作者的全部署名机构。

不同口径下的排名差别很大。比如中国科学院大学在 C 口径下有 365 篇，在 A 口径下只有 2 篇，因为国科大的作者通常把中科院某个研究所写在第一署名。引用任何数字时，请注明出自哪个口径。

附属医院归并到所属大学（见 `analyze_cns.py` 中的 `HOSPITAL_PARENT`）；中科院各研究所不计入任何高校。

## 复算

```bash
pip install -r requirements.txt
python scripts/analyze_cns.py            # 基于 data/ 重新统计（不需要联网）
python scripts/map_institutions.py       # 可选：重建机构映射
python scripts/fetch_cns.py              # 可选：重新抓取（建议设置 OPENALEX_EMAIL）
```

`analyze_cns.py` 跑出来的 `cns_result.json` 与已发布版本逐字节一致。

## 已知问题：生命科学联合中心

OpenAlex 里有一个机构叫 "Center for Life Sciences"，即北京大学–清华大学生命科学联合中心。名称匹配会把它全部归给清华，已发布的数字就是这样算的。但这个中心是两校共建的，怎么归属直接影响结果：

| `--cls` | 清华 A / C | 北大 A / C |
|---|---|---|
| `tsinghua`（已发布） | 98 / 293 | 150 / 251 |
| `none` | 55 / 259 | 150 / 251 |
| `both` | 98 / 293 | 193 / 296 |

运行 `python scripts/analyze_cns.py --cls none --out other.json` 可以得到另一种口径下的结果。其他学校的数字不受影响。

## 其他局限

- OpenAlex 的机构解析并不完美，漏标或错标的机构会直接影响计数。
- 2026 年这份数据里，通讯作者只存了机构 ID，不在映射表里的医院会在通讯作者这一侧漏计。新版抓取脚本同时保存了机构名称。
- 发文数量不能代表学科实力，请不要这样解读。

交叉验证：C 口径下的前 20 名与高绩 2024 年鉴、青塔 2026 报告一致。

## 数据来源

- [OpenAlex](https://openalex.org)（CC0）
- 教育部第二轮"双一流"建设高校及建设学科名单（教研函〔2022〕1号）

## 引用

见 [`CITATION.cff`](CITATION.cff)。引用任何数字时，请同时注明口径和时间窗口。

## 许可证

代码和衍生数据采用 MIT 许可，见 [LICENSE](LICENSE)；OpenAlex 原始记录为 CC0。邓良超（Liangchao Deng）。
