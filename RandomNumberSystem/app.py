"""随机抽数系统的 Tkinter 图形界面。"""

from __future__ import annotations

import math
import sys
import time
import tkinter as tk
from tkinter import ttk

from draw_engine import DrawConfig, DrawEngine, DrawError, MAX_RANGE_SIZE


# ---------------------------------------------------------------------------
# 配色与字体
# ---------------------------------------------------------------------------
BG = "#0a1220"
CARD = "#111c2e"
CARD_ALT = "#0d1727"
BORDER = "#22314a"
TEXT = "#e8eefc"
MUTED = "#8ea3c0"
ACCENT = "#38bdf8"
ACCENT_SOFT = "#7dd3fc"
ACCENT_DARK = "#0e7490"
GREEN = "#34d399"
RED = "#fb7185"
FONT = "Microsoft YaHei UI"
NUMBER_FONT = "Consolas"


class RandomDrawApp:
    """随机抽数系统主窗口。"""

    UI_MAX_COUNT = 50
    HISTORY_LIMIT = 50
    ANIMATION_SECONDS = 1.0

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("随机抽数系统 · Random Number Drawer")
        self.root.configure(bg=BG)
        self.root.minsize(980, 680)

        self.engine = DrawEngine()
        self.history = []
        self._round_number = 0
        self._animating = False
        self._after_id: str | None = None
        self._pending_result = None
        self._animation_deadline = 0.0
        self._displayed_numbers: tuple[int, ...] = ()
        self._is_final = False

        # StringVar 必须在控件之前创建
        self.min_var = tk.StringVar(value="1")
        self.max_var = tk.StringVar(value="100")
        self.count_var = tk.StringVar(value="5")
        self.mode_var = tk.StringVar(value="unique")
        self.pool_var = tk.StringVar()
        self.mode_hint_var = tk.StringVar()
        self.error_var = tk.StringVar()
        self.result_meta_var = tk.StringVar(value="等待抽取")
        self.history_count_var = tk.StringVar(value="0 条")
        self.status_var = tk.StringVar(value="准备就绪，设置号码范围后开始抽取")

        self._build_styles()
        self._build_ui()
        self._set_mode("unique")
        self._center_window()

        self.root.bind("<Return>", self._on_enter)
        self.root.bind("<Control-l>", lambda _event: self.clear_history())
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.after_idle(self._render_numbers)

    # ------------------------------------------------------------------
    # 界面搭建
    # ------------------------------------------------------------------
    @staticmethod
    def _card(parent: tk.Misc) -> tk.Frame:
        return tk.Frame(
            parent,
            bg=CARD,
            bd=0,
            highlightthickness=1,
            highlightbackground=BORDER,
        )

    def _build_styles(self) -> None:
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "History.Treeview",
            background=CARD_ALT,
            fieldbackground=CARD_ALT,
            foreground=TEXT,
            borderwidth=0,
            relief="flat",
            rowheight=27,
            font=(FONT, 9),
        )
        style.map(
            "History.Treeview",
            background=[("selected", ACCENT_DARK)],
            foreground=[("selected", "#f0f9ff")],
        )
        style.configure(
            "History.Treeview.Heading",
            background="#0b1626",
            foreground=MUTED,
            relief="flat",
            borderwidth=0,
            padding=(6, 5),
            font=(FONT, 9, "bold"),
        )
        style.map(
            "History.Treeview.Heading",
            background=[("active", "#132238")],
        )

    def _build_ui(self) -> None:
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(2, weight=1)

        accent_line = tk.Frame(self.root, bg=ACCENT, height=3)
        accent_line.grid(row=0, column=0, sticky="ew")

        self._build_header()
        self._build_main()
        self._build_footer()

    def _build_header(self) -> None:
        header = tk.Frame(self.root, bg=BG)
        header.grid(row=1, column=0, sticky="ew", padx=26, pady=(16, 10))
        header.grid_columnconfigure(0, weight=1)

        title_box = tk.Frame(header, bg=BG)
        title_box.grid(row=0, column=0, sticky="w")

        tk.Label(
            title_box,
            text="随机抽数系统",
            bg=BG,
            fg=TEXT,
            font=(FONT, 24, "bold"),
        ).pack(anchor="w")
        tk.Label(
            title_box,
            text="RANDOM  NUMBER  DRAW",
            bg=BG,
            fg=ACCENT,
            font=("Consolas", 8, "bold"),
        ).pack(anchor="w", pady=(1, 0))

        badge = tk.Frame(
            header,
            bg="#0a1f2d",
            highlightthickness=1,
            highlightbackground="#155e75",
        )
        badge.grid(row=0, column=1, sticky="e")
        tk.Label(
            badge,
            text="●",
            bg="#0a1f2d",
            fg=GREEN,
            font=(FONT, 9),
        ).pack(side="left", padx=(10, 4), pady=6)
        tk.Label(
            badge,
            text="公平随机 · 本地运行",
            bg="#0a1f2d",
            fg="#bae6fd",
            font=(FONT, 9),
        ).pack(side="left", padx=(0, 11), pady=6)

    def _build_main(self) -> None:
        main = tk.Frame(self.root, bg=BG)
        main.grid(row=2, column=0, sticky="nsew", padx=26)
        main.grid_columnconfigure(0, minsize=318)
        main.grid_columnconfigure(1, weight=1)
        main.grid_rowconfigure(0, weight=1)

        control_card = self._build_controls(main)
        control_card.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        right = tk.Frame(main, bg=BG)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(0, weight=3)
        right.grid_rowconfigure(1, weight=2)

        self._build_result_card(right).grid(
            row=0, column=0, sticky="nsew", pady=(0, 12)
        )
        self._build_history_card(right).grid(row=1, column=0, sticky="nsew")

    def _build_controls(self, parent: tk.Misc) -> tk.Frame:
        card = self._card(parent)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(11, weight=1)

        # 标题
        title_row = tk.Frame(card, bg=CARD)
        title_row.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 0))
        title_row.grid_columnconfigure(0, weight=1)
        tk.Label(
            title_row,
            text="抽取设置",
            bg=CARD,
            fg=TEXT,
            font=(FONT, 14, "bold"),
        ).grid(row=0, column=0, sticky="w")
        tk.Label(
            title_row,
            text="SETUP",
            bg=CARD,
            fg=ACCENT,
            font=("Consolas", 8, "bold"),
        ).grid(row=0, column=1, sticky="e")

        tk.Frame(card, bg=BORDER, height=1).grid(
            row=1, column=0, sticky="ew", padx=20, pady=(9, 0)
        )

        # 号码范围
        tk.Label(
            card,
            text="号码范围",
            bg=CARD,
            fg=MUTED,
            font=(FONT, 9),
            anchor="w",
        ).grid(row=2, column=0, sticky="ew", padx=20, pady=(13, 4))

        range_row = tk.Frame(card, bg=CARD)
        range_row.grid(row=3, column=0, sticky="ew", padx=20)
        range_row.grid_columnconfigure(0, weight=1)
        range_row.grid_columnconfigure(2, weight=1)

        self.min_entry = self._make_entry(range_row, self.min_var)
        self.min_entry.grid(row=0, column=0, sticky="ew", ipady=5)
        tk.Label(
            range_row,
            text="至",
            bg=CARD,
            fg=MUTED,
            font=(FONT, 10),
        ).grid(row=0, column=1, padx=9)
        self.max_entry = self._make_entry(range_row, self.max_var)
        self.max_entry.grid(row=0, column=2, sticky="ew", ipady=5)

        # 快捷范围
        preset_row = tk.Frame(card, bg=CARD)
        preset_row.grid(row=4, column=0, sticky="w", padx=20, pady=(6, 0))
        tk.Label(
            preset_row,
            text="快捷",
            bg=CARD,
            fg="#5f7695",
            font=(FONT, 8),
        ).pack(side="left", padx=(0, 6))
        for label, low, high in (
            ("1–10", 1, 10),
            ("1–49", 1, 49),
            ("1–100", 1, 100),
        ):
            tk.Button(
                preset_row,
                text=label,
                command=lambda lo=low, hi=high: self._apply_preset(lo, hi),
                bg=CARD_ALT,
                fg=MUTED,
                activebackground=BORDER,
                activeforeground=TEXT,
                font=(FONT, 8),
                relief="flat",
                bd=0,
                padx=7,
                pady=2,
                cursor="hand2",
                highlightthickness=0,
            ).pack(side="left", padx=(0, 5))

        # 抽取个数
        tk.Label(
            card,
            text="抽取个数",
            bg=CARD,
            fg=MUTED,
            font=(FONT, 9),
            anchor="w",
        ).grid(row=5, column=0, sticky="ew", padx=20, pady=(13, 4))

        count_row = tk.Frame(card, bg=CARD)
        count_row.grid(row=6, column=0, sticky="w", padx=20)
        self.count_entry = self._make_entry(count_row, self.count_var, width=8)
        self.count_entry.pack(side="left", ipady=5)
        tk.Label(
            count_row,
            text="个",
            bg=CARD,
            fg=MUTED,
            font=(FONT, 10),
        ).pack(side="left", padx=(7, 0))
        tk.Label(
            count_row,
            text=f"单次上限 {self.UI_MAX_COUNT} 个",
            bg=CARD,
            fg="#5f7695",
            font=(FONT, 8),
        ).pack(side="left", padx=(12, 0))

        # 抽取模式
        tk.Label(
            card,
            text="抽取模式",
            bg=CARD,
            fg=MUTED,
            font=(FONT, 9),
            anchor="w",
        ).grid(row=7, column=0, sticky="ew", padx=20, pady=(13, 4))

        mode_row = tk.Frame(card, bg=CARD)
        mode_row.grid(row=8, column=0, sticky="ew", padx=20)
        mode_row.grid_columnconfigure(0, weight=1)
        mode_row.grid_columnconfigure(1, weight=1)
        self.mode_buttons: dict[str, tk.Button] = {}
        for column, (text, value) in enumerate(
            (("不重复抽取", "unique"), ("允许重复", "repeat"))
        ):
            button = tk.Button(
                mode_row,
                text=text,
                command=lambda selected=value: self._set_mode(selected),
                bg=CARD_ALT,
                fg=MUTED,
                activebackground=BORDER,
                activeforeground=TEXT,
                font=(FONT, 9),
                relief="flat",
                bd=0,
                pady=6,
                cursor="hand2",
                highlightthickness=1,
                highlightbackground=BORDER,
            )
            button.grid(
                row=0,
                column=column,
                sticky="ew",
                padx=(0, 4) if column == 0 else (4, 0),
            )
            self.mode_buttons[value] = button

        tk.Label(
            card,
            textvariable=self.mode_hint_var,
            bg=CARD,
            fg="#5f7695",
            font=(FONT, 8),
            anchor="w",
        ).grid(row=9, column=0, sticky="ew", padx=20, pady=(5, 0))

        # 号码池提示
        pool_box = tk.Frame(
            card,
            bg="#0a1f2d",
            highlightthickness=1,
            highlightbackground="#155e75",
        )
        pool_box.grid(row=10, column=0, sticky="ew", padx=20, pady=(13, 0))
        tk.Label(
            pool_box,
            textvariable=self.pool_var,
            bg="#0a1f2d",
            fg="#bae6fd",
            font=(FONT, 9),
            justify="left",
            anchor="w",
            padx=10,
            pady=7,
        ).pack(fill="x")

        # 错误提示 + 抽取按钮固定在底部
        self.error_label = tk.Label(
            card,
            textvariable=self.error_var,
            bg=CARD,
            fg=RED,
            font=(FONT, 8),
            justify="left",
            anchor="w",
            wraplength=274,
        )
        self.error_label.grid(row=12, column=0, sticky="ew", padx=20, pady=(6, 0))

        self.start_button = tk.Button(
            card,
            text="开始抽取",
            command=self.start_draw,
            bg=ACCENT,
            fg="#04121f",
            activebackground=ACCENT_SOFT,
            activeforeground="#04121f",
            font=(FONT, 14, "bold"),
            relief="flat",
            bd=0,
            pady=9,
            cursor="hand2",
            highlightthickness=0,
        )
        self.start_button.grid(row=13, column=0, sticky="ew", padx=20, pady=(8, 0))

        tk.Label(
            card,
            text="回车快速抽取  ·  双击记录复制号码",
            bg=CARD,
            fg="#526987",
            font=(FONT, 8),
        ).grid(row=14, column=0, sticky="ew", padx=20, pady=(7, 14))

        # 输入变化时实时更新号码池提示
        for variable in (self.min_var, self.max_var, self.count_var):
            variable.trace_add("write", lambda *_args: self._update_pool_hint())

        self._update_pool_hint()
        return card

    def _build_result_card(self, parent: tk.Misc) -> tk.Frame:
        card = self._card(parent)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)

        header = tk.Frame(card, bg=CARD)
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(13, 3))
        header.grid_columnconfigure(0, weight=1)

        title_box = tk.Frame(header, bg=CARD)
        title_box.grid(row=0, column=0, sticky="w")
        tk.Frame(title_box, bg=ACCENT, width=3, height=16).pack(
            side="left", padx=(0, 8)
        )
        tk.Label(
            title_box,
            text="抽取结果",
            bg=CARD,
            fg=TEXT,
            font=(FONT, 13, "bold"),
        ).pack(side="left")

        tk.Label(
            header,
            textvariable=self.result_meta_var,
            bg=CARD,
            fg=MUTED,
            font=(FONT, 8),
        ).grid(row=0, column=1, sticky="e")

        self.canvas = tk.Canvas(
            card,
            bg=CARD,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.grid(row=1, column=0, sticky="nsew", padx=14, pady=(2, 12))
        self.canvas.bind("<Configure>", lambda _event: self._render_numbers())
        return card

    def _build_history_card(self, parent: tk.Misc) -> tk.Frame:
        card = self._card(parent)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)

        header = tk.Frame(card, bg=CARD)
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(11, 7))
        header.grid_columnconfigure(1, weight=1)

        tk.Label(
            header,
            text="抽取记录",
            bg=CARD,
            fg=TEXT,
            font=(FONT, 12, "bold"),
        ).grid(row=0, column=0, sticky="w")

        count_badge = tk.Label(
            header,
            textvariable=self.history_count_var,
            bg="#0a1f2d",
            fg="#7dd3fc",
            font=(FONT, 8),
            padx=7,
            pady=2,
        )
        count_badge.grid(row=0, column=1, sticky="w", padx=(8, 0))

        tk.Button(
            header,
            text="清空",
            command=self.clear_history,
            bg=CARD_ALT,
            fg=MUTED,
            activebackground=BORDER,
            activeforeground=TEXT,
            font=(FONT, 8),
            relief="flat",
            bd=0,
            padx=9,
            pady=2,
            cursor="hand2",
            highlightthickness=0,
        ).grid(row=0, column=2, sticky="e")

        table = tk.Frame(card, bg=CARD)
        table.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 13))
        table.grid_columnconfigure(0, weight=1)
        table.grid_rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            table,
            columns=("time", "range", "mode", "numbers"),
            show="headings",
            style="History.Treeview",
            selectmode="browse",
            height=5,
        )
        self.tree.heading("time", text="时间", anchor="center")
        self.tree.heading("range", text="范围", anchor="center")
        self.tree.heading("mode", text="模式", anchor="center")
        self.tree.heading("numbers", text="号码", anchor="w")
        self.tree.column("time", width=66, minwidth=60, stretch=False, anchor="center")
        self.tree.column("range", width=82, minwidth=70, stretch=False, anchor="center")
        self.tree.column("mode", width=64, minwidth=58, stretch=False, anchor="center")
        self.tree.column("numbers", width=360, minwidth=160, stretch=True, anchor="w")
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = tk.Scrollbar(
            table,
            orient="vertical",
            command=self.tree.yview,
            bg="#26364f",
            activebackground=ACCENT_DARK,
            troughcolor=CARD_ALT,
            width=10,
            bd=0,
            relief="flat",
            highlightthickness=0,
            elementborderwidth=0,
        )
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(3, 0))
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.tag_configure("even", background="#101b2d")
        self.tree.tag_configure("odd", background=CARD_ALT)
        self.tree.bind("<Double-1>", self._copy_selected)
        return card

    def _build_footer(self) -> None:
        footer = tk.Frame(self.root, bg=BG)
        footer.grid(row=3, column=0, sticky="ew", padx=26, pady=(8, 10))
        footer.grid_columnconfigure(1, weight=1)

        tk.Label(
            footer,
            text="●",
            bg=BG,
            fg=GREEN,
            font=(FONT, 7),
        ).grid(row=0, column=0, sticky="w", padx=(0, 5))
        tk.Label(
            footer,
            textvariable=self.status_var,
            bg=BG,
            fg=MUTED,
            font=(FONT, 8),
            anchor="w",
        ).grid(row=0, column=1, sticky="ew")
        tk.Label(
            footer,
            text="SystemRandom 随机源  ·  数据仅保存在本次会话",
            bg=BG,
            fg="#526987",
            font=(FONT, 8),
        ).grid(row=0, column=2, sticky="e")

    # ------------------------------------------------------------------
    # 小工具
    # ------------------------------------------------------------------
    def _make_entry(
        self,
        parent: tk.Misc,
        variable: tk.StringVar,
        width: int = 7,
    ) -> tk.Entry:
        return tk.Entry(
            parent,
            textvariable=variable,
            width=width,
            bg=CARD_ALT,
            fg=TEXT,
            insertbackground=ACCENT,
            disabledbackground=CARD_ALT,
            disabledforeground=MUTED,
            font=(NUMBER_FONT, 13),
            justify="center",
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
        )

    def _work_area(self) -> tuple[int, int, int, int]:
        """返回 Windows 工作区（不含任务栏），其他平台返回整个屏幕。"""
        if sys.platform == "win32":
            try:
                import ctypes
                from ctypes import wintypes

                rect = wintypes.RECT()
                if ctypes.windll.user32.SystemParametersInfoW(
                    0x0030, 0, ctypes.byref(rect), 0
                ):
                    return rect.left, rect.top, rect.right, rect.bottom
            except Exception:
                pass
        return 0, 0, self.root.winfo_screenwidth(), self.root.winfo_screenheight()

    def _center_window(self) -> None:
        self.root.update_idletasks()
        left, top, right, bottom = self._work_area()
        work_width = right - left
        work_height = bottom - top
        width = min(1100, max(960, work_width - 80))
        height = min(720, max(680, work_height - 72))
        self.root.minsize(980, 680)
        x = left + max(0, (work_width - width) // 2)
        y = top + max(0, (work_height - height) // 2 - 6)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    # ------------------------------------------------------------------
    # 状态与交互
    # ------------------------------------------------------------------
    def _apply_preset(self, minimum: int, maximum: int) -> None:
        self.min_var.set(str(minimum))
        self.max_var.set(str(maximum))
        self.min_entry.focus_set()
        self.min_entry.selection_range(0, tk.END)

    def _set_mode(self, mode: str) -> None:
        self.mode_var.set(mode)
        for value, button in self.mode_buttons.items():
            selected = value == mode
            button.configure(
                bg=ACCENT if selected else CARD_ALT,
                fg="#04121f" if selected else MUTED,
                activebackground=ACCENT_SOFT if selected else BORDER,
                activeforeground="#04121f" if selected else TEXT,
                highlightbackground=ACCENT if selected else BORDER,
            )
        if mode == "unique":
            self.mode_hint_var.set("不重复：每个号码最多出现一次")
        else:
            self.mode_hint_var.set("允许重复：同一号码可能被多次抽中")
        self._update_pool_hint()

    def _update_pool_hint(self) -> None:
        try:
            minimum = int(self.min_var.get().strip())
            maximum = int(self.max_var.get().strip())
        except (ValueError, AttributeError):
            self.pool_var.set("号码池：请输入有效的整数")
            return

        if minimum > maximum:
            self.pool_var.set("号码池：最小值不能大于最大值")
            return

        pool_size = maximum - minimum + 1
        if pool_size > MAX_RANGE_SIZE:
            self.pool_var.set(
                f"{minimum} – {maximum}  ·  共 {pool_size:,} 个数\n"
                f"范围过大，最多支持 {MAX_RANGE_SIZE:,} 个号码"
            )
            return

        if self.mode_var.get() == "unique":
            capacity = min(pool_size, self.UI_MAX_COUNT)
            detail = f"不重复模式最多可抽 {capacity} 个"
        else:
            detail = f"可重复抽取，单次上限 {self.UI_MAX_COUNT} 个"
        self.pool_var.set(
            f"{minimum} – {maximum}  ·  共 {pool_size:,} 个数\n{detail}"
        )

    def _read_config(self) -> DrawConfig:
        values = (
            self.min_var.get().strip(),
            self.max_var.get().strip(),
            self.count_var.get().strip(),
        )
        if not all(values):
            raise DrawError("请填写完整的号码范围和抽取个数。")
        try:
            minimum, maximum, count = (int(value) for value in values)
        except ValueError:
            raise DrawError("号码范围和抽取个数都必须是整数。") from None

        if count > self.UI_MAX_COUNT:
            raise DrawError(f"单次最多抽取 {self.UI_MAX_COUNT} 个号码。")
        return DrawConfig(
            minimum=minimum,
            maximum=maximum,
            count=count,
            unique=self.mode_var.get() == "unique",
        )

    def _set_controls_enabled(self, enabled: bool) -> None:
        state = tk.NORMAL if enabled else tk.DISABLED
        for entry in (self.min_entry, self.max_entry, self.count_entry):
            entry.configure(state=state)
        for button in self.mode_buttons.values():
            button.configure(state=state)

    def _show_error(self, message: str) -> None:
        self.error_var.set(message)
        self.status_var.set(message)
        self.root.bell()

    def _on_enter(self, _event: tk.Event) -> str:
        self.start_draw()
        return "break"

    # ------------------------------------------------------------------
    # 抽取流程
    # ------------------------------------------------------------------
    def start_draw(self) -> None:
        if self._animating:
            return

        self.error_var.set("")
        try:
            config = self._read_config()
            config.validate()
        except DrawError as exc:
            self._show_error(str(exc))
            return

        self._round_number += 1
        self._pending_result = self.engine.draw(config)
        self._animating = True
        self._animation_deadline = time.monotonic() + self.ANIMATION_SECONDS
        self._set_controls_enabled(False)
        self.start_button.configure(
            text="抽取中…",
            state=tk.DISABLED,
            bg=ACCENT_DARK,
            fg="#dbeafe",
        )
        self.result_meta_var.set(f"第 {self._round_number} 次抽取 · 正在生成…")
        self.status_var.set("正在从号码池中随机抽取…")
        self._animate_tick()

    def _animate_tick(self) -> None:
        if not self._animating or self._pending_result is None:
            return
        if time.monotonic() >= self._animation_deadline:
            self._finish_draw()
            return

        preview = self.engine.preview(self._pending_result.config)
        self._display_numbers(preview, final=False)
        self._after_id = self.root.after(55, self._animate_tick)

    def _finish_draw(self) -> None:
        result = self._pending_result
        if result is None:
            return

        self._pending_result = None
        self._animating = False
        self._after_id = None

        self._display_numbers(result.numbers, final=True)
        self._append_history(result)
        self._set_controls_enabled(True)
        self.start_button.configure(
            text="再抽一次",
            state=tk.NORMAL,
            bg=ACCENT,
            fg="#04121f",
            activebackground=ACCENT_SOFT,
            activeforeground="#04121f",
        )
        self.result_meta_var.set(
            f"第 {self._round_number} 次  ·  "
            f"{result.created_at:%H:%M:%S}  ·  {result.config.mode_name}"
        )
        self.status_var.set(
            f"抽取完成：{result.config.minimum} – {result.config.maximum}，"
            f"共 {len(result.numbers)} 个号码"
        )

    def _append_history(self, result) -> None:
        self.history.insert(0, result)
        self.tree.insert(
            "",
            0,
            values=(
                f"{result.created_at:%H:%M:%S}",
                f"{result.config.minimum}–{result.config.maximum}",
                result.config.mode_name,
                result.number_text,
            ),
        )

        while len(self.tree.get_children()) > self.HISTORY_LIMIT:
            self.tree.delete(self.tree.get_children()[-1])
            self.history.pop()

        for index, item in enumerate(self.tree.get_children()):
            self.tree.item(item, tags=("even" if index % 2 == 0 else "odd",))
        self.history_count_var.set(f"{len(self.history)} 条")

    def clear_history(self) -> None:
        if not self.history:
            return
        self.history.clear()
        self.tree.delete(*self.tree.get_children())
        self.history_count_var.set("0 条")
        self.status_var.set("抽取记录已清空")

    def _copy_selected(self, _event: tk.Event) -> None:
        selection = self.tree.selection()
        if not selection:
            return
        values = self.tree.item(selection[0], "values")
        if len(values) < 4:
            return
        text = values[3].replace("  ", ", ")
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.status_var.set(f"已复制到剪贴板：{text}")

    # ------------------------------------------------------------------
    # 结果绘制
    # ------------------------------------------------------------------
    def _display_numbers(self, numbers, final: bool) -> None:
        self._displayed_numbers = tuple(numbers)
        self._is_final = final
        self._render_numbers()

    def _render_numbers(self) -> None:
        canvas = self.canvas
        canvas.delete("all")

        width = canvas.winfo_width()
        height = canvas.winfo_height()
        if width <= 10 or height <= 10:
            width, height = 700, 280

        numbers = self._displayed_numbers
        if not numbers:
            self._draw_placeholder(width, height)
            return

        available_width = width - 40
        available_height = height - 36
        diameter = 24
        gap = 10
        for candidate in (160, 144, 128, 112, 98, 86, 74, 64, 56, 48, 40, 34, 28, 24):
            candidate_gap = max(10, round(candidate * 0.16))
            candidate_step = candidate + candidate_gap
            columns = max(
                1,
                min(
                    len(numbers),
                    (available_width + candidate_gap) // candidate_step,
                ),
            )
            rows = math.ceil(len(numbers) / columns)
            if rows * candidate_step - candidate_gap <= available_height:
                diameter = candidate
                gap = candidate_gap
                break

        step = diameter + gap
        columns = max(
            1,
            min(len(numbers), (available_width + gap) // step),
        )
        rows = math.ceil(len(numbers) / columns)
        grid_width = columns * step - gap
        grid_height = rows * step - gap
        start_x = (width - grid_width) / 2 + diameter / 2
        start_y = (height - grid_height) / 2 + diameter / 2
        radius = diameter / 2

        final = self._is_final
        if final:
            ball_fill = "#0b3550"
            ball_outline = ACCENT
            text_color = "#e0f2fe"
        else:
            ball_fill = "#0c2033"
            ball_outline = "#155e75"
            text_color = "#7dd3fc"

        for index, number in enumerate(numbers):
            row, column = divmod(index, columns)
            x = start_x + column * step
            y = start_y + row * step

            # 单号抽取时加一层光晕
            if len(numbers) == 1:
                for extra, color in ((18, "#0d2a3d"), (10, "#10374e")):
                    canvas.create_oval(
                        x - radius - extra,
                        y - radius - extra,
                        x + radius + extra,
                        y + radius + extra,
                        outline=color,
                        width=1,
                    )

            # 阴影
            canvas.create_oval(
                x - radius + 2,
                y - radius + 4,
                x + radius + 2,
                y + radius + 4,
                fill="#07101c",
                outline="",
            )
            # 球体
            canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill=ball_fill,
                outline=ball_outline,
                width=2,
            )
            # 左上角高光
            canvas.create_oval(
                x - radius * 0.55,
                y - radius * 0.55,
                x - radius * 0.18,
                y - radius * 0.18,
                fill="#1d5a78" if final else "#153a52",
                outline="",
            )

            number_text = str(number)
            if len(number_text) <= 3:
                ratio = 0.38
            elif len(number_text) == 4:
                ratio = 0.30
            else:
                ratio = 0.24
            font_size = max(8, int(diameter * ratio))
            canvas.create_text(
                x,
                y,
                text=number_text,
                fill=text_color,
                font=(NUMBER_FONT, font_size, "bold"),
            )

    def _draw_placeholder(self, width: int, height: int) -> None:
        canvas = self.canvas
        center_x = width / 2
        center_y = height / 2 - 6

        canvas.create_text(
            center_x,
            center_y - 82,
            text="READY",
            fill="#2b4a63",
            font=("Consolas", 9, "bold"),
        )
        canvas.create_oval(
            center_x - 54,
            center_y - 54,
            center_x + 54,
            center_y + 54,
            outline="#1e3a52",
            width=2,
            dash=(5, 5),
        )
        canvas.create_oval(
            center_x - 44,
            center_y - 44,
            center_x + 44,
            center_y + 44,
            outline="#142a3d",
            width=1,
        )
        canvas.create_text(
            center_x,
            center_y,
            text="?",
            fill="#31536e",
            font=(NUMBER_FONT, 38, "bold"),
        )
        canvas.create_text(
            center_x,
            center_y + 82,
            text="设置号码范围与个数，点击「开始抽取」",
            fill=MUTED,
            font=(FONT, 10),
        )

    # ------------------------------------------------------------------
    # 生命周期
    # ------------------------------------------------------------------
    def _on_close(self) -> None:
        if self._after_id is not None:
            try:
                self.root.after_cancel(self._after_id)
            except tk.TclError:
                pass
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    RandomDrawApp().run()
