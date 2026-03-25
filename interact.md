# interact.md

## 目的
`interact.md` 用于记录**用户可见的接口契约**，避免“入口/输出/默认行为”发生变更却没有同步说明，导致使用方（人或脚本）误用。

当发生以下任一变更时，必须同步更新本文件：
- 任何 CLI 入口脚本的参数（新增/删除/改名/默认值变化）
- 关键输出文件/目录的路径、文件名、字段含义、时间索引约定（UTC/本地时区）变化
- 重要错误提示、退出码、排序稳定性变化

## 稳定入口（面向用户/脚本）
> 说明：这里列的是“会被人直接运行/被脚本依赖”的入口。模块内部函数不在此处承诺稳定。

- `run_tests.sh`：测试入口，支持 `quick` / `all` 两个 stage，失败应返回非 0 退出码。
  - 约定：环境可用性探测使用 `pytest/numpy/pandas` 导入检查，超时阈值为 15 秒。
  - 约定：当环境不可用时，错误提示固定引导执行 `bash tools/run_trading.sh`（`uv`）；不再建议使用 `pip install`。
- `process_json_files.py`：`process_json_files(...)` 默认仍返回统计字典；当显式传 `return_data=True` 时返回 `(stats, final_dict)`，用于下游复用聚合内存数据；可选传 `config_data` 复用已加载配置，避免重复读盘；日期连续性检查支持 `check_dates_from_data(data=...)`（兼容包装 `check_dates(data_path, data=None)` 仍可用）；批次执行异常与单文件读取/解析异常采用 Fail Fast，发生异常时不会继续写出聚合文件。
- `check_test_intergret.py`：完整性检查采用“单次聚合 + 内存校验”链路，避免重复读取聚合大文件；`processed_errors.json` 与 `check_dates` 语义保持不变。
- `benchmark/*.py`：手工 benchmark 工具入口（**非默认门禁**，不会被 `run_tests.sh` 自动执行）。
  - 约定：benchmark 工具产物统一写入 `benchmark/_out/`，不再写入 `benchmark/` 根目录或仓库其他业务目录。
  - 治理约定（流程项）：涉及 `benchmark/rust_backtest` 源码改动时，发布前需按 `TESTING.md` 执行 Rust 扩展重装与验证流程，避免“源码已变但运行旧扩展”。
  - 约定：`benchmark/compare_backtest_loop.py` 的 baseline 与 old-loop 对比路径固定使用 `engine="python"`，避免结果受本机是否安装 `rust_backtest` 扩展影响。
- `scripts/bench_backtest_mav_numba.py` / `tools/benchmark_backtest_fastpath.py`：手工性能对比工具入口（**非默认门禁**）。
  - 约定：仅用于本地性能与一致性分析，不改变生产交易主流程。
  - 约定：一致性 compare 在遇到 non-finite 时会打印首个异常列/索引，并将 `max_abs_diff` 记为 `inf`。
