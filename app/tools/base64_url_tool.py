import base64
import urllib.parse
import tkinter as tk
from tkinter import ttk


class Base64UrlTool(ttk.Frame):
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
        style.configure("TNotebook",
                        background="#f5f6fa",
                        borderwidth=0)
        style.configure("TNotebook.Tab",
                        font=("Microsoft YaHei", 11, "bold"),
                        padding=(20, 10),
                        background="#ecf0f1",
                        foreground="#34495e")
        style.map("TNotebook.Tab",
                  background=[("selected", "#ffffff")],
                  foreground=[("selected", "#2c3e50")])

    def _create_widgets(self):
        title_label = ttk.Label(self,
                                text="Base64 / URL 编解码",
                                style="ToolTitle.TLabel")
        title_label.pack(anchor=tk.W, pady=(0, 15))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self._create_base64_tab()
        self._create_url_tab()

        self._create_status_area()

    def _create_base64_tab(self):
        base64_frame = ttk.Frame(self.notebook, style="Content.TFrame", padding=15)
        self.notebook.add(base64_frame, text="  Base64 编解码  ")

        input_label = ttk.Label(base64_frame,
                                text="输入原文：",
                                style="Section.TLabel")
        input_label.pack(anchor=tk.W, pady=(0, 5))

        text_container = ttk.Frame(base64_frame)
        text_container.pack(fill=tk.BOTH, expand=True)

        self.base64_input = tk.Text(text_container,
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
        self.base64_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        input_scrollbar = ttk.Scrollbar(text_container,
                                        orient=tk.VERTICAL,
                                        command=self.base64_input.yview)
        input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.base64_input.configure(yscrollcommand=input_scrollbar.set)

        btn_frame = ttk.Frame(base64_frame, style="Content.TFrame")
        btn_frame.pack(fill=tk.X, pady=15)

        btn_container = ttk.Frame(btn_frame, style="Content.TFrame")
        btn_container.pack(anchor=tk.CENTER)

        encode_btn = ttk.Button(btn_container,
                                text="编码",
                                style="Primary.TButton",
                                command=self._base64_encode)
        encode_btn.pack(side=tk.LEFT, padx=5)

        decode_btn = ttk.Button(btn_container,
                                text="解码",
                                style="Success.TButton",
                                command=self._base64_decode)
        decode_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(btn_container,
                               text="清空",
                               style="Danger.TButton",
                               command=self._clear_base64)
        clear_btn.pack(side=tk.LEFT, padx=5)

        output_label = ttk.Label(base64_frame,
                                 text="输出结果：",
                                 style="Section.TLabel")
        output_label.pack(anchor=tk.W, pady=(0, 5))

        output_container = ttk.Frame(base64_frame)
        output_container.pack(fill=tk.BOTH, expand=True)

        self.base64_output = tk.Text(output_container,
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
        self.base64_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        output_scrollbar = ttk.Scrollbar(output_container,
                                         orient=tk.VERTICAL,
                                         command=self.base64_output.yview)
        output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.base64_output.configure(yscrollcommand=output_scrollbar.set)

        copy_btn = ttk.Button(base64_frame,
                              text="复制结果",
                              style="Action.TButton",
                              command=lambda: self._copy_result(self.base64_output, "Base64"))
        copy_btn.pack(anchor=tk.E, pady=(10, 0))

    def _create_url_tab(self):
        url_frame = ttk.Frame(self.notebook, style="Content.TFrame", padding=15)
        self.notebook.add(url_frame, text="  URL 编解码  ")

        input_label = ttk.Label(url_frame,
                                text="输入原文：",
                                style="Section.TLabel")
        input_label.pack(anchor=tk.W, pady=(0, 5))

        text_container = ttk.Frame(url_frame)
        text_container.pack(fill=tk.BOTH, expand=True)

        self.url_input = tk.Text(text_container,
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
        self.url_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        input_scrollbar = ttk.Scrollbar(text_container,
                                        orient=tk.VERTICAL,
                                        command=self.url_input.yview)
        input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.url_input.configure(yscrollcommand=input_scrollbar.set)

        btn_frame = ttk.Frame(url_frame, style="Content.TFrame")
        btn_frame.pack(fill=tk.X, pady=15)

        btn_container = ttk.Frame(btn_frame, style="Content.TFrame")
        btn_container.pack(anchor=tk.CENTER)

        encode_btn = ttk.Button(btn_container,
                                text="编码",
                                style="Primary.TButton",
                                command=self._url_encode)
        encode_btn.pack(side=tk.LEFT, padx=5)

        decode_btn = ttk.Button(btn_container,
                                text="解码",
                                style="Success.TButton",
                                command=self._url_decode)
        decode_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(btn_container,
                               text="清空",
                               style="Danger.TButton",
                               command=self._clear_url)
        clear_btn.pack(side=tk.LEFT, padx=5)

        output_label = ttk.Label(url_frame,
                                 text="输出结果：",
                                 style="Section.TLabel")
        output_label.pack(anchor=tk.W, pady=(0, 5))

        output_container = ttk.Frame(url_frame)
        output_container.pack(fill=tk.BOTH, expand=True)

        self.url_output = tk.Text(output_container,
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
        self.url_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        output_scrollbar = ttk.Scrollbar(output_container,
                                         orient=tk.VERTICAL,
                                         command=self.url_output.yview)
        output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.url_output.configure(yscrollcommand=output_scrollbar.set)

        copy_btn = ttk.Button(url_frame,
                              text="复制结果",
                              style="Action.TButton",
                              command=lambda: self._copy_result(self.url_output, "URL"))
        copy_btn.pack(anchor=tk.E, pady=(10, 0))

    def _create_status_area(self):
        status_frame = ttk.Frame(self, style="Content.TFrame")
        status_frame.pack(fill=tk.X, pady=(10, 0))

        self.status_label = ttk.Label(status_frame,
                                      text="就绪",
                                      style="Status.TLabel")
        self.status_label.pack(anchor=tk.W)

    def _base64_encode(self):
        try:
            input_text = self.base64_input.get("1.0", tk.END).rstrip("\n")
            if not input_text:
                self._set_status("输入内容为空", "warning")
                return

            encoded_bytes = base64.b64encode(input_text.encode("utf-8"))
            encoded_text = encoded_bytes.decode("utf-8")
            self.base64_output.delete("1.0", tk.END)
            self.base64_output.insert("1.0", encoded_text)
            self._set_status("Base64 编码成功", "success")
        except Exception as e:
            self._set_status(f"编码失败：{str(e)}", "error")

    def _base64_decode(self):
        try:
            input_text = self.base64_input.get("1.0", tk.END).rstrip("\n")
            if not input_text:
                self._set_status("输入内容为空", "warning")
                return

            decoded_bytes = base64.b64decode(input_text.encode("utf-8"))
            decoded_text = decoded_bytes.decode("utf-8")
            self.base64_output.delete("1.0", tk.END)
            self.base64_output.insert("1.0", decoded_text)
            self._set_status("Base64 解码成功", "success")
        except Exception as e:
            self._set_status(f"解码失败：{str(e)}", "error")

    def _url_encode(self):
        try:
            input_text = self.url_input.get("1.0", tk.END).rstrip("\n")
            if not input_text:
                self._set_status("输入内容为空", "warning")
                return

            encoded_text = urllib.parse.quote(input_text, safe="")
            self.url_output.delete("1.0", tk.END)
            self.url_output.insert("1.0", encoded_text)
            self._set_status("URL 编码成功", "success")
        except Exception as e:
            self._set_status(f"编码失败：{str(e)}", "error")

    def _url_decode(self):
        try:
            input_text = self.url_input.get("1.0", tk.END).rstrip("\n")
            if not input_text:
                self._set_status("输入内容为空", "warning")
                return

            decoded_text = urllib.parse.unquote(input_text)
            self.url_output.delete("1.0", tk.END)
            self.url_output.insert("1.0", decoded_text)
            self._set_status("URL 解码成功", "success")
        except Exception as e:
            self._set_status(f"解码失败：{str(e)}", "error")

    def _copy_result(self, text_widget, tool_name):
        content = text_widget.get("1.0", tk.END).strip()
        if not content:
            self._set_status("没有可复制的内容", "warning")
            return

        self.clipboard_clear()
        self.clipboard_append(content)
        self.update()
        self._set_status(f"{tool_name} 结果已复制到剪贴板", "success")

    def _clear_base64(self):
        self.base64_input.delete("1.0", tk.END)
        self.base64_output.delete("1.0", tk.END)
        self._set_status("已清空", "info")

    def _clear_url(self):
        self.url_input.delete("1.0", tk.END)
        self.url_output.delete("1.0", tk.END)
        self._set_status("已清空", "info")

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
