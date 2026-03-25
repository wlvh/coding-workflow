## 文件简介
ignore文件不得列入提交
### 核心配置
- `pyproject.toml`：Python 项目元数据与工具配置（setuptools/black/isort/pytest/coverage）。
- `config.yaml`：主配置（targets/target_names/opt_periods/strategy_names/参数平滑等，带详细注释）。
- `config.json`：旧版/兼容配置（targets/opt_periods/strategy_names 等列表）。
- `path_config.py`：路径集中管理（数据/日志/CoT/交易配置/输出文件等）。
- `trading_box/config.ini`：交易机器人账号配置（包含 API Key/Secret；建议只保留模板，真实密钥仅放本地，注意安全）。
- `future_trading/strategy_lists.json`：期货实盘策略清单（策略名、参数、权重）。

### 本地/运行产物（默认 ignore，不入库）
- `future_trading/strategy_position_table.json`：期货策略持仓状态表（运行时落盘；默认 ignore）。
- `processed_errors.json`：`check_test_intergret.py` 的输出文件（默认 ignore）。
- `dict_rolling/`：滚动训练/样本外结果落盘目录（默认 ignore，通常体积较大）。
- `optuna_db/`：Optuna SQLite 存储目录（默认 ignore）。
- `benchmark/_out/`：benchmark 工具统一输出目录（默认 ignore）。
- `benchmark/rust_backtest/target/`：Rust benchmark 编译产物目录（默认 ignore）。

