import hashlib
import uuid
import tkinter as tk
from tkinter import ttk


class HashTool(ttk.Frame):
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
        style.configure("Status.TLabel",
                        font=("Microsoft YaHei", 10),
                        background="#f5f6fa")
        style.configure("Result.TLabel",
                        font=("Consolas", 12),
                        background="white",
                        foreground="#2c3e50",
                        padding=10)
        style.configure("TRadiobutton",
                        font=("Microsoft YaHei", 10),
                        background="#f5f6fa",
                        foreground="#34495e")

    def _create_widgets(self):
        title_label = ttk.Label(self,
                                text="哈希计算",
                                style="ToolTitle.TLabel")
        title_label.pack(anchor=tk.W, pady=(0, 15))

        self._create_hash_area()
        self._create_uuid_area()
        self._create_status_area()

    def _create_hash_area(self):
        hash_frame = ttk.LabelFrame(self, text="哈希计算", style="Content.TFrame", padding=15)
        hash_frame.pack(fill=tk.X, pady=(0, 15))

        input_label = ttk.Label(hash_frame,
                                text="输入内容：",
                                style="Section.TLabel")
        input_label.pack(anchor=tk.W, pady=(0, 5))

        input_container = ttk.Frame(hash_frame)
        input_container.pack(fill=tk.X)

        self.hash_input = tk.Text(input_container,
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
                                  height=6)
        self.hash_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        input_scrollbar = ttk.Scrollbar(input_container,
                                        orient=tk.VERTICAL,
                                        command=self.hash_input.yview)
        input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.hash_input.configure(yscrollcommand=input_scrollbar.set)

        algo_frame = ttk.Frame(hash_frame, style="Content.TFrame")
        algo_frame.pack(fill=tk.X, pady=15)

        algo_label = ttk.Label(algo_frame,
                               text="选择算法：",
                               style="SubSection.TLabel")
        algo_label.pack(side=tk.LEFT)

        self.hash_algorithm = tk.StringVar(value="SHA256")

        algorithms = ["MD5", "SHA1", "SHA256", "SHA512"]
        for algo in algorithms:
            radio = ttk.Radiobutton(algo_frame,
                                    text=algo,
                                    value=algo,
                                    variable=self.hash_algorithm,
                                    command=self._calculate_hash)
            radio.pack(side=tk.LEFT, padx=15)

        output_frame = ttk.Frame(hash_frame, style="Content.TFrame")
        output_frame.pack(fill=tk.X)

        output_label = ttk.Label(output_frame,
                                 text="哈希结果：",
                                 style="Section.TLabel")
        output_label.pack(anchor=tk.W, pady=(0, 5))

        result_container = ttk.Frame(output_frame)
        result_container.pack(fill=tk.X)

        self.hash_result = ttk.Label(result_container,
                                     text="",
                                     style="Result.TLabel",
                                     anchor=tk.W)
        self.hash_result.pack(side=tk.LEFT, fill=tk.X, expand=True)

        copy_btn = ttk.Button(result_container,
                              text="复制",
                              style="Action.TButton",
                              width=8,
                              command=self._copy_hash)
        copy_btn.pack(side=tk.LEFT, padx=(10, 0))

        self.hash_input.bind("<KeyRelease>", lambda e: self._calculate_hash())

    def _create_uuid_area(self):
        uuid_frame = ttk.LabelFrame(self, text="UUID 生成", style="Content.TFrame", padding=15)
        uuid_frame.pack(fill=tk.X, pady=(0, 15))

        self.recent_uuids = []

        generate_btn = ttk.Button(uuid_frame,
                                  text="生成 UUID",
                                  style="Success.TButton",
                                  command=self._generate_uuid)
        generate_btn.pack(anchor=tk.W, pady=(0, 15))

        list_label = ttk.Label(uuid_frame,
                               text="最近生成的 UUID（最多 5 个）：",
                               style="SubSection.TLabel")
        list_label.pack(anchor=tk.W, pady=(0, 10))

        self.uuid_list_frame = ttk.Frame(uuid_frame, style="Content.TFrame")
        self.uuid_list_frame.pack(fill=tk.X)

        self.uuid_widgets = []
        for i in range(5):
            row_frame = ttk.Frame(self.uuid_list_frame, style="Content.TFrame")
            row_frame.pack(fill=tk.X, pady=3)

            uuid_label = ttk.Label(row_frame,
                                   text="",
                                   font=("Consolas", 11),
                                   background="white",
                                   foreground="#7f8c8d",
                                   padding=8,
                                   anchor=tk.W)
            uuid_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

            copy_btn = ttk.Button(row_frame,
                                  text="复制",
                                  style="Action.TButton",
                                  width=8,
                                  command=lambda idx=i: self._copy_uuid(idx))
            copy_btn.pack(side=tk.LEFT, padx=(10, 0))

            self.uuid_widgets.append((uuid_label, copy_btn))

    def _create_status_area(self):
        status_frame = ttk.Frame(self, style="Content.TFrame")
        status_frame.pack(fill=tk.X, pady=(10, 0))

        self.status_label = ttk.Label(status_frame,
                                      text="就绪",
                                      style="Status.TLabel")
        self.status_label.pack(anchor=tk.W)

    def _calculate_hash(self):
        try:
            input_text = self.hash_input.get("1.0", tk.END).rstrip("\n")
            if not input_text:
                self.hash_result.configure(text="")
                self._set_status("请输入内容", "info")
                return

            algorithm = self.hash_algorithm.get().lower()

            if algorithm == "md5":
                hash_obj = hashlib.md5()
            elif algorithm == "sha1":
                hash_obj = hashlib.sha1()
            elif algorithm == "sha256":
                hash_obj = hashlib.sha256()
            elif algorithm == "sha512":
                hash_obj = hashlib.sha512()
            else:
                self._set_status("未知的哈希算法", "error")
                return

            hash_obj.update(input_text.encode("utf-8"))
            hash_result = hash_obj.hexdigest()

            self.hash_result.configure(text=hash_result, foreground="#2c3e50")
            self._set_status(f"{self.hash_algorithm.get()} 计算完成", "success")
        except Exception as e:
            self.hash_result.configure(text="计算失败", foreground="#e74c3c")
            self._set_status(f"计算失败：{str(e)}", "error")

    def _copy_hash(self):
        content = self.hash_result.cget("text")
        if not content or content in ["", "计算失败"]:
            self._set_status("没有可复制的内容", "warning")
            return

        self.clipboard_clear()
        self.clipboard_append(content)
        self.update()
        self._set_status("哈希值已复制到剪贴板", "success")

    def _generate_uuid(self):
        try:
            new_uuid = str(uuid.uuid4())
            self.recent_uuids.insert(0, new_uuid)
            if len(self.recent_uuids) > 5:
                self.recent_uuids.pop()

            self._refresh_uuid_list()
            self._set_status("UUID 生成成功", "success")
        except Exception as e:
            self._set_status(f"生成失败：{str(e)}", "error")

    def _refresh_uuid_list(self):
        for i in range(5):
            label, btn = self.uuid_widgets[i]
            if i < len(self.recent_uuids):
                label.configure(text=self.recent_uuids[i], foreground="#2c3e50")
                btn.configure(state="normal")
            else:
                label.configure(text="", foreground="#7f8c8d")
                btn.configure(state="disabled")

    def _copy_uuid(self, index):
        if index >= len(self.recent_uuids):
            self._set_status("没有可复制的内容", "warning")
            return

        content = self.recent_uuids[index]
        self.clipboard_clear()
        self.clipboard_append(content)
        self.update()
        self._set_status("UUID 已复制到剪贴板", "success")

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
