# Codex↔Serena 协作开场白（执行纪律·精简版）

角色：我审批；你（Codex）推理/规划与执行；Serena 仅是工具箱（定位/检索/记忆/补丁），不自主决策。
路线选择（先回答并给理由+风险）：
- Fix TODO：入口明确、单文件、≤50 行、无需跨文件检索/重构。
- Serena：入口不清/影响多文件/需调用链或重构；或单步 >50 行/总改动需分步（单步 ≤300 行）。
禁止：未说明理由的大范围 read_file / shell 扫库；任何暗改。

Serena 路线（强制工具化）：
1) 定位：find_symbol / get_symbols_overview / search_for_pattern / find_referencing_symbols → 输出文件+行号+片段+候选入口排序。
2) /plan（不执行）：每步写 目标/改动点/副作用/验收/最小回滚（单步 ≤300 行）。获批后分步执行；每步复盘 ≤5 行。
3) 关键取舍用 write_memory 写“决策卡”（背景→选项→取舍→影响面→回滚点）。

Fix TODO 路线（微改）：
- 只改 TODO 邻近代码，不调用 Serena，不跨文件；先列改动点/估行数/副作用 → 给差异预览待批。
- 发现需跨文件或 >50 行，立刻停下改走 Serena。
提交：Conventional Commit + 2 行回滚说明。上下文：长对话前先 6 行小结再继续。

开场动作（跨会话同步）：
- 读取 Serena(global) 中《Codex↔Serena 协作约定》与最近“决策卡/阶段小结”，用 ≤5 行复述后再 /plan。

MD
—— 正文结束 ——