- `DIY_Volume_numpy.py`：对外门面模块；支持 `import DIY_Volume_numpy as DVN` / `from DIY_Volume_numpy import X` / `from DIY_Volume_numpy import *`。
  - contract tests 固化的是强公开 API 子集（`EXPECTED_PUBLIC_API`）及其签名；`from DIY_Volume_numpy import *` 的导出以该子集为准（通过 `__all__` 控制）。
  - 约定：门面模块采用惰性加载；仅执行 `import DIY_Volume_numpy` 时不应隐式导入 optuna/pandas/numba/matplotlib 等重依赖（需要相应符号/功能时才加载）。
  - 约定：`main` / `rsi_main` / `wrsi_main` / `macd_main` / `mav_main` 的 `startcash` 与 `com` 必须被透传到策略执行层，且绩效统计使用同一 `startcash`（禁止硬编码覆盖）。
  - 约定：当 `printlog=False` 时，门面入口会将 stdout 重定向到 `os.devnull`，下游策略/绩效内部 `print` 也应被静默；当 `printlog=True` 时保持原输出行为。
  - 约定：`main` 的 `buy_atr_sma_period` 与 `sell_atr_sma_period` 必须成对提供或同时为 `None`；若仅提供其中一个参数，函数应 Fail Fast 并抛出 `ValueError`。
  - 约定：VWAP 入场语义改为“共享 `vwap/atr/atr_sma/avg_volume` + `band_k * atr` 通道 + 共享 volume gate”；对外仍保留 `buy_* / sell_*` 命名以兼容历史调用，但对应的 `*_vwap_period`、`*_atr_period`、`*_atr_sma_period`、`*_volume_window`、`*_volume_multiplier` 必须两侧相等，否则必须 Fail Fast。
  - 约定：`main` / `calculate_VWAPsignals` / `VWAPStrategy` 的 `band_k` 继续保留关键字参数默认值 `0.0`，仅用于维持既有 Python 调用 ABI；这不代表直接消费 VWAP 参数字典的链路也可以省略该字段。
  - 约定：VWAP 的 dict payload 边界（rolling/live/apply/process_opt/warm-start 直接消费路径）统一要求当前 schema 完整存在：`band_k`、`buy_atr_sma_period`、`sell_atr_sma_period` 必须显式提供且不得为 `None`，共享参数组必须两侧齐全、相等且不得为 `None`；旧 VWAP payload 不再自动补齐/投影，发现后必须在入口处 Fail Fast。
  - 约定：实盘 VWAP 只允许窗口头部保留 warmup 值；若最新决策区间或最新消费点的共享 `vwap/atr/atr_sma/avg_volume` 出现非有限值、负值或 `atr_sma<=0`，必须以 `[LIVE_GUARD]` 前缀 Fail Fast；当 shared 列与 legacy mirror 列同时存在时，两套表示也必须保持一致。
  - 约定：`optimize_and_run` 的 VWAP warm-start 仅接受当前 compact study schema；runner 会在 enqueue/best_params 边界将 compact 参数确定性展开为完整 runtime payload。若检测到旧版 shared runtime 键，必须直接 Fail Fast，不得静默跳过或退回兼容投影。
  - 约定：`evaluate_opt_results` 在处理 VWAP 策略参数时会执行必需参数校验；若缺失参数，必须在入口处 Fail Fast 抛出 `ValueError`（错误消息以 `缺少<策略名>必需参数:` 开头），而不是继续执行到更深层报错。
  - 约定：`create_storage` 的存储选择顺序为 `OPTUNA_STORAGE_URL`（优先）→ `OPTUNA_DB_DIR` → 源码仓库模式下 `repo_root/optuna_db` → `cwd/optuna_db` → 系统临时目录；当候选目录不可写时会自动回退并输出提示。
  - 约定：`optimize_and_run` 的 `num_evals` 表示每个 target 的 study 希望**累计运行**的 trial 总数（最少 3）；若 study 已达到该数量，本次调用不应再追加 trial（支持安全续跑/重启）。
  - 约定：`optimize_and_run` 若在当前 study 中得不到任何 `TrialState.COMPLETE`（例如 VWAP trial 全部因 `SignalConflictError` 被 prune），必须 Fail Fast 抛出 `RuntimeError`；不得返回 `best_value=nan` 或复用 pruned trial 的参数冒充优化结果。
  - 约定：回测时间区间统一使用半开区间 `[start_date, end_date)`；时间语义按 UTC 解释，但实现侧统一使用 **UTC naive**（无 tzinfo）的 `%Y-%m-%d %H:%M:%S` 时间字符串进行索引/比较。若传入 tz-aware 时间戳/字符串，会先转换到 UTC 再去除 tzinfo（否则 Fail Fast）。其中 `start_date` 包含，`end_date` 为右开边界不包含；signals/strategies/performance 需保持一致，滚动窗口可安全拼接（下一段 `start_date == 上一段 end_date` 无重叠）。
  - 约定：`calculate_performance` 若 `[start_date, end_date)` 内无任何数据点，必须 Fail Fast 抛出 `ValueError`（错误消息包含 `绩效窗口无数据`），而不是触发 `IndexError` 等隐式异常。
- `allocate_optimized.sh`：周日批跑入口（target 内层并行）。
  - 约定：脚本启动后会切换到自身所在目录执行，`shell_errors.txt`、`errors.txt`、`output.txt`、`optuna_db_backups/`、`backups/` 等产物均相对脚本目录落盘。
  - 约定：默认使用同目录 `./.venv/bin/python`，若虚拟环境缺失必须 Fail Fast，并提示执行 `bash tools/run_trading.sh`。
  - 约定：默认从同目录 `config.yaml` 读取 `target_names`、`opt_periods`、`strategy_names` 作为批跑集合；缺字段、非 list 或空 list 时必须 Fail Fast。
  - 约定：若未显式设置环境变量，默认日期范围为 `ALLOC_START_SUNDAY=2025-08-24`、`ALLOC_END_SUNDAY=2026-03-08`。
  - 约定：日期范围由 `ALLOC_START_SUNDAY` / `ALLOC_END_SUNDAY` 控制，脚本会自动生成并校验范围内所有周日日期。
  - 约定：默认会先同步执行 `trading_data_pipeline.py`，数据更新成功后才提交 `rolling.py` 任务；如需跳过该阶段，可显式设置 `ALLOC_RUN_DATA_PIPELINE=0`。
  - 约定：并发与节奏支持环境变量覆盖：`ALLOC_HALF_EVALS`、`ALLOC_CPU_CORES`、`ALLOC_LAUNCH_DELAY_SECONDS`、`ALLOC_POST_DATE_SLEEP_SECONDS`；其中 `ALLOC_HALF_EVALS` 与 `ALLOC_CPU_CORES` 必须为正整数，脚本内部会将 `max_jobs` 下限钉为 1，避免单核场景卡死。
  - 约定：并发槽位只统计当前 `allocate_optimized.sh` 实例自己启动且仍存活的 `rolling.py` 子进程；无关终端、其他目录或手工调试会话中的同名进程不得占用本实例槽位。
  - 约定：任一 `rolling.py` 子进程返回非 0 时，脚本必须回收该退出码、停止继续提交新的 `rolling.py` 任务，并整体以非 0 退出；不得继续打印“所有任务已完成！”伪装整批成功。
  - 约定：当使用 PostgreSQL storage 时，脚本默认收敛为 `OPTUNA_POOL_SIZE=1`、`OPTUNA_MAX_OVERFLOW=0`，并将 `max_jobs` 上限压到 8，优先避免打满数据库连接槽。
  - 约定：`ALLOC_VALIDATE_ONLY=1` 时仅打印解析后的配置与日期并退出成功，不执行备份或提交任何 `rolling.py` 任务。
