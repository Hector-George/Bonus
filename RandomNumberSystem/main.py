"""随机抽数系统入口。

直接运行进入图形界面；加上 --cli 参数可进入命令行模式：

    python main.py
    python main.py --cli --min 1 --max 49 --count 6
"""

from __future__ import annotations

import argparse
import sys

from draw_engine import DrawConfig, DrawEngine, DrawError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="随机抽数系统：图形界面 / 命令行双模式",
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="使用命令行模式，不打开图形界面",
    )
    parser.add_argument(
        "--min",
        dest="minimum",
        type=int,
        default=1,
        help="号码最小值（默认 1）",
    )
    parser.add_argument(
        "--max",
        dest="maximum",
        type=int,
        default=100,
        help="号码最大值（默认 100）",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="抽取个数（默认 5）",
    )
    parser.add_argument(
        "--allow-duplicates",
        action="store_true",
        help="允许号码重复（默认不重复）",
    )
    return parser


def _use_utf8_for_redirected_output() -> None:
    """输出被重定向（IDE、管道）时统一使用 UTF-8，避免中文乱码。"""
    for stream in (sys.stdout, sys.stderr):
        if stream is not None and hasattr(stream, "reconfigure"):
            try:
                if not stream.isatty():
                    stream.reconfigure(encoding="utf-8")
            except (OSError, ValueError):
                pass


def run_cli(config: DrawConfig) -> None:
    _use_utf8_for_redirected_output()
    result = DrawEngine().draw(config)
    line = "=" * 58
    print(line)
    print("  随机抽数系统 · 抽取结果")
    print(line)
    print(f"  号码范围：{config.minimum} – {config.maximum}")
    print(f"  抽取模式：{config.mode_name}")
    print(f"  抽取个数：{config.count}")
    print("-" * 58)
    print("  " + "   ".join(f"{number:>3}" for number in result.numbers))
    print("-" * 58)
    print(f"  抽取时间：{result.created_at:%Y-%m-%d %H:%M:%S}")
    print(line)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = DrawConfig(
        minimum=args.minimum,
        maximum=args.maximum,
        count=args.count,
        unique=not args.allow_duplicates,
    )

    if args.cli:
        try:
            run_cli(config)
        except DrawError as exc:
            print(f"参数错误：{exc}", file=sys.stderr)
            return 2
        return 0

    try:
        from app import RandomDrawApp
    except ImportError as exc:
        print(f"无法启动图形界面：{exc}", file=sys.stderr)
        print("可以改用命令行模式，例如：python main.py --cli", file=sys.stderr)
        return 1

    RandomDrawApp().run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
