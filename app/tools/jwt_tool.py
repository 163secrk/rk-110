import base64
import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timezone


class JWTTool(ttk.Frame):
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
                        background="#ffffff",
                        foreground="#3498db")
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
        style.configure("Timestamp.TLabel",
                        font=("Microsoft YaHei", 9),
                        background="#ffffff",
                        foreground="#27ae60")

    def _create_widgets(self):
        title_label = ttk.Label(self,
                                text="JWT 解析",
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
                                text="粘贴 JWT Token：",
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
                                  wrap=tk.WORD,
                                  padx=10,
                                  pady=10,
                                  relief=tk.FLAT,
                                  borderwidth=1,
                                  highlightthickness=1,
                                  highlightbackground="#bdc3c7",
                                  highlightcolor="#3498db",
                                  height=5)
        self.input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        input_scrollbar = ttk.Scrollbar(text_container,
                                        orient=tk.VERTICAL,
                                        command=self.input_text.yview)
        input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.input_text.configure(yscrollcommand=input_scrollbar.set)

        parent.add(input_frame, weight=1)

    def _create_button_area(self, parent):
        button_frame = ttk.Frame(parent, style="Content.TFrame")
        button_frame.pack(fill=tk.X, pady=10)

        btn_container = ttk.Frame(button_frame, style="Content.TFrame")
        btn_container.pack(anchor=tk.CENTER)

        parse_btn = ttk.Button(btn_container,
                               text="解析",
                               style="Primary.TButton",
                               command=self._parse_jwt)
        parse_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(btn_container,
                               text="清空",
                               style="Danger.TButton",
                               command=self._clear_all)
        clear_btn.pack(side=tk.LEFT, padx=5)

    def _create_output_area(self, parent):
        output_frame = ttk.Frame(parent, style="Content.TFrame")

        sections_paned = ttk.PanedWindow(output_frame, orient=tk.HORIZONTAL)
        sections_paned.pack(fill=tk.BOTH, expand=True)

        self._create_section(sections_paned, "Header", "header")
        self._create_section(sections_paned, "Payload", "payload")
        self._create_section(sections_paned, "Signature", "signature")

        parent.add(output_frame, weight=5)

    def _create_section(self, parent, title, attr_prefix):
        section_frame = ttk.Frame(parent, style="Content.TFrame")

        title_label = ttk.Label(section_frame,
                                text=title,
                                style="Section.TLabel")
        title_label.pack(anchor=tk.W, pady=(0, 5))

        timestamp_frame = ttk.Frame(section_frame, style="Content.TFrame")
        timestamp_frame.pack(fill=tk.X, pady=(0, 5))

        text_container = ttk.Frame(section_frame)
        text_container.pack(fill=tk.BOTH, expand=True)

        text_widget = tk.Text(text_container,
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
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(text_container,
                                  orient=tk.VERTICAL,
                                  command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.configure(yscrollcommand=scrollbar.set)

        hscrollbar = ttk.Scrollbar(section_frame,
                                   orient=tk.HORIZONTAL,
                                   command=text_widget.xview)
        hscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        text_widget.configure(xscrollcommand=hscrollbar.set)

        setattr(self, f"{attr_prefix}_text", text_widget)
        setattr(self, f"{attr_prefix}_timestamp_frame", timestamp_frame)

        parent.add(section_frame, weight=1)

    def _create_status_area(self):
        status_frame = ttk.Frame(self, style="Content.TFrame")
        status_frame.pack(fill=tk.X, pady=(10, 0))

        self.status_label = ttk.Label(status_frame,
                                      text="就绪",
                                      style="Status.TLabel")
        self.status_label.pack(anchor=tk.W)

    def _base64url_decode(self, data):
        padding = 4 - len(data) % 4
        if padding != 4:
            data += "=" * padding
        data = data.replace("-", "+").replace("_", "/")
        return base64.b64decode(data.encode("utf-8"))

    def _is_valid_base64url(self, data):
        try:
            padding = 4 - len(data) % 4
            if padding != 4:
                data += "=" * padding
            data = data.replace("-", "+").replace("_", "/")
            base64.b64decode(data.encode("utf-8"), validate=True)
            return True
        except Exception:
            return False

    def _format_timestamp(self, timestamp):
        try:
            ts = int(timestamp)
            dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            local_dt = dt.astimezone()
            return local_dt.strftime("%Y-%m-%d %H:%M:%S %Z")
        except Exception:
            return None

    def _update_timestamp_labels(self, payload_data):
        for widget in self.payload_timestamp_frame.winfo_children():
            widget.destroy()

        timestamp_keys = ["iat", "exp", "nbf", "auth_time"]
        found = False
        for key in timestamp_keys:
            if key in payload_data and isinstance(payload_data[key], (int, float)):
                formatted = self._format_timestamp(payload_data[key])
                if formatted:
                    found = True
                    label_text = f"{key}: {payload_data[key]}  →  {formatted}"
                    label = ttk.Label(self.payload_timestamp_frame,
                                      text=label_text,
                                      style="Timestamp.TLabel")
                    label.pack(anchor=tk.W, pady=1)

        if not found:
            label = ttk.Label(self.payload_timestamp_frame,
                              text="",
                              style="Timestamp.TLabel")
            label.pack(anchor=tk.W)

    def _parse_jwt(self):
        token = self.input_text.get("1.0", tk.END).strip()
        if not token:
            self._set_status("请输入 JWT Token", "warning")
            messagebox.showwarning("提示", "请输入 JWT Token")
            return

        parts = token.split(".")
        if len(parts) != 3:
            self._set_status(f"格式错误：JWT Token 必须包含 3 段（以 '.' 分隔），当前为 {len(parts)} 段", "error")
            messagebox.showerror("格式错误",
                                 f"JWT Token 格式不正确\n\n"
                                 f"标准 JWT 格式：Header.Payload.Signature（三段以 '.' 分隔）\n"
                                 f"当前输入包含 {len(parts)} 段")
            return

        header_b64, payload_b64, signature_b64 = parts

        if not self._is_valid_base64url(signature_b64):
            self._set_status("格式错误：Signature 段不是有效的 Base64URL 格式", "error")
            messagebox.showerror("格式错误",
                                 "Signature 段格式不正确\n\n"
                                 "Signature 必须是有效的 Base64URL 编码字符串")
            return

        try:
            header_bytes = self._base64url_decode(header_b64)
            header_json = json.loads(header_bytes.decode("utf-8"))
        except Exception as e:
            self._set_status(f"Header 解析失败：{str(e)}", "error")
            messagebox.showerror("解析错误",
                                 f"Header 段解析失败\n\n"
                                 f"可能原因：\n"
                                 f"1. Header 不是有效的 Base64URL 编码\n"
                                 f"2. 解码后的内容不是合法的 JSON\n\n"
                                 f"错误信息：{str(e)}")
            return

        try:
            payload_bytes = self._base64url_decode(payload_b64)
            payload_json = json.loads(payload_bytes.decode("utf-8"))
        except Exception as e:
            self._set_status(f"Payload 解析失败：{str(e)}", "error")
            messagebox.showerror("解析错误",
                                 f"Payload 段解析失败\n\n"
                                 f"可能原因：\n"
                                 f"1. Payload 不是有效的 Base64URL 编码\n"
                                 f"2. 解码后的内容不是合法的 JSON\n\n"
                                 f"错误信息：{str(e)}")
            return

        header_formatted = json.dumps(header_json, ensure_ascii=False, indent=2)
        payload_formatted = json.dumps(payload_json, ensure_ascii=False, indent=2)

        self._set_text(self.header_text, header_formatted)
        self._set_text(self.payload_text, payload_formatted)
        self._set_text(self.signature_text, signature_b64)

        self._update_timestamp_labels(payload_json)
        self._set_status("JWT 解析成功", "success")

    def _set_text(self, text_widget, content):
        text_widget.configure(state=tk.NORMAL)
        text_widget.delete("1.0", tk.END)
        text_widget.insert("1.0", content)
        text_widget.configure(state=tk.DISABLED)

    def _clear_all(self):
        self.input_text.delete("1.0", tk.END)
        self._set_text(self.header_text, "")
        self._set_text(self.payload_text, "")
        self._set_text(self.signature_text, "")
        for widget in self.payload_timestamp_frame.winfo_children():
            widget.destroy()
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