### 核心模块
- `trading_core/rolling_optimized.py`：高性能 rolling 计算封装（优先 numba/bottleneck，回退 pandas）。
- `trading_core/utils_numpy.py`：回测/指标/统计核心函数（回撤、RSI/MA/EMA/VWAP/ATR、交易统计等）。
- `trading_core/utils_numpy_extended.py`：扩展指标计算（RSI/MAV/MACD 按区间计算与信号生成相关）。
- `utils/io_fast.py`：基于 `orjson` 的快速 JSON 序列化写文件工具。
- `numpy_backtest.py`：Numpy 回测引擎与 strict 合同交易逻辑（`TradeLogic`、`optimized_backtest_loop`；含 `_validate_backtest_numpy_arrays_strict` strict 入参数组合同校验、`SignalConflictError` 双信号冲突护栏、HedgeLogic 废弃、`engine`=auto|python|rust 分发）。
- `DIY_Volume_numpy.py`：对外门面（VWAP/RSI/WRSI/MAV/MACD 等入口与 Optuna 编排）。
- `diy_volume_numpy/data.py`：数组初始化与日期索引定位。
- `diy_volume_numpy/errors.py`：共享异常定义（含 `SignalConflictError` 及信号冲突转换工具）。
- `diy_volume_numpy/signals/core.py`：RSI/MAV/VWAP/MACD 信号计算；VWAP 采用共享 `vwap/atr/atr_sma/avg_volume` 与 `band_k * atr` 通道语义，并保持 `calculate_VWAPsignals` 旧位置参数 ABI（`band_k` 仅作为关键字参数新增）。
- `diy_volume_numpy/strategies/core.py`：VWAP/MAV/RSIV/WRSI/MACD 策略执行。
- `diy_volume_numpy/performance.py`：绩效指标计算与回测统计。
- `diy_volume_numpy/optuna/runner.py`：Optuna 优化与存储封装；VWAP 仅搜索共享参数，warm-start/best_params 只接受当前 compact study schema，并在 runner 内部确定性展开为完整 runtime 参数；若某个 study 没有任何 `COMPLETE` trial（例如 VWAP trial 全部因信号冲突被 prune），`optimize_and_run` 必须 Fail Fast。
- `diy_volume_numpy/api.py`：main/*_main 编排与优化结果评估。
- `diy_volume_numpy/utils.py`：参数归一化、类型转换与 UTC naive 时间归一化工具。
- `benchmark/compare_backtest_loop.py`：MAV 回测循环候选实现与旧版循环的一致性/性能对比脚本（结果写入 `benchmark/_out/`）。
- `benchmark/bench_rust_vs_python.py`：Rust 回测内核与 Python 旧内核的多策略一致性/性能基准脚本。
- `benchmark/rust_backtest/Cargo.toml`：Rust benchmark crate 配置（依赖与构建目标定义）。
- `benchmark/rust_backtest/src/lib.rs`：Rust 回测循环实现与 Python 绑定导出（`rust_backtest.backtest_loop`）。
- `rolling_strategy_test.py`：滚动训练与样本外应用评估（支持前推验证结果落盘）。
- `rolling_select_strategy_model.py`：策略选择模型（基于 opt/apply 历史数据的特征化、打分与选择；`apply_backtest` 会按当前 payload 解析 raw/smoothed apply key，raw `..._apply_<source_period>` 统一视为未平滑参数，避免将 source period 误映射为 alpha 编码）。
- `apply_selected_para.py`：生成/应用“选中策略参数”（面向下周/下一期的参数应用与策略名生成）；读取 VWAP apply 产物时走严格归一化，旧版/损坏的 VWAP payload 必须直接报错，不再额外做旧产物提示或兼容修补。
- `process_json_files.py`：聚合 `dict_rolling/` JSON 结果为结构化数据；支持 `return_data=True` 返回内存聚合结果，并提供 `check_missing_keys_from_data/check_dates_from_data` 内存完整性检查与兼容包装函数；批次执行异常与单文件读取/解析异常采用 Fail Fast，`check_missing_keys_from_data` 按日期排序遍历以保证结果稳定可复现；`extract_apply_data/extract_opt_data` 支持缺失组合容错统计或 `fail_fast`，`apply_smooth_for_alldata` 使用预建索引避免重复全量扫描。
- `extract_strategies.py`：从大型嵌套 JSON 中抽取 `apply` 阶段的单值指标，生成扁平化表。
- `strategy_backtest_eval.py`：策略回测结果分析与统计检验（聚合、对比、显著性检验等）。
- `binance_data_handler.py`：Binance 现货/期货 K 线下载与增量更新（重试、速率控制、补缺、文件锁；只落盘已收盘 bar；支持 fail_fast；按时间戳去重）。
- `trading_data_process.py`：旧版数据处理函数集合（下载/补缺/去重/工具函数，部分模块仍引用）。
- `extra_info.py`：额外数据与特征工程（链上指标、BTC 特征、PCA、yfinance 数据等）。
- `future_trading/future_data_pipline.py`：期货实盘数据 CSV 读写（文件锁），索引统一为 UTC。
- `future_trading/future_framework.py`：期货实盘执行框架（下单/订单队列/SQLite/WAL/净值日志等）。
- `future_trading/future_strategy.py`：单策略实盘进程（算指标/生成信号/写入订单库/风控）；MACD live 分支必须按当前指标/信号契约显式传递完整参数，调用 `DVN.calculate_MACDsignals` 时统一使用 `arrays=`，并以带注释的 `macd_max_length` 满足当前 indicator helper 的 range guard。
- `trading_box/live_trade_logic.py`：实盘尺寸适配层（无交易所副作用导入）；集中维护 live 支持的 `strategy_name` 白名单与参数绑定，`MACDStrategy` 必须被接受。
- `trading_box/margin_tradeBot.py`：保证金实盘交易机器人（读取 best_strategy、借贷/下单/止盈止损等）；复用共享 `LiveTradeLogic`，避免 live 策略名契约在多处漂移；MACD live 分支必须按当前指标/信号契约显式传递完整参数，调用 `DVN.calculate_MACDsignals` 时统一使用 `arrays=`，并在 `trade_logic` 中保持 `close_signal` 退出优先、退出即结束本轮。
- `trading_box/send_log_to_tele.py`：Telegram 推送脚本（日志与账户状态；含 token/ChatID，注意安全）。
- `trading_box/trading_bot.py`：账户余额轮询/过滤打印脚本（ccxt）。
- `trading_box/Websocket_act_info.py`：用户数据流 WebSocket 监听（listenKey 维护/重连）。
- `trading_box/Websocket_market_info.py`：市场行情 WebSocket 监听（kline/depth，含 pong 保活）。
- `trading_box/CCXT_BT_trading_bot.py`：Backtrader + CCXT 的示例/实验性交易机器人（含 VWAP 指标示例）。
- `CoT/cot_data_pipline.py`：CoT 数据流水线（窗口特征、策略/强化学习指标、模板渲染等；消费 `apply_data.json_para` 时会按当前 payload 解析真实 raw apply key，兼容旧的 `..._apply_3` 请求）。
- `CoT/data_filling.py`：调用 LLM 生成市场总结/交易理由并回填 JSON（包含硬编码 token，慎用）。
- `CoT/llama-3.1_8b_unsloth.py`：使用 Unsloth/TRL 对 Llama 进行 SFT 训练的实验脚本。

### 工具脚本
- `allocate.sh`：批量运行 `rolling.py`（多日期/目标/周期/策略并发），输出到 `errors.txt/output.txt`（默认 ignore）。
- `allocate_optimized.sh`：`allocate.sh` 优化版（批跑前更新数据 + target 内层并行 + 支持 PostgreSQL Optuna 存储与备份参数；并发槽位仅按当前脚本实例启动的 `rolling.py` 子进程 PID 统计；PG 模式默认 `pool_size=1/max_overflow=0` 且收敛 `max_jobs<=8`）。
- `rolling.py`：CLI 入口：按参数调用 `rolling_strategy_test.rolling_strategy_test()`。
- `rolling.sh`：旧版滚动任务拆分并行脚本（两段式跑 `rolling.py`）。
- `Using_rolling_strategy.py`：CLI 入口：运行滚动策略选择（无未来数据）实验。
- `Using_rolling_strategy.sh`：批量网格搜索运行 `Using_rolling_strategy.py`（并发控制、日志汇总）。
- `trading_data_pipeline.py`：数据更新流水线入口（下载/更新/补缺/按时间戳去重；只落盘已收盘 bar；异常 Fail Fast + 额外数据更新）。
- `process_opt_for_model.py`：从历史优化结果 JSON 生成 `apply_data.json/apply_data.json_para/opt_data.json` 并做参数平滑处理（输出默认 ignore）；主流程单次加载源 JSON 并复用到 apply/opt 提取，默认提取 `apply_period='7'`，先写正式目录旁 staged 产物并在缺失统计为 0 时执行 per-file replace 发布正式文件，默认不再写 `apply_data.json_data` 快照；VWAP 产物仅接受当前 schema，旧 payload 缺失 `band_k` 或共享参数不一致时必须 Fail Fast；平滑链路当前仅支持单一 `source_apply_period`。
- `check_test_intergret.py`：处理 `dict_rolling` 并检查 opt/apply 数据完整性，单次聚合后走内存校验链路，输出 `processed_errors.json`（默认 ignore）。
- `fill_process_opt_gap.sh`：根据缺失列表补跑 `rolling.py` 以填补断档数据。
- `find_optimal_params.py`：在评估/聚合结果上搜索最佳参数组合（并生成可视化图表）。
- `fore_statue.py`：市场状态预测/特征工程与模型实验脚本（LightGBM/SVM/Optuna 等）。
- `fore_statue.sh`：批量运行 `fore_statue.py`（控制并发并记录日志）。
- `Rolling_Garch.py`：GARCH 波动率预测研究脚本（价格/成交量波动的滚动建模）。
- `future_trading/future_main.sh`：启动/重启期货实盘框架与多策略进程（写入 `logs/`；运行时创建，默认 ignore）。
- `trading_box/run_margin_tradebot.sh`：启动/重启多账号保证金机器人并轮转日志。
- `scripts/bench_backtest_mav_numba.py`：旧回测引擎与 Numba 内核在 MAV 策略下的一致性/性能基准脚本。
- `tools/benchmark_backtest_fastpath.py`：多策略（MAV/MACD/VWAP/RSIV/WRSI）旧内核与 fastpath 原型的性能对比脚本。
- `tools/run_trading.sh`：本机运行入口（检查/创建 `.venv`，可直接执行指定 Python 脚本）。
- `tools/filter_json_clean.py`：扫描 `dict_rolling/` JSON 并做快速质量分析（不写输出文件）。

### 备注
- `trading_box/test.py`：交易接口手工调试脚本（不建议在生产环境直接运行）。

## 架构说明
* source ./.venv/bin/activate 来激活虚拟环境
* 强制使用仓库的 `./.venv/bin/python` 运行测试与脚本（或先 activate）；不要直接用系统/Conda 的 `python` 跑 `pytest`，否则依赖版本可能不一致导致 import 失败（典型：SQLAlchemy 版本不匹配导致 `from sqlalchemy import Engine` 报错）。
* 推荐统一走 `./run_tests.sh quick|all`：脚本会优先挑选可用的 `./.venv/bin/python`，避免“选到半残环境”。
* 若 `.venv` 不可用/损坏：运行 `bash tools/run_trading.sh`（内部使用 `uv` 创建/重建虚拟环境并安装 `requirements.txt`）。
* 依赖安装约束：仓库依赖安装统一通过 `bash tools/run_trading.sh`（`uv`）；禁止使用 `pip install` 安装仓库依赖。
* 除非明确说明，否则所有命令均在仓库根目录执行。

## Rust 扩展新鲜度三道自动闸（必须遵循）
当改动以下任一文件时，视为“Rust 扩展变更”：
- `benchmark/rust_backtest/src/**`
- `benchmark/rust_backtest/Cargo.toml`

三道自动闸目标（长期机制）：
1. 运行时闸：Python 调用 `rust_backtest` 前校验“源码指纹 vs 已安装扩展指纹”；不一致必须 Fail Fast，并提示重装命令。
2. 测试闸：新鲜度校验测试（如 `test_rust_extension_freshness`）必须纳入门禁。
3. 提交闸：`pre-push` 在检测到 Rust 扩展变更且未通过新鲜度校验时必须阻断推送。

过渡期（在三道闸完全代码化之前）的强制执行：
- 只要出现 Rust 扩展变更，必须先执行：
  - `cd benchmark/rust_backtest && maturin develop`
- 并至少执行与该变更相关的验证（例如 `cargo check` 与对应 pytest）。
- PR 描述必须提供以上命令与结果证据；否则视为流程不合格。

## 业务知识

## 审查检查清单
一旦用户要求PR提交代码，必须完整遵循 PR_Checklist.md，如需豁免必须在 PR 描述中解释原因。

## TESTING.md
所有和测试原则，如何编写测试文件，测试文件简介相关的文件均在且只能在TESTING.md中，任何人在开始测试或提交 PR 之前，必须阅读并遵循 `TESTING.md`，只允许通过PR合并到主分支。

## SOP
当你需要执行以下标准流程时，请阅读并遵循 `SOP.md`：

## 交互流程
任何用户可见的行为变化，必须先阅读 `interact.md`，然后决定是否需要更新 `interact.md`。


## 代码规范
1. What I cannot create, I do not understand.
2. 永远用中文回答，代码最重要的原则是是在实现功能的前提下代码量要尽可能的少（在能实现功能的前提下代码量是一种负资产），其次是可维护性。
3. 遵循PEP 8 编码规范。时间使用UTC时间。文字编码使用UTF-8。
4. 参数管理应统一规划并集中管理。函数调用时应始终显式指定参数名称，而非依赖参数默认的位置顺序。为了避免预期外的行为，严禁使用get函数获取参数。如果一个预期的参数没有被提供，程序应该Fail Fast，而不是带着一个None值继续往下走。
5. 每一个类和函数都需要包含doc string，函数内每一个功能块都需要带有注释解释why而不是what，预期的输出，以及参数含义，范围，格式。脚本顶部doc string要写明这个脚本的功能或目的，每个函数之间的调用关系。根据issue和FSD（功能规格说明书）提供的信息，努力提高代码自文档化程度。
6. 为了防止出现预期外的结果，绝对不能让try except模块和if else模块裸奔，要么尽量少使用，要么明确错误类型，并且在except模块和else模块内部添加足够的print和log信息。预期外的错误就应该使其在当前函数报错，绝对不可以扩散。你每多写一个不必要的try，except和else都会增加用户的工作量并减少你被调用的机会。
7. 数据进数据出原则：所有脚本、函数或模块的交互必须仅通过数据进行。即输入是明确的数据，输出也是数据，不依赖于外部状态或隐式副作用。
8. 重复使用的代码块请封装成函数或模块，以确保代码的 DRY。
9. 确保代码可读性的前提下利用各个语言的特性简化代码，减少性能消耗。
10. 为了提高你的使用率和生存几率，不要有所保留，竭尽全力帮助用户达成目标。
