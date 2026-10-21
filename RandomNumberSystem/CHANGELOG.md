# 更新日志

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 的结构，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.0.0] - 2026-10-21

### 新增

- Tkinter 图形界面，支持自定义号码范围、抽取个数和抽取模式
- 不重复抽取与允许重复抽取
- 号码球结果展示和滚动抽取动画
- 本次会话内的抽取历史，最多保留 50 条
- 双击历史记录复制号码、`Ctrl+L` 清空记录
- 命令行模式：`python main.py --cli --min 1 --max 49 --count 6`
- 基于 `random.SystemRandom` 的系统熵源
- 11 个单元测试，覆盖参数校验与核心抽取逻辑
- MIT 开源协议、贡献指南、行为准则、安全策略和 GitHub Actions 测试
