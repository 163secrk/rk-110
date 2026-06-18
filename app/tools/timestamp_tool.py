import time
import datetime
import tkinter as tk
from tkinter import ttk


class TimestampTool(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, style="Content.TFrame")
        self._setup_styles()
        self._create_widgets()
        self._update_current_timestamp()

    def _setup_styles(self):
        style = ttk.Style()
        style.configure("ToolTitle.TLabel",
                        font=("Microsoft YaHei", 16, "bold"),
                        background="#f5f6fa",
                        foreground="#2c3e50")
        style.configure("Section.TLabel",
                        font=("Microsoft YaHei", 11, "bold"),
                        background="#f5f6fa",
                        foreground="#34495e")
        style.configure("SubSection.TLabel",
                        font=("Microsoft YaHei", 10, "bold"),
                        background="#f5f6fa",
                        foreground="#34495e")
        style.configure("Action.TButton",
                        font=("Microsoft YaHei", 10),
                        padding=8)
        style.configure("Primary.TButton",
                        font=("Microsoft YaHei", 10, "bold"),
                        padding=8,
                        background="#3498db",
                        foreground="white")
        style.map("Primary.TButton",
                  background=[("active", "#2980b9")])
        style.configure("Success.TButton",
                        font=("Microsoft YaHei", 10, "bold"),
                        padding=8,
                        background="#27ae60",
                        foreground="white")
        style.map("Success.TButton",
                  background=[("active", "#229954")])
        style.configure("Status.TLabel",
                        font=("Microsoft YaHei", 10),
                        background="#f5f6fa")
        style.configure("Result.TLabel",
                        font=("Consolas", 12, "bold"),
                        background="white",
                        foreground="#2c3e50",
                        padding=10)
        style.configure("CurrentTime.TLabel",
                        font=("Consolas", 14, "bold"),
                        background="#ecf0f1",
                        foreground="#2c3e50",
                        padding=15)

    def _create_widgets(self):
        title_label = ttk.Label(self,
                                text="时间戳转换",
                                style="ToolTitle.TLabel")
        title_label.pack(anchor=tk.W, pady=(0, 15))

        self._create_timestamp_to_datetime_area()
        self._create_datetime_to_timestamp_area()
        self._create_current_time_area()
        self._create_status_area()

    def _create_timestamp_to_datetime_area(self):
        frame = ttk.LabelFrame(self, text="时间戳 → 日期时间", style="Content.TFrame", padding=15)
        frame.pack(fill=tk.X, pady=(0, 15))

        input_frame = ttk.Frame(frame, style="Content.TFrame")
        input_frame.pack(fill=tk.X, pady=(0, 10))

        ts_label = ttk.Label(input_frame, text="时间戳（秒）：", style="SubSection.TLabel")
        ts_label.pack(side=tk.LEFT)

        self.timestamp_entry = ttk.Entry(input_frame, font=("Consolas", 12), width=20)
        self.timestamp_entry.pack(side=tk.LEFT, padx=10)
        self.timestamp_entry.insert(0, str(int(time.time())))
        self.timestamp_entry.bind("<KeyRelease>", lambda e: self._convert_timestamp())
        self.timestamp_entry.bind("<Return>", lambda e: self._convert_timestamp())

        convert_btn = ttk.Button(input_frame,
                                 text="转换",
                                 style="Primary.TButton",
                                 command=self._convert_timestamp)
        convert_btn.pack(side=tk.LEFT, padx=5)

        copy_btn = ttk.Button(input_frame,
                              text="复制结果",
                              style="Action.TButton",
                              command=lambda: self._copy_to_clipboard(self.ts_result_label, "ts_to_dt"))
        copy_btn.pack(side=tk.LEFT, padx=5)

        result_frame = ttk.Frame(frame, style="Content.TFrame")
        result_frame.pack(fill=tk.X)

        result_label = ttk.Label(result_frame, text="转换结果：", style="SubSection.TLabel")
        result_label.pack(anchor=tk.W, pady=(0, 5))

        self.ts_result_label = ttk.Label(result_frame, text="", style="Result.TLabel", anchor=tk.W)
        self.ts_result_label.pack(fill=tk.X)

        self._convert_timestamp()

    def _create_datetime_to_timestamp_area(self):
        frame = ttk.LabelFrame(self, text="日期时间 → 时间戳", style="Content.TFrame", padding=15)
        frame.pack(fill=tk.X, pady=(0, 15))

        dt_frame = ttk.Frame(frame, style="Content.TFrame")
        dt_frame.pack(fill=tk.X, pady=(0, 10))

        dt_label = ttk.Label(dt_frame, text="选择日期时间：", style="SubSection.TLabel")
        dt_label.pack(side=tk.LEFT)

        now = datetime.datetime.now()

        self.year_var = tk.StringVar(value=str(now.year))
        self.month_var = tk.StringVar(value=str(now.month))
        self.day_var = tk.StringVar(value=str(now.day))
        self.hour_var = tk.StringVar(value=str(now.hour))
        self.minute_var = tk.StringVar(value=str(now.minute))
        self.second_var = tk.StringVar(value=str(now.second))

        ttk.Label(dt_frame, text="年", background="#f5f6fa").pack(side=tk.LEFT, padx=(10, 2))
        ttk.Spinbox(dt_frame, from_=1970, to=2100, width=6, textvariable=self.year_var,
                    command=self._convert_datetime).pack(side=tk.LEFT)

        ttk.Label(dt_frame, text="月", background="#f5f6fa").pack(side=tk.LEFT, padx=(10, 2))
        ttk.Spinbox(dt_frame, from_=1, to=12, width=4, textvariable=self.month_var,
                    command=self._convert_datetime).pack(side=tk.LEFT)

        ttk.Label(dt_frame, text="日", background="#f5f6fa").pack(side=tk.LEFT, padx=(10, 2))
        ttk.Spinbox(dt_frame, from_=1, to=31, width=4, textvariable=self.day_var,
                    command=self._convert_datetime).pack(side=tk.LEFT)

        ttk.Label(dt_frame, text="时", background="#f5f6fa").pack(side=tk.LEFT, padx=(10, 2))
        ttk.Spinbox(dt_frame, from_=0, to=23, width=4, textvariable=self.hour_var,
                    command=self._convert_datetime).pack(side=tk.LEFT)

        ttk.Label(dt_frame, text="分", background="#f5f6fa").pack(side=tk.LEFT, padx=(10, 2))
        ttk.Spinbox(dt_frame, from_=0, to=59, width=4, textvariable=self.minute_var,
                    command=self._convert_datetime).pack(side=tk.LEFT)

        ttk.Label(dt_frame, text="秒", background="#f5f6fa").pack(side=tk.LEFT, padx=(10, 2))
        ttk.Spinbox(dt_frame, from_=0, to=59, width=4, textvariable=self.second_var,
                    command=self._convert_datetime).pack(side=tk.LEFT)

        for var in [self.year_var, self.month_var, self.day_var,
                    self.hour_var, self.minute_var, self.second_var]:
            var.trace_add("write", lambda *args: self._convert_datetime())

        btn_frame = ttk.Frame(frame, style="Content.TFrame")
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        convert_btn = ttk.Button(btn_frame,
                                 text="转换",
                                 style="Primary.TButton",
                                 command=self._convert_datetime)
        convert_btn.pack(side=tk.LEFT, padx=5)

        copy_btn = ttk.Button(btn_frame,
                              text="复制结果",
                              style="Action.TButton",
                              command=lambda: self._copy_to_clipboard(self.dt_result_label, "dt_to_ts"))
        copy_btn.pack(side=tk.LEFT, padx=5)

        now_btn = ttk.Button(btn_frame,
                             text="当前时间",
                             style="Success.TButton",
                             command=self._set_current_datetime)
        now_btn.pack(side=tk.LEFT, padx=5)

        result_frame = ttk.Frame(frame, style="Content.TFrame")
        result_frame.pack(fill=tk.X)

        result_label = ttk.Label(result_frame, text="转换结果：", style="SubSection.TLabel")
        result_label.pack(anchor=tk.W, pady=(0, 5))

        self.dt_result_label = ttk.Label(result_frame, text="", style="Result.TLabel", anchor=tk.W)
        self.dt_result_label.pack(fill=tk.X)

        self._convert_datetime()

    def _create_current_time_area(self):
        frame = ttk.LabelFrame(self, text="当前时间", style="Content.TFrame", padding=15)
        frame.pack(fill=tk.X, pady=(0, 15))

        self.current_time_label = ttk.Label(frame, text="", style="CurrentTime.TLabel", anchor=tk.CENTER)
        self.current_time_label.pack(fill=tk.X)

        btn_frame = ttk.Frame(frame, style="Content.TFrame")
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        copy_ts_btn = ttk.Button(btn_frame,
                                 text="复制时间戳",
                                 style="Action.TButton",
                                 command=self._copy_current_timestamp)
        copy_ts_btn.pack(side=tk.LEFT, padx=5)

        copy_dt_btn = ttk.Button(btn_frame,
                                 text="复制日期时间",
                                 style="Action.TButton",
                                 command=self._copy_current_datetime)
        copy_dt_btn.pack(side=tk.LEFT, padx=5)

    def _create_status_area(self):
        status_frame = ttk.Frame(self, style="Content.TFrame")
        status_frame.pack(fill=tk.X, pady=(10, 0))

        self.status_label = ttk.Label(status_frame,
                                      text="就绪",
                                      style="Status.TLabel")
        self.status_label.pack(anchor=tk.W)

    def _convert_timestamp(self):
        try:
            ts_str = self.timestamp_entry.get().strip()
            if not ts_str:
                self.ts_result_label.configure(text="")
                return

            ts = float(ts_str)
            dt = datetime.datetime.fromtimestamp(ts)
            result = dt.strftime("%Y-%m-%d %H:%M:%S")
            self.ts_result_label.configure(text=result)
            self._set_status("转换成功", "success")
        except (ValueError, OSError) as e:
            self.ts_result_label.configure(text="无效的时间戳")
            self._set_status(f"转换失败：{str(e)}", "error")

    def _convert_datetime(self):
        try:
            year = int(self.year_var.get())
            month = int(self.month_var.get())
            day = int(self.day_var.get())
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            second = int(self.second_var.get())

            dt = datetime.datetime(year, month, day, hour, minute, second)
            ts = int(dt.timestamp())
            self.dt_result_label.configure(text=str(ts))
            self._set_status("转换成功", "success")
        except (ValueError, OSError) as e:
            self.dt_result_label.configure(text="无效的日期时间")
            self._set_status(f"转换失败：{str(e)}", "error")

    def _set_current_datetime(self):
        now = datetime.datetime.now()
        self.year_var.set(str(now.year))
        self.month_var.set(str(now.month))
        self.day_var.set(str(now.day))
        self.hour_var.set(str(now.hour))
        self.minute_var.set(str(now.minute))
        self.second_var.set(str(now.second))
        self._convert_datetime()

    def _update_current_timestamp(self):
        now = datetime.datetime.now()
        ts = int(now.timestamp())
        dt_str = now.strftime("%Y-%m-%d %H:%M:%S")
        self.current_time_label.configure(text=f"时间戳：{ts}   |   日期时间：{dt_str}")
        self.after(1000, self._update_current_timestamp)

    def _copy_to_clipboard(self, widget, mode):
        content = widget.cget("text")
        if not content or content in ["无效的时间戳", "无效的日期时间", ""]:
            self._set_status("没有可复制的内容", "warning")
            return

        self.clipboard_clear()
        self.clipboard_append(content)
        self.update()
        self._set_status("已复制到剪贴板", "success")

    def _copy_current_timestamp(self):
        now = int(time.time())
        self.clipboard_clear()
        self.clipboard_append(str(now))
        self.update()
        self._set_status("时间戳已复制到剪贴板", "success")

    def _copy_current_datetime(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.clipboard_clear()
        self.clipboard_append(now)
        self.update()
        self._set_status("日期时间已复制到剪贴板", "success")

    def _set_status(self, message, status_type="info"):
        if not hasattr(self, "status_label"):
            return
        colors = {
            "success": "#27ae60",
            "error": "#e74c3c",
            "warning": "#f39c12",
            "info": "#3498db"
        }
        color = colors.get(status_type, "#34495e")
        self.status_label.configure(text=message, foreground=color)
