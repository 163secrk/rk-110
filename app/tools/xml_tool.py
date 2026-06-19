import tkinter as tk
from tkinter import ttk, messagebox
import xml.etree.ElementTree as ET
from xml.dom import minidom
import re


class XMLTool(ttk.Frame):
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

    def _create_widgets(self):
        title_label = ttk.Label(self,
                                text="XML 格式化校验",
                                style="ToolTitle.TLabel")
        title_label.pack(anchor=tk.W, pady=(0, 15))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self._create_format_tab()
        self._create_validate_tab()

    def _create_format_tab(self):
        format_frame = ttk.Frame(self.notebook, style="Content.TFrame")
        self.notebook.add(format_frame, text="格式化")

        paned = ttk.PanedWindow(format_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(paned, style="Content.TFrame")
        left_label = ttk.Label(left_frame, text="XML 原文：", style="Section.TLabel")
        left_label.pack(anchor=tk.W, pady=(0, 5))

        left_text_container = ttk.Frame(left_frame)
        left_text_container.pack(fill=tk.BOTH, expand=True)

        self.format_input_text = tk.Text(left_text_container,
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
        self.format_input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        left_scrollbar_y = ttk.Scrollbar(left_text_container,
                                         orient=tk.VERTICAL,
                                         command=self.format_input_text.yview)
        left_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.format_input_text.configure(yscrollcommand=left_scrollbar_y.set)

        left_scrollbar_x = ttk.Scrollbar(left_frame,
                                         orient=tk.HORIZONTAL,
                                         command=self.format_input_text.xview)
        left_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.format_input_text.configure(xscrollcommand=left_scrollbar_x.set)

        self.format_input_text.insert(tk.END, '<?xml version="1.0" encoding="UTF-8"?><root><name>开发者工具箱</name><version>1.0.0</version><features><feature>XML格式化</feature><feature>XML校验</feature></features></root>')

        paned.add(left_frame, weight=1)

        right_frame = ttk.Frame(paned, style="Content.TFrame")
        right_label = ttk.Label(right_frame, text="格式化结果：", style="Section.TLabel")
        right_label.pack(anchor=tk.W, pady=(0, 5))

        right_btn_frame = ttk.Frame(right_frame, style="Content.TFrame")
        right_btn_frame.pack(fill=tk.X, pady=(0, 5))

        format_btn = ttk.Button(right_btn_frame,
                                text="格式化",
                                style="Primary.TButton",
                                command=self._format_xml)
        format_btn.pack(side=tk.LEFT, padx=(0, 5))

        copy_btn = ttk.Button(right_btn_frame,
                              text="复制结果",
                              style="Action.TButton",
                              command=self._copy_format_result)
        copy_btn.pack(side=tk.LEFT)

        clear_btn = ttk.Button(right_btn_frame,
                               text="清空",
                               style="Danger.TButton",
                               command=self._clear_format)
        clear_btn.pack(side=tk.RIGHT)

        right_text_container = ttk.Frame(right_frame)
        right_text_container.pack(fill=tk.BOTH, expand=True)

        self.format_output_text = tk.Text(right_text_container,
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
        self.format_output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right_scrollbar_y = ttk.Scrollbar(right_text_container,
                                          orient=tk.VERTICAL,
                                          command=self.format_output_text.yview)
        right_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.format_output_text.configure(yscrollcommand=right_scrollbar_y.set)

        right_scrollbar_x = ttk.Scrollbar(right_frame,
                                          orient=tk.HORIZONTAL,
                                          command=self.format_output_text.xview)
        right_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.format_output_text.configure(xscrollcommand=right_scrollbar_x.set)

        paned.add(right_frame, weight=1)

        self.format_status_label = ttk.Label(format_frame, text="就绪", style="Status.TLabel")
        self.format_status_label.pack(anchor=tk.W, pady=(10, 0))

    def _create_validate_tab(self):
        validate_frame = ttk.Frame(self.notebook, style="Content.TFrame")
        self.notebook.add(validate_frame, text="校验")

        input_label = ttk.Label(validate_frame, text="XML 字符串：", style="Section.TLabel")
        input_label.pack(anchor=tk.W, pady=(0, 5))

        btn_frame = ttk.Frame(validate_frame, style="Content.TFrame")
        btn_frame.pack(fill=tk.X, pady=(0, 5))

        validate_btn = ttk.Button(btn_frame,
                                  text="校验",
                                  style="Success.TButton",
                                  command=self._validate_xml)
        validate_btn.pack(side=tk.LEFT, padx=(0, 5))

        clear_btn = ttk.Button(btn_frame,
                               text="清空",
                               style="Danger.TButton",
                               command=self._clear_validate)
        clear_btn.pack(side=tk.LEFT)

        text_container = ttk.Frame(validate_frame)
        text_container.pack(fill=tk.BOTH, expand=True)

        self.validate_input_text = tk.Text(text_container,
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
        self.validate_input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        input_scrollbar_y = ttk.Scrollbar(text_container,
                                          orient=tk.VERTICAL,
                                          command=self.validate_input_text.yview)
        input_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.validate_input_text.configure(yscrollcommand=input_scrollbar_y.set)

        input_scrollbar_x = ttk.Scrollbar(validate_frame,
                                          orient=tk.HORIZONTAL,
                                          command=self.validate_input_text.xview)
        input_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.validate_input_text.configure(xscrollcommand=input_scrollbar_x.set)

        self.validate_input_text.insert(tk.END, '<?xml version="1.0" encoding="UTF-8"?>\n<root>\n  <name>开发者工具箱</name>\n  <version>1.0.0</version>\n</root>')

        self.validate_status_label = ttk.Label(validate_frame, text="就绪", style="Status.TLabel")
        self.validate_status_label.pack(anchor=tk.W, pady=(10, 0))

    def _format_xml(self):
        input_content = self.format_input_text.get("1.0", tk.END).strip()
        if not input_content:
            self._set_format_status("输入内容为空", "warning")
            messagebox.showwarning("提示", "请输入 XML 内容")
            return

        try:
            dom = minidom.parseString(input_content)
            pretty_xml = dom.toprettyxml(indent="  ", encoding="utf-8")
            pretty_xml_str = pretty_xml.decode("utf-8")
            pretty_xml_str = self._remove_extra_blank_lines(pretty_xml_str)
            self._set_format_output(pretty_xml_str)
            self._set_format_status("格式化成功", "success")
        except Exception as e:
            line, col, msg = self._parse_xml_error(e)
            if line is not None:
                error_msg = f"XML 格式错误：第 {line} 行，第 {col} 列 - {msg}"
            else:
                error_msg = f"XML 格式错误：{msg}"
            self._set_format_status(error_msg, "error")
            messagebox.showerror("XML 解析错误", error_msg)

    def _remove_extra_blank_lines(self, text):
        return re.sub(r'\n\s*\n', '\n', text)

    def _parse_xml_error(self, exception):
        msg = str(exception)
        line = None
        col = None

        line_match = re.search(r'line\s+(\d+)', msg, re.IGNORECASE)
        if line_match:
            line = int(line_match.group(1))

        col_match = re.search(r'column\s+(\d+)', msg, re.IGNORECASE)
        if col_match:
            col = int(col_match.group(1))

        if line is not None and col is None:
            col_match = re.search(r'col\s+(\d+)', msg, re.IGNORECASE)
            if col_match:
                col = int(col_match.group(1))

        return line, col, msg

    def _copy_format_result(self):
        content = self.format_output_text.get("1.0", tk.END).strip()
        if not content:
            self._set_format_status("没有可复制的内容", "warning")
            return

        self.clipboard_clear()
        self.clipboard_append(content)
        self.update()
        self._set_format_status("已复制到剪贴板", "success")

    def _clear_format(self):
        self.format_input_text.delete("1.0", tk.END)
        self._set_format_output("")
        self._set_format_status("已清空", "info")

    def _validate_xml(self):
        input_content = self.validate_input_text.get("1.0", tk.END).strip()
        if not input_content:
            self._set_validate_status("输入内容为空", "warning")
            messagebox.showwarning("提示", "请输入 XML 内容")
            return

        try:
            ET.fromstring(input_content)
            self._set_validate_status("XML 格式正确，校验通过", "success")
            messagebox.showinfo("校验通过", "XML 格式正确！")
        except ET.ParseError as e:
            line, col = e.position
            error_msg = f"XML 格式错误：第 {line} 行，第 {col} 列 - {e.code}"
            self._set_validate_status(error_msg, "error")
            messagebox.showerror("校验失败",
                                 f"XML 格式不合法\n\n位置：第 {line} 行，第 {col} 列\n错误：{e.code}")
        except Exception as e:
            line, col, msg = self._parse_xml_error(e)
            if line is not None:
                error_msg = f"XML 格式错误：第 {line} 行，第 {col} 列 - {msg}"
            else:
                error_msg = f"XML 格式错误：{msg}"
            self._set_validate_status(error_msg, "error")
            messagebox.showerror("校验失败", error_msg)

    def _clear_validate(self):
        self.validate_input_text.delete("1.0", tk.END)
        self._set_validate_status("已清空", "info")

    def _set_format_output(self, content):
        self.format_output_text.configure(state=tk.NORMAL)
        self.format_output_text.delete("1.0", tk.END)
        self.format_output_text.insert("1.0", content)
        self.format_output_text.configure(state=tk.DISABLED)

    def _set_format_status(self, message, status_type="info"):
        colors = {
            "success": "#27ae60",
            "error": "#e74c3c",
            "warning": "#f39c12",
            "info": "#3498db"
        }
        color = colors.get(status_type, "#34495e")
        self.format_status_label.configure(text=message, foreground=color)

    def _set_validate_status(self, message, status_type="info"):
        colors = {
            "success": "#27ae60",
            "error": "#e74c3c",
            "warning": "#f39c12",
            "info": "#3498db"
        }
        color = colors.get(status_type, "#34495e")
        self.validate_status_label.configure(text=message, foreground=color)
