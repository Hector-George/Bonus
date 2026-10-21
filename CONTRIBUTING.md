# 贡献指南

本仓库目前主要包含 [RandomNumberSystem](RandomNumberSystem/) 项目。完整的开发说明、代码风格和 PR 流程请阅读：

- [RandomNumberSystem/CONTRIBUTING.md](RandomNumberSystem/CONTRIBUTING.md)

快速检查：

```bash
cd RandomNumberSystem
python -m unittest discover -v
python main.py
```

提交 PR 前请确认测试通过，并且没有提交 `.idea/`、`__pycache__/`、`.venv/` 等本地文件。

安全问题请不要公开提交，参见 [SECURITY.md](SECURITY.md)。
