"""随机抽数系统的核心逻辑。

这个模块不依赖任何第三方库，也不依赖图形界面，方便单独测试与复用。
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime


MAX_DRAW_COUNT = 1000
MAX_RANGE_SIZE = 10_000_000


class DrawError(ValueError):
    """抽取参数不合法时抛出的异常。"""


@dataclass(frozen=True, slots=True)
class DrawConfig:
    """一次抽取的配置。"""

    minimum: int = 1
    maximum: int = 100
    count: int = 5
    unique: bool = True

    @property
    def pool_size(self) -> int:
        """号码池中一共有多少个数。"""
        return self.maximum - self.minimum + 1

    @property
    def mode_name(self) -> str:
        return "不重复" if self.unique else "可重复"

    def validate(self) -> None:
        """校验参数，不合法时抛出 DrawError。"""
        if self.minimum > self.maximum:
            raise DrawError("最小值不能大于最大值。")
        if self.count < 1:
            raise DrawError("抽取个数至少为 1 个。")
        if self.count > MAX_DRAW_COUNT:
            raise DrawError(f"单次抽取个数不能超过 {MAX_DRAW_COUNT} 个。")
        if self.pool_size > MAX_RANGE_SIZE:
            raise DrawError(f"号码范围过大，最多支持 {MAX_RANGE_SIZE:,} 个号码。")
        if self.unique and self.count > self.pool_size:
            raise DrawError(f"不重复抽取时，最多只能抽取 {self.pool_size} 个号码。")


@dataclass(frozen=True, slots=True)
class DrawResult:
    """一次抽取的完整结果。"""

    numbers: tuple[int, ...]
    config: DrawConfig
    created_at: datetime

    @property
    def number_text(self) -> str:
        return "  ".join(str(number) for number in self.numbers)

    @property
    def comma_text(self) -> str:
        return ", ".join(str(number) for number in self.numbers)


class DrawEngine:
    """线程安全的抽数引擎。

    默认使用 ``random.SystemRandom``，它来自操作系统熵源，比普通伪随机数
    更适合抽奖、点名等场景。测试时可以注入带固定种子的 ``random.Random``。
    """

    def __init__(self, rng: random.Random | None = None) -> None:
        self._rng = rng if rng is not None else random.SystemRandom()

    @property
    def rng(self) -> random.Random:
        return self._rng

    def draw(self, config: DrawConfig) -> DrawResult:
        """按配置抽取号码，并返回带时间戳的结果。"""
        config.validate()

        if config.unique:
            numbers = self._rng.sample(
                range(config.minimum, config.maximum + 1),
                config.count,
            )
        else:
            numbers = [
                self._rng.randint(config.minimum, config.maximum)
                for _ in range(config.count)
            ]

        return DrawResult(
            numbers=tuple(numbers),
            config=config,
            created_at=datetime.now(),
        )

    def preview(self, config: DrawConfig) -> list[int]:
        """生成一组仅用于界面滚动的预览号码，不写入历史记录。"""
        config.validate()
        if config.unique:
            return self._rng.sample(
                range(config.minimum, config.maximum + 1),
                config.count,
            )
        return [
            self._rng.randint(config.minimum, config.maximum)
            for _ in range(config.count)
        ]