- `rolling.py`：滚动训练/评估 CLI 入口；参数与输出文件约定如有变化需同步更新。
- `process_opt_for_model.py`：历史优化 JSON 提取与平滑入口（输出 `apply_data.json`、`apply_data.json_para`、`opt_data.json`）。
  - 约定：提取阶段默认按 `apply_period='7'` 生成 apply 数据键，不再依赖无效分支（如固定 `apply_period=='3'`）。
  - 约定：默认不再写出 `apply_data.json_data` 快照文件；该文件不属于稳定默认产物。
  - 约定：`extract_opt_data` / `extract_apply_data` 缺失组合默认“容错继续并汇总统计”；主入口会在提取统计存在缺失记录时于平滑前 Fail Fast，且不会发布本次产物文件。
  - 约定：提取/平滑链路对 VWAP payload 只接受当前 schema；旧 VWAP 结果若缺失 `band_k` 或共享参数不一致，必须在提取/平滑入口直接失败，不再自动修补成新产物。
  - 约定：平滑阶段对 `apply_data.json_para` 采用“单次建索引 + 窗口查询”路径，避免每次查询重复全量排序/扫描；当前仅支持单一 `source_apply_period`，多值时必须 Fail Fast。
  - 约定：发布阶段采用“正式目录旁 staged + per-file replace”，避免跨文件系统 `os.replace` 失败；不承诺三文件整组原子切换。
- `CoT/cot_data_pipline.py`：CoT 数据流水线入口（模板渲染 / 回测结果加工 / RL 策略回放）。
  - 约定：消费 `apply_data.json_para` 时，旧请求键 `..._apply_3` 不再被视为固定 source period；实现必须从当期 payload 解析真实 raw apply key（如 `..._apply_7`），并在存在多个 raw 候选时 Fail Fast。
- `trading_data_pipeline.py`：数据更新流水线入口；输出落盘位置/增量更新策略变化需同步更新。
  - 约定：落盘的 K 线只包含已收盘 bar（`endTime` 对齐到“当前 bar 开盘时间 - 1ms”），避免尾部数据随运行时刻变化导致回测不可复现。
  - 约定：去重仅基于时间戳（DatetimeIndex），禁止按 OHLCV 数值去重（不同时间出现相同 OHLCV 属于正常情况）。
  - 约定：遇到数据获取失败、仍存在缺口/重复时间戳/格式异常（例如秒数不为 0）时必须 Fail Fast，并返回非 0 退出码。
- `apply_selected_para.py`：生成/应用“选中策略参数”的入口；输出文件名与策略命名规则变化需同步更新。
- `rolling_select_strategy_model.py`：策略选择模型入口（研究/回放）。
  - 约定：`apply_backtest` 统一走 strict 主循环 + `finalize_backtest`，并采用右开区间 `[start_idx, end_idx)` 语义；`StopTrain=True` 时禁止开仓信号，仅维护净值与持仓一致性。
  - 约定：不再输出 `final_hedge_logic_output.csv`（strict 合同下禁用 `HedgeLogic`）。
  - 约定：`apply_json` 中 raw key `..._apply_<source_period>` 统一视为未平滑参数并映射到 `alpha_nan`；仅 `..._apply_alpha_<alpha>` 参与具体 alpha one-hot 编码。
