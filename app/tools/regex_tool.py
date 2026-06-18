import re
import tkinter as tk
from tkinter import ttk


class RegexTool(ttk.Frame):
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
        style.configure("Success.TButton",
                        font=("Microsoft YaHei", 10, "bold"),
                        padding=8,
                        background="#27ae60",
                        foreground="white")
        style.map("Success.TButton",
                  background=[("active", "#229954")])
        style.configure("Danger.TButton",
                        font=("Microsoft YaHei", 10),
                        padding=8,
                        background="#e74c3c",
                        foreground="white")
        style.map("Danger.TButton",
                  background=[("active", "#c0392b")])
        style.configure("Status.TLabel",
                        font=("Microsoft YaHei", 10),
                        background="#f5f6fa")

    def _create_widgets(self):
        title_label = ttk.Label(self,
                                text="正则测试",
                                style="ToolTitle.TLabel")
        title_label.pack(anchor=tk.W, pady=(0, 15))

        self._create_input_area()
        self._create_button_area()
        self._create_result_area()
        self._create_status_area()

    def _create_input_area(self):
        input_frame = ttk.LabelFrame(self, text="输入", style="Content.TFrame", padding=15)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        regex_frame = ttk.Frame(input_frame, style="Content.TFrame")
        regex_frame.pack(fill=tk.X, pady=(0, 10))

        regex_label = ttk.Label(regex_frame, text="正则表达式：", style="SubSection.TLabel")
        regex_label.pack(side=tk.LEFT)

        self.regex_entry = ttk.Entry(regex_frame, font=("Consolas", 11))
        self.regex_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.regex_entry.insert(0, r"\d+")
        self.regex_entry.bind("<KeyRelease>", lambda e: self._execute_match())
        self.regex_entry.bind("<Return>", lambda e: self._execute_match())

        flags_frame = ttk.Frame(regex_frame, style="Content.TFrame")
        flags_frame.pack(side=tk.LEFT)

        self.ignore_case_var = tk.BooleanVar(value=False)
        self.multiline_var = tk.BooleanVar(value=False)
        self.dotall_var = tk.BooleanVar(value=False)

        ttk.Checkbutton(flags_frame, text="忽略大小写", variable=self.ignore_case_var,
                        command=self._execute_match).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(flags_frame, text="多行模式", variable=self.multiline_var,
                        command=self._execute_match).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(flags_frame, text="点号匹配所有", variable=self.dotall_var,
                        command=self._execute_match).pack(side=tk.LEFT, padx=5)

        test_frame = ttk.Frame(input_frame, style="Content.TFrame")
        test_frame.pack(fill=tk.X, pady=(0, 10))

        test_label = ttk.Label(test_frame, text="测试文本：", style="SubSection.TLabel")
        test_label.pack(anchor=tk.W, pady=(0, 5))

        test_text_container = ttk.Frame(test_frame)
        test_text_container.pack(fill=tk.X)

        self.test_text = tk.Text(test_text_container,
                                 font=("Consolas", 11),
                                 bg="white",
                                 fg="#2c3e50",
                                 insertbackground="#3498db",
                                 selectbackground="#3498db",
                                 selectforeground="white",
                                 wrap=tk.WORD,
                                 height=6,
                                 padx=10,
                                 pady=10,
                                 relief=tk.FLAT,
                                 borderwidth=1,
                                 highlightthickness=1,
                                 highlightbackground="#bdc3c7",
                                 highlightcolor="#3498db")
        self.test_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.test_text.insert(tk.END, "测试文本示例：\n电话号码：13812345678，15987654321\n邮箱：test@example.com, hello@world.org\n价格：¥199.99, $299.50\n日期：2024-01-15, 2023/12/25")
        self.test_text.bind("<KeyRelease>", lambda e: self._execute_match())
        self.test_text.tag_configure("highlight", background="#fff3cd", foreground="#856404")
        self.test_text.tag_configure("highlight_active", background="#ffeeba", foreground="#856404", underline=1)

        test_scrollbar = ttk.Scrollbar(test_text_container,
                                       orient=tk.VERTICAL,
                                       command=self.test_text.yview)
        test_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.test_text.configure(yscrollcommand=test_scrollbar.set)

        replace_frame = ttk.Frame(input_frame, style="Content.TFrame")
        replace_frame.pack(fill=tk.X)

        replace_label = ttk.Label(replace_frame, text="替换文本（可选）：", style="SubSection.TLabel")
        replace_label.pack(side=tk.LEFT)

        self.replace_entry = ttk.Entry(replace_frame, font=("Consolas", 11))
        self.replace_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.replace_entry.bind("<KeyRelease>", lambda e: self._execute_match())
        self.replace_entry.bind("<Return>", lambda e: self._execute_match())

    def _create_button_area(self):
        button_frame = ttk.Frame(self, style="Content.TFrame")
        button_frame.pack(fill=tk.X, pady=(0, 10))

        btn_container = ttk.Frame(button_frame, style="Content.TFrame")
        btn_container.pack(anchor=tk.CENTER)

        match_btn = ttk.Button(btn_container,
                               text="执行匹配",
                               style="Primary.TButton",
                               command=self._execute_match)
        match_btn.pack(side=tk.LEFT, padx=5)

        copy_match_btn = ttk.Button(btn_container,
                                    text="复制匹配结果",
                                    style="Action.TButton",
                                    command=self._copy_match_results)
        copy_match_btn.pack(side=tk.LEFT, padx=5)

        copy_replace_btn = ttk.Button(btn_container,
                                      text="复制替换结果",
                                      style="Success.TButton",
                                      command=self._copy_replace_result)
        copy_replace_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(btn_container,
                               text="清空",
                               style="Danger.TButton",
                               command=self._clear_all)
        clear_btn.pack(side=tk.LEFT, padx=5)

    def _create_result_area(self):
        result_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        result_paned.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self._create_match_list_area(result_paned)
        self._create_replace_preview_area(result_paned)

    def _create_match_list_area(self, parent):
        match_frame = ttk.LabelFrame(parent, text="匹配结果", style="Content.TFrame", padding=10)

        columns = ("index", "content", "start", "end", "groups")
        self.match_tree = ttk.Treeview(match_frame, columns=columns, show="headings", selectmode="browse")
        self.match_tree.heading("index", text="#")
        self.match_tree.heading("content", text="匹配内容")
        self.match_tree.heading("start", text="起始")
        self.match_tree.heading("end", text="结束")
        self.match_tree.heading("groups", text="分组")

        self.match_tree.column("index", width=50, anchor=tk.CENTER)
        self.match_tree.column("content", width=200, anchor=tk.W)
        self.match_tree.column("start", width=60, anchor=tk.CENTER)
        self.match_tree.column("end", width=60, anchor=tk.CENTER)
        self.match_tree.column("groups", width=150, anchor=tk.W)

        tree_scrollbar = ttk.Scrollbar(match_frame, orient=tk.VERTICAL, command=self.match_tree.yview)
        self.match_tree.configure(yscrollcommand=tree_scrollbar.set)

        self.match_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.match_tree.bind("<<TreeviewSelect>>", self._on_match_select)

        parent.add(match_frame, weight=1)

    def _create_replace_preview_area(self, parent):
        replace_frame = ttk.LabelFrame(parent, text="替换预览", style="Content.TFrame", padding=10)

        self.replace_text = tk.Text(replace_frame,
                                    font=("Consolas", 11),
                                    bg="white",
                                    fg="#2c3e50",
                                    insertbackground="#3498db",
                                    selectbackground="#3498db",
                                    selectforeground="white",
                                    wrap=tk.WORD,
                                    padx=10,
                                    pady=10,
                                    relief=tk.FLAT,
                                    borderwidth=1,
                                    highlightthickness=1,
                                    highlightbackground="#bdc3c7",
                                    highlightcolor="#3498db",
                                    state=tk.DISABLED)
        self.replace_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.replace_text.tag_configure("replaced", background="#d4edda", foreground="#155724")

        replace_scrollbar = ttk.Scrollbar(replace_frame,
                                          orient=tk.VERTICAL,
                                          command=self.replace_text.yview)
        replace_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.replace_text.configure(yscrollcommand=replace_scrollbar.set)

        parent.add(replace_frame, weight=1)

    def _create_status_area(self):
        status_frame = ttk.Frame(self, style="Content.TFrame")
        status_frame.pack(fill=tk.X, pady=(10, 0))

        self.status_label = ttk.Label(status_frame,
                                      text="就绪",
                                      style="Status.TLabel")
        self.status_label.pack(anchor=tk.W)

    def _get_flags(self):
        flags = 0
        if self.ignore_case_var.get():
            flags |= re.IGNORECASE
        if self.multiline_var.get():
            flags |= re.MULTILINE
        if self.dotall_var.get():
            flags |= re.DOTALL
        return flags

    def _execute_match(self):
        try:
            pattern = self.regex_entry.get().strip()
            test_content = self.test_text.get("1.0", tk.END)
            replace_content = self.replace_entry.get()

            if not pattern:
                self._clear_matches()
                self._set_status("请输入正则表达式", "warning")
                return

            flags = self._get_flags()
            regex = re.compile(pattern, flags)

            matches = list(regex.finditer(test_content))

            self._update_match_list(matches)
            self._highlight_matches(matches, test_content)
            self._update_replace_preview(regex, test_content, replace_content, matches)

            self._set_status(f"找到 {len(matches)} 个匹配", "success" if matches else "info")

        except re.error as e:
            self._clear_matches()
            self._set_status(f"正则表达式错误：{str(e)}", "error")
        except Exception as e:
            self._clear_matches()
            self._set_status(f"错误：{str(e)}", "error")

    def _update_match_list(self, matches):
        for item in self.match_tree.get_children():
            self.match_tree.delete(item)

        for idx, match in enumerate(matches, 1):
            groups = match.groups()
            groups_str = ", ".join([f"${i+1}={g}" for i, g in enumerate(groups)]) if groups else "-"
            self.match_tree.insert("", tk.END, values=(
                idx,
                match.group(),
                match.start(),
                match.end(),
                groups_str
            ))

    def _highlight_matches(self, matches, content):
        self.test_text.tag_remove("highlight", "1.0", tk.END)
        self.test_text.tag_remove("highlight_active", "1.0", tk.END)

        for match in matches:
            start_pos = self._index_to_pos(content, match.start())
            end_pos = self._index_to_pos(content, match.end())
            self.test_text.tag_add("highlight", start_pos, end_pos)

    def _index_to_pos(self, content, index):
        lines = content[:index].split('\n')
        line = len(lines)
        col = len(lines[-1])
        return f"{line}.{col}"

    def _update_replace_preview(self, regex, test_content, replace_content, matches):
        self.replace_text.configure(state=tk.NORMAL)
        self.replace_text.delete("1.0", tk.END)

        if not replace_content or not matches:
            self.replace_text.insert(tk.END, test_content)
            self.replace_text.configure(state=tk.DISABLED)
            return

        try:
            result = regex.sub(replace_content, test_content)
            self.replace_text.insert(tk.END, result)

            if replace_content:
                try:
                    new_regex = re.compile(re.escape(replace_content), self._get_flags())
                    for match in new_regex.finditer(result):
                        start_pos = self._index_to_pos(result, match.start())
                        end_pos = self._index_to_pos(result, match.end())
                        self.replace_text.tag_add("replaced", start_pos, end_pos)
                except re.error:
                    pass

        except re.error as e:
            self.replace_text.insert(tk.END, f"替换错误：{str(e)}")

        self.replace_text.configure(state=tk.DISABLED)

    def _on_match_select(self, event):
        selection = self.match_tree.selection()
        if not selection:
            return

        item = self.match_tree.item(selection[0])
        values = item["values"]
        if not values:
            return

        start_idx = values[2]
        end_idx = values[3]

        content = self.test_text.get("1.0", tk.END)
        start_pos = self._index_to_pos(content, start_idx)
        end_pos = self._index_to_pos(content, end_idx)

        self.test_text.tag_remove("highlight_active", "1.0", tk.END)
        self.test_text.tag_add("highlight_active", start_pos, end_pos)
        self.test_text.see(start_pos)

    def _clear_matches(self):
        for item in self.match_tree.get_children():
            self.match_tree.delete(item)
        self.test_text.tag_remove("highlight", "1.0", tk.END)
        self.test_text.tag_remove("highlight_active", "1.0", tk.END)
        self.replace_text.configure(state=tk.NORMAL)
        self.replace_text.delete("1.0", tk.END)
        self.replace_text.configure(state=tk.DISABLED)

    def _copy_match_results(self):
        items = self.match_tree.get_children()
        if not items:
            self._set_status("没有可复制的匹配结果", "warning")
            return

        lines = []
        for item in items:
            values = self.match_tree.item(item)["values"]
            lines.append(f"#{values[0]}: {values[1]} (位置: {values[2]}-{values[3]})")

        content = "\n".join(lines)
        self.clipboard_clear()
        self.clipboard_append(content)
        self.update()
        self._set_status("匹配结果已复制到剪贴板", "success")

    def _copy_replace_result(self):
        content = self.replace_text.get("1.0", tk.END).rstrip('\n')
        if not content:
            self._set_status("没有可复制的替换结果", "warning")
            return

        self.clipboard_clear()
        self.clipboard_append(content)
        self.update()
        self._set_status("替换结果已复制到剪贴板", "success")

    def _clear_all(self):
        self.regex_entry.delete(0, tk.END)
        self.test_text.delete("1.0", tk.END)
        self.replace_entry.delete(0, tk.END)
        self.ignore_case_var.set(False)
        self.multiline_var.set(False)
        self.dotall_var.set(False)
        self._clear_matches()
        self._set_status("已清空", "info")

    def _set_status(self, message, status_type="info"):
        colors = {
            "success": "#27ae60",
            "error": "#e74c3c",
            "warning": "#f39c12",
            "info": "#3498db"
        }
        color = colors.get(status_type, "#34495e")
        self.status_label.configure(text=message, foreground=color)
