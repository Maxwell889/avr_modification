# AVR实验框架

## 概述
本目录包含用于测试AVR模型检查器在crafted benchmark上性能的实验脚本。

## 文件说明

### 核心脚本
- `run_avr_experiments.py` - AVR实验主脚本，测试所有crafted案例

### 输出文件
- `avr_output/` - AVR测试的详细输出日志目录
- `avr_results.json` - 实验结果的JSON格式详细数据
- `avr_stats.txt` - 统计结果的文本格式摘要

## 使用方法

### 1. 运行AVR实验
```bash
python run_avr_experiments.py
```

这将：
- 自动发现 `/tests/crafted/` 目录下的所有Verilog文件
- 对每个文件运行AVR模型检查器（1秒超时）
- 分类统计结果（成功/超时/错误/其他失败）
- 生成详细的统计报告

### 2. 查看结果
实验完成后会生成：
- 控制台输出：实时进度和最终统计
- `avr_results.json`：包含所有测试案例的详细结果
- `avr_stats.txt`：易于阅读的统计摘要

## 实验配置

### 参数设置
- **超时时间**: 1秒（在脚本中的 `TIMEOUT` 变量）
- **测试目录**: `/tests/crafted/`
- **AVR路径**: `/build/bin/reach_y2`

### 结果分类
- **✅ 成功**: AVR成功验证了属性（safe/unsafe）
- **⏱️ 超时**: 在1秒内未能完成验证
- **🚫 错误**: AVR运行时出现错误
- **❌ 其他失败**: 其他未分类的失败情况

## 结果解释

### AVR输出含义
- `h` 或 `safe`: 属性被验证为安全（UNSAT）
- `cea` 或 `unsafe`: 发现了反例（SAT）
- `timeout`: 超时未完成

### JSON结果格式
```json
{
  "experiment": "AVR Crafted Cases",
  "timeout": 1,
  "total_cases": 24,
  "solved_count": X,
  "timeout_count": Y,
  "error_count": Z,
  "solved_cases": ["case1", "case2", ...],
  "timeout_cases": ["case3", ...],
  "detailed_results": [...]
}
```

## 注意事项
1. 确保AVR已正确编译并位于 `/build/bin/reach_y2`
2. 测试目录包含24个crafted benchmark案例
3. 每个案例设置1秒超时限制
4. 结果会保存在当前目录下的输出文件中

## 扩展使用
如需修改实验参数，编辑脚本中的配置常量：
- `TIMEOUT`: 调整超时时间
- `TESTS_DIR`: 修改测试目录
- AVR命令行参数可在 `run_avr_on_file()` 函数中调整
