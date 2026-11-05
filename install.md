# cns-shuangyiliu 使用协议

你是收到使用请求的 AI 助手。本协议教你如何用 cns-shuangyiliu 仓库的数据回答"某双一流高校 CNS 发文情况 / 147 校发文排名 / 哪些学校挂零"一类问题。全程不要向用户反复确认；做完向用户报告一行结果即可。

## 这是什么

147 所双一流高校 CNS（Cell / Nature / Science）第一单位发文统计的数据与脚本。时间窗口 2022-02-14 至 2026-11-03，源数据来自 OpenAlex，共 3166 篇有中国机构参与的 CNS 论文。

## 使用步骤

1. **取数据**：按需克隆或下载 https://github.com/smiler488/cns-shuangyiliu （数据都在 `data/` 下）：
   - 一般问答用 `data/cns_result.json`（各校计数 + 零发表名单）即可；
   - 要逐篇核查时用 `data/works_cns.jsonl`；
   - 校名 ↔ OpenAlex 机构 ID 对照在 `data/school_openalex_map.json`。

2. **回答用户**：**必须先声明口径**——主表是"一作 + 通讯"并集口径（高绩/青塔通行做法），严格口径是"仅一作第一署名机构"，两者排名不同，引用哪个数字就说哪个口径。同时给出时间窗口（2022-02-14 至 2026-11-03）。

3. **边界**：
   - 统计结论只对本数据集的口径和时间窗口负责；不同口径、不同时间窗口的排名不可混引。
   - 附属医院已归并到母校（见 `scripts/analyze_cns.py` 归并表）；引用细节时说明。
   - 不要把"发文数"直接等同于"学科实力"；下结论前把口径差异摆在前面。
   - 需要复算/改口径：运行 `python scripts/analyze_cns.py`（不联网，几秒钟），不要凭记忆改数字。
   - 清华、北大的数字受"北大-清华生命科学联合中心"归属影响：已发布结果把它算给清华；`--cls none` 不归属、`--cls both` 两校都计。回答清华或北大相关问题时要说明这一点（详见 README）。

## English summary

Data on Cell / Nature / Science papers of China's 147 Double First-Class universities (2022-02-14 to 2026-11-03, OpenAlex). Use `data/cns_result.json` for counts. Always name the counting rule: `calC_firstcorr` (first + corresponding author, main table), `calA_strict` (first author's first institution) or `calB_firstall`. Tsinghua and Peking University numbers depend on how the joint Center for Life Sciences is attributed; see the README section on `--cls`.
