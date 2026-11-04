# cns-shuangyiliu

147 所双一流高校 CNS（Cell / Nature / Science）第一单位发文统计：数据、脚本与结果。2022-02-14 至 2026-11-03，经 OpenAlex API 抓取，共 3166 篇有中国机构参与的 CNS 论文。

配套公众号文章：《双一流CNS发文统计：120所发文、27所挂零》（微信公众号 @smiler488）。

## 一句话使用（给 AI）

把下面这句发给你在用的 AI 助手，它就知道怎么查用本仓库的数据：

```text
请根据 https://raw.githubusercontent.com/smiler488/cns-shuangyiliu/main/install.md，使用 cns-shuangyiliu 的统计数据回答问题。
```

## 目录

- `data/works_cns.jsonl` — 抓取的论文数据（slim JSONL：一作机构信息 + 通讯作者标记）
- `data/school_openalex_map.json` — 147 所双一流高校 → OpenAlex 机构 ID 映射
- `data/shuangyiliu_147.txt` — 147 所高校名单
- `data/cns_result.json` — 统计结果（各校发文计数 + 零发表名单）
- `scripts/fetch_cns.py` — 抓取（需 `OPENALEX_API_KEY` 环境变量，可选；不设则走较低礼貌池速率）
- `scripts/map_institutions.py` — 高校名 → OpenAlex 机构 ID 映射（含附属医院归并到母校）
- `scripts/analyze_cns.py` — 统计分析

## 口径

- **主表口径（一作 + 通讯）**：第一作者机构与通讯作者机构的并集（高绩/青塔通行做法）
- **严格口径**：仅第一作者的第一署名机构（另列，用于揭示"国科大计数陷阱"等口径差异）
- **一作全口径**：第一作者的全部机构

时间窗口、期刊口径、机构归并规则均可在脚本里改，重新跑一遍即可复算。

## 复现

```sh
pip install requests
python scripts/map_institutions.py   # 重建机构映射（可选，data/ 已含结果）
python scripts/fetch_cns.py          # 重新抓取（可选，data/ 已含数据）
python scripts/analyze_cns.py        # 重算统计
```

交叉验证：Top20 排名与高绩 2024 年鉴、青塔 2026 报告一致。

## 数据来源

- [OpenAlex](https://openalex.org)（论文与机构元数据，CC0）
- 教育部第二轮"双一流"建设高校及建设学科名单（教研函〔2022〕1 号）

统计结果按"数据 + 代码开源、口径可复算"原则发布；引用时请注明口径与时间窗口。

## License

MIT © smiler488
