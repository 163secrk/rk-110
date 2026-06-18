import json
import tkinter as tk
from tkinter import ttk, messagebox


class JsonTool(ttk.Frame):
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
        style.configure("Warning.TButton",
                        font=("Microsoft YaHei", 10),
                        padding=8,
                        background="#f39c12",
                        foreground="white")
        style.map("Warning.TButton",
                  background=[("active", "#d68910")])
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
                                text="JSON 格式化校验",
                                style="ToolTitle.TLabel")
        title_label.pack(anchor=tk.W, pady=(0, 15))

        main_paned = ttk.PanedWindow(self, orient=tk.VERTICAL)
        main_paned.pack(fill=tk.BOTH, expand=True)

        self._create_input_area(main_paned)
        self._create_button_area(main_paned)
        self._create_output_area(main_paned)
        self._create_status_area()

    def _create_input_area(self, parent):
        input_frame = ttk.Frame(parent, style="Content.TFrame")

        input_label = ttk.Label(input_frame,
                                text="输入 JSON：",
                                style="Section.TLabel")
        input_label.pack(anchor=tk.W, pady=(0, 5))

        text_container = ttk.Frame(input_frame)
        text_container.pack(fill=tk.BOTH, expand=True)

        self.input_text = tk.Text(text_container,
                                  font=("Consolas", 11),
                                  bg="white",
                                  fg="#2c3e50",
                                  insertbackground="#3498db",
                                  selectbackground="#3498db",
                                  selectforeground="white",
                                  wrap=tk.NONE,
                                  padx=10,
                                  pady=10,
                                  relief=tk.FLAT,
                                  borderwidth=1,
                                  highlightthickness=1,
                                  highlightbackground="#bdc3c7",
                                  highlightcolor="#3498db")
        self.input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        input_scrollbar = ttk.Scrollbar(text_container,
                                        orient=tk.VERTICAL,
                                        command=self.input_text.yview)
        input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.input_text.configure(yscrollcommand=input_scrollbar.set)

        input_hscrollbar = ttk.Scrollbar(input_frame,
                                         orient=tk.HORIZONTAL,
                                         command=self.input_text.xview)
        input_hscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.input_text.configure(xscrollcommand=input_hscrollbar.set)

        self.input_text.insert(tk.END, '{\n  "name": "开发者工具箱",\n  "version": "1.0.0",\n  "features": ["JSON格式化", "JSON校验"]\n}')

        parent.add(input_frame, weight=3)

    def _create_button_area(self, parent):
        button_frame = ttk.Frame(parent, style="Content.TFrame")
        button_frame.pack(fill=tk.X, pady=15)

        btn_container = ttk.Frame(button_frame, style="Content.TFrame")
        btn_container.pack(anchor=tk.CENTER)

        format_btn = ttk.Button(btn_container,
                                text="格式化",
                                style="Primary.TButton",
                                command=self._format_json)
        format_btn.pack(side=tk.LEFT, padx=5)

        compress_btn = ttk.Button(btn_container,
                                  text="压缩",
                                  style="Action.TButton",
                                  command=self._compress_json)
        compress_btn.pack(side=tk.LEFT, padx=5)

        validate_btn = ttk.Button(btn_container,
                                  text="校验",
                                  style="Success.TButton",
                                  command=self._validate_json)
        validate_btn.pack(side=tk.LEFT, padx=5)

        copy_btn = ttk.Button(btn_container,
                              text="复制结果",
                              style="Action.TButton",
                              command=self._copy_result)
        copy_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(btn_container,
                               text="清空",
                               style="Danger.TButton",
                               command=self._clear_all)
        clear_btn.pack(side=tk.LEFT, padx=5)

    def _create_output_area(self, parent):
        output_frame = ttk.Frame(parent, style="Content.TFrame")

        output_label = ttk.Label(output_frame,
                                 text="输出结果：",
                                 style="Section.TLabel")
        output_label.pack(anchor=tk.W, pady=(0, 5))

        text_container = ttk.Frame(output_frame)
        text_container.pack(fill=tk.BOTH, expand=True)

        self.output_text = tk.Text(text_container,
                                   font=("Consolas", 11),
                                   bg="white",
                                   fg="#2c3e50",
                                   insertbackground="#3498db",
                                   selectbackground="#3498db",
                                   selectforeground="white",
                                   wrap=tk.NONE,
                                   padx=10,
                                   pady=10,
                                   relief=tk.FLAT,
                                   borderwidth=1,
                                   highlightthickness=1,
                                   highlightbackground="#bdc3c7",
                                   highlightcolor="#3498db",
                                   state=tk.DISABLED)
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        output_scrollbar = ttk.Scrollbar(text_container,
                                         orient=tk.VERTICAL,
                                         command=self.output_text.yview)
        output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.configure(yscrollcommand=output_scrollbar.set)

        output_hscrollbar = ttk.Scrollbar(output_frame,
                                          orient=tk.HORIZONTAL,
                                          command=self.output_text.xview)
        output_hscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.output_text.configure(xscrollcommand=output_hscrollbar.set)

        parent.add(output_frame, weight=3)

    def _create_status_area(self):
        status_frame = ttk.Frame(self, style="Content.TFrame")
        status_frame.pack(fill=tk.X, pady=(10, 0))

        self.status_label = ttk.Label(status_frame,
                                      text="就绪",
                                      style="Status.TLabel")
        self.status_label.pack(anchor=tk.W)

    def _parse_json(self):
        try:
            input_content = self.input_text.get("1.0", tk.END).strip()
            if not input_content:
                raise ValueError("输入内容为空")
            return json.loads(input_content)
        except json.JSONDecodeError as e:
            self._set_status(f"JSON 格式错误：第 {e.lineno} 行，第 {e.colno} 列 - {e.msg}", "error")
            messagebox.showerror("JSON 解析错误",
                                 f"格式错误\n\n位置：第 {e.lineno} 行，第 {e.colno} 列\n错误：{e.msg}")
            return None
        except ValueError as e:
            self._set_status(str(e), "error")
            messagebox.showwarning("提示", str(e))
            return None

    def _format_json(self):
        data = self._parse_json()
        if data is None:
            return

        formatted = json.dumps(data, ensure_ascii=False, indent=2)
        self._set_output(formatted)
        self._set_status("格式化成功", "success")

    def _compress_json(self):
        data = self._parse_json()
        if data is None:
            return

        compressed = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        self._set_output(compressed)
        self._set_status("压缩成功", "success")

    def _validate_json(self):
        data = self._parse_json()
        if data is None:
            return

        formatted = json.dumps(data, ensure_ascii=False, indent=2)
        self._set_output(formatted)
        self._set_status("JSON 格式正确，校验通过", "success")
        messagebox.showinfo("校验通过", "JSON 格式正确！")

    def _copy_result(self):
        content = self.output_text.get("1.0", tk.END).strip()
        if not content:
            self._set_status("没有可复制的内容", "warning")
            return

        self.clipboard_clear()
        self.clipboard_append(content)
        self.update()
        self._set_status("已复制到剪贴板", "success")

    def _clear_all(self):
        self.input_text.delete("1.0", tk.END)
        self._set_output("")
        self._set_status("已清空", "info")

    def _set_output(self, content):
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", content)
        self.output_text.configure(state=tk.DISABLED)

    def _set_status(self, message, status_type="info"):
        colors = {
            "success": "#27ae60",
            "error": "#e74c3c",
            "warning": "#f39c12",
            "info": "#3498db"
        }
        color = colors.get(status_type, "#34495e")
        self.status_label.configure(text=message, foreground=color)
