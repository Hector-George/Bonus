# 贡献指南

感谢你愿意改进「随机抽数系统」。无论是报告问题、提出建议，还是提交代码，都很有价值。

## 报告问题

- 先搜索现有的 [Issues](https://github.com/Hector-George/Bonus/issues)，避免重复。
- 使用 Bug Report 模板，说明操作系统、Python 版本、复现步骤和期望结果。
- 如果问题涉及界面，请附上截图；如果涉及抽取结果，请附上号码范围、模式和个数。
- 不要在 Issue 中粘贴个人敏感信息。

## 提出功能建议

使用 Feature Request 模板，说明使用场景和期望效果。请尽量描述「为什么需要」，而不只是「增加什么按钮」。

## 本地开发

1. Fork 仓库并克隆到本地：

   ```bash
   git clone https://github.com/<your-name>/Bonus.git
   cd Bonus/RandomNumberSystem
   ```

2. 运行程序：

   ```bash
   python main.py
   ```

3. 运行测试：

   ```bash
   python -m unittest discover -v
   ```

项目没有第三方运行依赖，因此不需要创建虚拟环境；如果你使用虚拟环境，也完全没问题。

## 代码风格

- 使用 Python 3.10+ 语法。
- 保持 4 空格缩进，单行尽量不超过 100 个字符。
- 新增抽取逻辑时，优先放进 `draw_engine.py`，并为它补充单元测试。
- GUI 代码放在 `app.py`，避免把业务逻辑写进按钮回调。
- 中文文案保持简洁、明确；错误提示要告诉用户如何修正。
- 不要提交 `.idea/`、`__pycache__/`、`.venv/` 等本地文件。

## 提交 Pull Request

1. 从 `main` 创建一个语义清晰的分支，例如 `fix/range-validation`。
2. 保持改动聚焦，一个 PR 只解决一个问题。
3. 提交信息建议使用 Conventional Commits：

   ```text
   feat: add repeat-mode animation
   fix: reject count larger than pool
   docs: update CLI examples
   test: cover negative ranges
   ```

4. 在 PR 描述中说明改动内容、测试方式和相关 Issue。
5. 确认 `python -m unittest discover -v` 全部通过。

## 行为准则

参与本项目即表示你同意遵守 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。

## 许可证

提交代码即表示你同意以本项目的 [MIT License](LICENSE) 发布你的贡献。
