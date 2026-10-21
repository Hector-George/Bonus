# 随机抽数系统

一个使用 Python 标准库编写的桌面随机抽数工具，带图形界面、抽取动画、历史记录和命令行模式。适合课堂点名、抽奖、随机分组等场景。

[![Tests](https://github.com/Hector-George/Bonus/actions/workflows/random-number-system-tests.yml/badge.svg)](https://github.com/Hector-George/Bonus/actions/workflows/random-number-system-tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg)](https://www.python.org/)

![界面预览](screenshot.png)

## 功能

- 自定义号码范围（支持负数），实时显示号码池大小
- 一次抽取 1–50 个号码，可选「不重复」或「允许重复」
- 抽取过程带滚动动画，结果以号码球展示
- 自动记录抽取时间、范围、模式和号码，最多保留 50 条
- 双击历史记录即可把号码复制到剪贴板
- 按回车快速再抽一次，`Ctrl+L` 清空记录
- 使用 `random.SystemRandom` 系统熵源，不依赖第三方库
- 同一套抽取逻辑同时服务 GUI 和 CLI，方便测试与复用

## 环境要求

- Python 3.10 及以上版本（已在 Python 3.13 测试）
- 图形界面使用 Python 自带的 Tkinter，无需安装第三方依赖
- 支持 Windows、macOS 和 Linux（Linux 需要系统安装 Tk）

## 快速开始

```bash
git clone https://github.com/Hector-George/Bonus.git
cd Bonus/RandomNumberSystem
python main.py
```

也可以直接在 PyCharm 中打开 `RandomNumberSystem` 目录，右键 `main.py`，选择 **Run 'main'**。

## 命令行模式

```bash
python main.py --cli --min 1 --max 49 --count 6
```

允许重复：

```bash
python main.py --cli --min 1 --max 10 --count 5 --allow-duplicates
```

参数说明：

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `--cli` | 使用命令行模式 | 关闭 |
| `--min` | 号码最小值 | `1` |
| `--max` | 号码最大值 | `100` |
| `--count` | 抽取个数 | `5` |
| `--allow-duplicates` | 允许号码重复 | 关闭 |

## 快捷键

| 快捷键 | 功能 |
| --- | --- |
| `Enter` | 开始抽取 / 再抽一次 |
| `Ctrl+L` | 清空抽取记录 |
| 双击历史记录 | 复制该次号码 |

## 测试

```bash
python -m unittest discover -v
```

当前包含 11 个单元测试，覆盖号码范围校验、去重逻辑、可重复模式、固定随机种子、预览接口和结果文本格式化。

## 项目结构

```text
RandomNumberSystem/
├── main.py                 # 程序入口（GUI / CLI）
├── app.py                  # Tkinter 图形界面
├── draw_engine.py          # 抽取逻辑与参数校验
├── tests/
│   └── test_draw_engine.py # 单元测试
├── screenshot.png          # 界面截图
├── requirements.txt        # 无第三方依赖
├── CONTRIBUTING.md         # 贡献指南
├── CODE_OF_CONDUCT.md      # 社区行为准则
├── SECURITY.md             # 安全问题报告方式
├── CHANGELOG.md            # 版本记录
└── LICENSE                 # MIT 协议
```

## 设计说明

抽取逻辑位于 `draw_engine.py`，不依赖 Tkinter，可以单独测试或在其他程序中复用。默认随机源是 `random.SystemRandom`，它从操作系统熵源取数，比普通伪随机数更适合抽奖、点名等场景。测试时可以注入固定种子的 `random.Random`，从而获得可复现的结果。

抽取结果只保存在当前会话内，关闭程序后不会写入磁盘。

## 贡献

欢迎提交 Issue 和 Pull Request。提交前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)，并确保单元测试通过。

## 许可证

本项目采用 [MIT License](LICENSE) 开源。

如果这个项目对你有帮助，欢迎点一个 Star。