- `future_trading/future_strategy.py` / `trading_box/margin_tradeBot.py`：实盘执行链路。
  - 约定：退出阶段（MACD `close_signal`、止损、止盈）一旦在本轮发出 `close` 请求，本轮必须立即结束；不得继续基于旧仓位快照评估反手、加仓或空仓开仓。成交确认由下一轮仓位刷新处理。
  - 约定：MACD live 分支必须按当前指标/信号函数契约调用，`calculate_MACDindicators_by_date` 需显式传入完整 MACD 参数，`DVN.calculate_MACDsignals` 必须使用 `arrays=`；不得沿用旧 `df=` 调用。
  - 约定：实盘尺寸适配层 `LiveTradeLogic` 必须接受 `MACDStrategy`，不得在 live 路径构造阶段因策略名白名单缺失而提前报错。
  - 约定：`trading_box/margin_tradeBot.py` 追加 `marginTrade_data*.csv` 时，若目标文件不存在或为空，必须先写入 `Price,Position,cash,Net_Value,Timestamp,Max_profit` 表头；该约束在冷启动首轮即命中 MACD `close_signal` 快路径时也必须成立。
  - 约定：`future_trading/future_strategy.py` 必须继续兼容现有“直接执行脚本文件”入口；`python future_strategy.py --help` 与 `future_main.sh` 的脚本模式启动不得因 repo-root 导入不可见而在参数解析前退出。
  - 约定：`trading_box/margin_tradeBot.py` 必须继续兼容现有“直接执行脚本文件”入口；`python margin_tradeBot.py --help` 与 `run_margin_tradebot.sh` 的脚本模式启动不得因包内相对导入失败而在参数解析前退出。

## 关键配置（面向用户）
- `config.yaml`：主配置；新增/删除字段、字段语义变化需同步更新注释与本文件说明。
- `config.json`：旧版/兼容配置；兼容性策略变化需同步更新。
- `trading_box/config.ini`：**本地私有**交易配置（API Key/Secret 等），禁止提交真实密钥到版本库；仓库内如需示例请使用模板文件。

## 关键产物（被下游依赖）
- `dict_rolling/`：滚动训练/样本外结果落盘目录；目录结构与文件命名规则变化需同步更新。
  - 语义版本约定：每个目标节点必须包含 `__meta__.backtest_semantic_version`（当前固定为 `exit_first_v2`），用于标识“退出优先”语义。
  - 聚合约定：`process_json_files.py` 会拒绝缺少该元数据或版本不匹配的文件，避免旧/新回测语义混合进入下游建模数据。
  - 聚合输出约定：`process_json_files.py` 输出中每个策略 entry 仅包含 `opt` 与 `apply` 两个 key；语义版本仅用于过滤输入文件，不会被写入到每个策略 entry。
- `processed_errors.json`：`check_test_intergret.py` 的输出文件；字段结构变化需同步更新。
- 回测输出 `numpy arrays`（严格合同，用户可见 breaking change）：
  - `open_direction` 已撤销：不得作为输入/输出字段出现。
  - `close_signal: bool[1d]` 为必需字段（仅 MACD 生效；非 MACD 策略必须忽略其 True 值）。
  - `buy_signal/sell_signal/close_signal` 必须为 `bool`；核心状态列必须为 `float64`，且要求一维/长度一致/C-contiguous。
  - `buy_signal` 与 `sell_signal` 同 bar 同时为 `True` 时，必须 Fail Fast 抛出 `SignalConflictError`（消息仍以 `signal_conflict at i=...` 开头），不得继续复用裸 `ValueError`。
  - strict 下输入数组底层内存不得重叠：任意可写状态列与任意其他输入列（含只读列）若共享内存，必须在入口处 Fail Fast 抛出 `memory_overlap_forbidden`。
  - `end_idx` 对应 bar 必须有可用的 `next_open`（通常要求 `end_idx < N-1`，或上游数据多包含 1 根 bar）。
  - `BTC_debt` 与 `USDT_debt` 在同一 bar 不得同时 `> 0`；若出现必须 Fail Fast 抛出 `invalid_debt_state`。
  - `position` 与债务方向必须一致：`position>0 => USDT_debt>0 且 BTC_debt==0`，`position<0 => BTC_debt>0 且 USDT_debt==0`，`position==0 => BTC_debt==USDT_debt==0`；违反时必须 Fail Fast 抛出 `invalid_position_debt_state`。
  - `open_cost_price` 平仓当根 bar 必须写入 `0.0`；持仓时必须 `> 0` 且 finite。
  - `com` 固定为 `0.0005`；`hedge_function` 在 strict 中禁用（必须为 False）。
  - `HedgeLogic` 在 strict 合同下已废弃；任何直接实例化都必须 Fail Fast 抛出 `ValueError("HedgeLogic is deprecated under strict contract")`。
  - 回测主循环入口统一使用 `numpy_backtest.optimized_backtest_loop(engine=auto|python|rust)`：auto 优先 Rust（`rust_backtest.backtest_loop`），不可用则回退 Python；生产禁止绕过该入口直接调用 Rust，以确保 dict-level 护栏（如 `open_direction` 禁止）在进入 Rust 前已 Fail Fast。
