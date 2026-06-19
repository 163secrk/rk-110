import tkinter as tk
from tkinter import ttk, scrolledtext
import difflib


class TextDiffTool(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, style="Content.TFrame")
        self._setup_styles()
        self._create_widgets()

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
        style.configure("Status.TLabel",
                        font=("Microsoft YaHei", 10),
                        background="#f5f6fa")
        style.configure("Stat.TLabel",
                        font=("Microsoft YaHei", 10, "bold"),
                        background="#f5f6fa",
                        padding=(10, 5))

    def _create_widgets(self):
        title_label = ttk.Label(self,
                                text="文本比对",
                                style="ToolTitle.TLabel")
        title_label.pack(anchor=tk.W, pady=(0, 15))

        self._create_input_area()
        self._create_button_area()
        self._create_stat_area()
        self._create_result_area()
        self._create_status_area()

    def _create_input_area(self):
        input_frame = ttk.Frame(self, style="Content.TFrame")
        input_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 10))

        left_frame = ttk.Frame(input_frame, style="Content.TFrame")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        left_label = ttk.Label(left_frame, text="原始文本", style="Section.TLabel")
        left_label.pack(anchor=tk.W, pady=(0, 5))

        self.original_text = scrolledtext.ScrolledText(
            left_frame,
            font=("Consolas", 11),
            height=12,
            wrap=tk.NONE,
            bg="white",
            fg="#2c3e50",
            insertbackground="#2c3e50",
            relief=tk.SOLID,
            borderwidth=1
        )
        self.original_text.pack(fill=tk.BOTH, expand=True)

        right_frame = ttk.Frame(input_frame, style="Content.TFrame")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        right_label = ttk.Label(right_frame, text="对比文本", style="Section.TLabel")
        right_label.pack(anchor=tk.W, pady=(0, 5))

        self.compare_text = scrolledtext.ScrolledText(
            right_frame,
            font=("Consolas", 11),
            height=12,
            wrap=tk.NONE,
            bg="white",
            fg="#2c3e50",
            insertbackground="#2c3e50",
            relief=tk.SOLID,
            borderwidth=1
        )
        self.compare_text.pack(fill=tk.BOTH, expand=True)

    def _create_button_area(self):
        btn_frame = ttk.Frame(self, style="Content.TFrame")
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        diff_btn = ttk.Button(btn_frame,
                              text="比对",
                              style="Primary.TButton",
                              command=self._do_diff)
        diff_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(btn_frame,
                               text="清空",
                               style="Action.TButton",
                               command=self._clear_all)
        clear_btn.pack(side=tk.LEFT, padx=5)

        swap_btn = ttk.Button(btn_frame,
                              text="交换文本",
                              style="Action.TButton",
                              command=self._swap_texts)
        swap_btn.pack(side=tk.LEFT, padx=5)

    def _create_stat_area(self):
        stat_frame = ttk.Frame(self, style="Content.TFrame")
        stat_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(stat_frame, text="统计：", style="SubSection.TLabel").pack(side=tk.LEFT)

        self.added_stat = ttk.Label(stat_frame, text="新增: 0 行", style="Stat.TLabel",
                                    foreground="#27ae60")
        self.added_stat.pack(side=tk.LEFT, padx=(10, 0))

        self.removed_stat = ttk.Label(stat_frame, text="删除: 0 行", style="Stat.TLabel",
                                      foreground="#e74c3c")
        self.removed_stat.pack(side=tk.LEFT, padx=(15, 0))

        self.unchanged_stat = ttk.Label(stat_frame, text="不变: 0 行", style="Stat.TLabel",
                                        foreground="#7f8c8d")
        self.unchanged_stat.pack(side=tk.LEFT, padx=(15, 0))

    def _create_result_area(self):
        result_frame = ttk.LabelFrame(self, text="比对结果", style="Content.TFrame", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.result_text = scrolledtext.ScrolledText(
            result_frame,
            font=("Consolas", 11),
            wrap=tk.NONE,
            bg="white",
            fg="#2c3e50",
            relief=tk.SOLID,
            borderwidth=1,
            state=tk.DISABLED
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)

        self.result_text.tag_configure("added", background="#d5f5e3", foreground="#1e8449")
        self.result_text.tag_configure("removed", background="#fadbd8", foreground="#c0392b")
        self.result_text.tag_configure("unchanged", background="white", foreground="#2c3e50")
        self.result_text.tag_configure("linenum", foreground="#95a5a6", font=("Consolas", 10))

    def _create_status_area(self):
        status_frame = ttk.Frame(self, style="Content.TFrame")
        status_frame.pack(fill=tk.X, pady=(5, 0))

        self.status_label = ttk.Label(status_frame,
                                      text="就绪",
                                      style="Status.TLabel")
        self.status_label.pack(anchor=tk.W)

    def _do_diff(self):
        try:
            original = self.original_text.get("1.0", tk.END).splitlines()
            compare = self.compare_text.get("1.0", tk.END).splitlines()

            while original and original[-1] == "":
                original.pop()
            while compare and compare[-1] == "":
                compare.pop()

            matcher = difflib.SequenceMatcher(None, original, compare)

            added_count = 0
            removed_count = 0
            unchanged_count = 0

            result_lines = []

            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == "equal":
                    for idx in range(i2 - i1):
                        line_num = i1 + idx + 1
                        line_content = original[i1 + idx]
                        result_lines.append(("unchanged", line_num, line_content))
                    unchanged_count += (i2 - i1)
                elif tag == "delete":
                    for idx in range(i2 - i1):
                        line_num = i1 + idx + 1
                        line_content = original[i1 + idx]
                        result_lines.append(("removed", line_num, line_content))
                    removed_count += (i2 - i1)
                elif tag == "insert":
                    for idx in range(j2 - j1):
                        line_num = j1 + idx + 1
                        line_content = compare[j1 + idx]
                        result_lines.append(("added", line_num, line_content))
                    added_count += (j2 - j1)
                elif tag == "replace":
                    for idx in range(i2 - i1):
                        line_num = i1 + idx + 1
                        line_content = original[i1 + idx]
                        result_lines.append(("removed", line_num, line_content))
                    removed_count += (i2 - i1)
                    for idx in range(j2 - j1):
                        line_num = j1 + idx + 1
                        line_content = compare[j1 + idx]
                        result_lines.append(("added", line_num, line_content))
                    added_count += (j2 - j1)

            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete("1.0", tk.END)

            for tag, line_num, content in result_lines:
                line_num_str = f"{line_num:4d}  "
                self.result_text.insert(tk.END, line_num_str, "linenum")
                self.result_text.insert(tk.END, content + "\n", tag)

            self.result_text.config(state=tk.DISABLED)

            self.added_stat.configure(text=f"新增: {added_count} 行")
            self.removed_stat.configure(text=f"删除: {removed_count} 行")
            self.unchanged_stat.configure(text=f"不变: {unchanged_count} 行")

            total = len(original)
            self._set_status(f"比对完成，原始文本共 {total} 行", "success")

        except Exception as e:
            self._set_status(f"比对失败：{str(e)}", "error")

    def _clear_all(self):
        self.original_text.delete("1.0", tk.END)
        self.compare_text.delete("1.0", tk.END)
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.config(state=tk.DISABLED)
        self.added_stat.configure(text="新增: 0 行")
        self.removed_stat.configure(text="删除: 0 行")
        self.unchanged_stat.configure(text="不变: 0 行")
        self._set_status("已清空", "info")

    def _swap_texts(self):
        original = self.original_text.get("1.0", tk.END)
        compare = self.compare_text.get("1.0", tk.END)
        self.original_text.delete("1.0", tk.END)
        self.original_text.insert("1.0", compare)
        self.compare_text.delete("1.0", tk.END)
        self.compare_text.insert("1.0", original)
        self._set_status("已交换文本", "info")

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
