import base64
import binascii
import io
import os
import re
import time
import tkinter as tk
from tkinter import ttk, filedialog

from PIL import Image, ImageTk, UnidentifiedImageError


SUPPORTED_FORMATS = {
    "PNG": "PNG",
    "JPEG": "JPG",
    "GIF": "GIF",
    "WEBP": "WebP",
    "BMP": "BMP",
}
SUPPORTED_EXTS = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp")
MAX_SIZE_BYTES = 2 * 1024 * 1024
_DATA_URI_RE = re.compile(r"^data:image/[a-zA-Z0-9.+\-]+;base64,(.*)$", re.DOTALL)


class ImageBase64Tool(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, style="Content.TFrame")
        self._b64_result = ""
        self._data_uri = ""
        self._decoded_image = None
        self._preview_photo = None
        self.mode_var = tk.IntVar(value=0)
        self._setup_styles()
        self._create_widgets()
        self._setup_dnd()
        self._switch_mode()

    # ------------------------------------------------------------------ styles
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
                        font=("Microsoft YaHei", 10),
                        background="#f5f6fa",
                        foreground="#7f8c8d")
        style.configure("Mode.TRadiobutton",
                        font=("Microsoft YaHei", 11, "bold"),
                        background="#f5f6fa")
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
        style.configure("Duration.TLabel",
                        font=("Consolas", 10, "bold"),
                        background="#f5f6fa",
                        foreground="#34495e")

    # ------------------------------------------------------------------ layout
    def _create_widgets(self):
        title = ttk.Label(self, text="图片Base64互转", style="ToolTitle.TLabel")
        title.pack(anchor=tk.W, pady=(0, 10))

        mode_frame = ttk.Frame(self, style="Content.TFrame")
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Radiobutton(mode_frame, text="图片转Base64", value=0,
                        variable=self.mode_var, command=self._switch_mode,
                        style="Mode.TRadiobutton").pack(side=tk.LEFT, padx=(0, 30))
        ttk.Radiobutton(mode_frame, text="Base64转图片", value=1,
                        variable=self.mode_var, command=self._switch_mode,
                        style="Mode.TRadiobutton").pack(side=tk.LEFT)

        self.content_holder = ttk.Frame(self, style="Content.TFrame")
        self.content_holder.pack(fill=tk.BOTH, expand=True)

        self._create_image_to_b64_mode(self.content_holder)
        self._create_b64_to_image_mode(self.content_holder)

        self._create_status_area()

    # ------------------------- mode 1: image -> base64
    def _create_image_to_b64_mode(self, parent):
        self.mode1_frame = ttk.Frame(parent, style="Content.TFrame")
        self.mode1_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        paned = ttk.PanedWindow(self.mode1_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(paned, style="Content.TFrame")
        right = ttk.Frame(paned, style="Content.TFrame")
        paned.add(left, weight=1)
        paned.add(right, weight=2)

        drop_frame = ttk.LabelFrame(left, text="拖拽区", style="Content.TFrame", padding=15)
        drop_frame.pack(fill=tk.BOTH, expand=True)

        self.drop_canvas = tk.Canvas(drop_frame, width=300, height=170,
                                     bg="#ffffff", relief=tk.FLAT, borderwidth=0,
                                     highlightthickness=2,
                                     highlightbackground="#bdc3c7",
                                     highlightcolor="#3498db")
        self.drop_canvas.pack(fill=tk.BOTH, expand=True)
        self.drop_canvas.bind("<Button-1>", lambda e: self._select_file())
        self._draw_drop_hint("拖拽图片到此处\n或点击选择文件\n\n支持 PNG / JPG / GIF / WebP / BMP")

        select_btn = ttk.Button(left, text="选择文件", style="Primary.TButton",
                                command=self._select_file)
        select_btn.pack(fill=tk.X, pady=(10, 0))

        info_frame = ttk.LabelFrame(right, text="文件信息", style="Content.TFrame", padding=12)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        self.file_name_var = tk.StringVar(value="-")
        self.file_size_var = tk.StringVar(value="-")
        self.file_dims_var = tk.StringVar(value="-")
        self.file_format_var = tk.StringVar(value="-")
        self._make_info_row(info_frame, "文件名：", self.file_name_var, 0)
        self._make_info_row(info_frame, "大小：", self.file_size_var, 1)
        self._make_info_row(info_frame, "尺寸：", self.file_dims_var, 2)
        self._make_info_row(info_frame, "格式：", self.file_format_var, 3)

        self.size_warning_lbl = tk.Label(info_frame, text="", anchor=tk.W,
                                         font=("Microsoft YaHei", 9),
                                         bg="#f5f6fa", fg="#f39c12")
        self.size_warning_lbl.pack(fill=tk.X, pady=(6, 0))

        result_frame = ttk.LabelFrame(right, text="Base64 编码结果", style="Content.TFrame", padding=12)
        result_frame.pack(fill=tk.BOTH, expand=True)

        out_container = ttk.Frame(result_frame)
        out_container.pack(fill=tk.BOTH, expand=True)

        self.b64_output = tk.Text(out_container,
                                  font=("Consolas", 10),
                                  bg="white", fg="#2c3e50",
                                  insertbackground="#3498db",
                                  selectbackground="#3498db",
                                  selectforeground="white",
                                  wrap=tk.NONE, padx=8, pady=8,
                                  relief=tk.FLAT, borderwidth=1,
                                  highlightthickness=1,
                                  highlightbackground="#bdc3c7",
                                  highlightcolor="#3498db", height=8)
        self.b64_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        y_scroll = ttk.Scrollbar(out_container, orient=tk.VERTICAL,
                                 command=self.b64_output.yview)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.b64_output.configure(yscrollcommand=y_scroll.set)

        x_scroll = ttk.Scrollbar(result_frame, orient=tk.HORIZONTAL,
                                 command=self.b64_output.xview)
        x_scroll.pack(fill=tk.X)
        self.b64_output.configure(xscrollcommand=x_scroll.set)

        btn_row = ttk.Frame(right, style="Content.TFrame")
        btn_row.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(btn_row, text="复制 Base64", style="Action.TButton",
                   command=self._copy_base64).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_row, text="复制 Data URI", style="Success.TButton",
                   command=self._copy_data_uri).pack(side=tk.LEFT)

    # ------------------------- mode 2: base64 -> image
    def _create_b64_to_image_mode(self, parent):
        self.mode2_frame = ttk.Frame(parent, style="Content.TFrame")
        self.mode2_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        input_frame = ttk.LabelFrame(self.mode2_frame, text="Base64 字符串",
                                     style="Content.TFrame", padding=12)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        hint = ttk.Label(input_frame, text="粘贴图片的 Base64 字符串（可含 data: 前缀）",
                         style="SubSection.TLabel")
        hint.pack(anchor=tk.W, pady=(0, 5))

        in_container = ttk.Frame(input_frame)
        in_container.pack(fill=tk.X)
        self.b64_input = tk.Text(in_container,
                                 font=("Consolas", 10),
                                 bg="white", fg="#2c3e50",
                                 insertbackground="#3498db",
                                 selectbackground="#3498db",
                                 selectforeground="white",
                                 wrap=tk.CHAR, padx=8, pady=8,
                                 relief=tk.FLAT, borderwidth=1,
                                 highlightthickness=1,
                                 highlightbackground="#bdc3c7",
                                 highlightcolor="#3498db", height=5)
        self.b64_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        in_scroll = ttk.Scrollbar(in_container, orient=tk.VERTICAL,
                                  command=self.b64_input.yview)
        in_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.b64_input.configure(yscrollcommand=in_scroll.set)

        decode_btn = ttk.Button(input_frame, text="解码预览", style="Primary.TButton",
                                command=self._decode_preview)
        decode_btn.pack(anchor=tk.W, pady=(10, 0))

        preview_frame = ttk.LabelFrame(self.mode2_frame, text="预览",
                                       style="Content.TFrame", padding=12)
        preview_frame.pack(fill=tk.BOTH, expand=True)

        self.preview_canvas = tk.Canvas(preview_frame, width=380, height=300,
                                        bg="#ffffff", relief=tk.FLAT, borderwidth=0,
                                        highlightthickness=1,
                                        highlightbackground="#bdc3c7")
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        self._draw_preview_placeholder()

        self.decoded_dims_var = tk.StringVar(value="-")
        self.decoded_format_var = tk.StringVar(value="-")
        info_row = ttk.Frame(self.mode2_frame, style="Content.TFrame")
        info_row.pack(fill=tk.X, pady=(10, 0))
        self._make_info_row(info_row, "尺寸：", self.decoded_dims_var, 0)
        self._make_info_row(info_row, "格式：", self.decoded_format_var, 1, same_row=True)

    # ------------------------- shared status bar
    def _create_status_area(self):
        status_frame = ttk.Frame(self, style="Content.TFrame")
        status_frame.pack(fill=tk.X, pady=(10, 0))

        self.status_label = ttk.Label(status_frame, text="就绪", style="Status.TLabel")
        self.status_label.pack(side=tk.LEFT)

        self.duration_label = ttk.Label(status_frame, text="耗时：-",
                                       style="Duration.TLabel")
        self.duration_label.pack(side=tk.RIGHT)

    # ------------------------------------------------------------------ helpers
    def _make_info_row(self, parent, label_text, var, row, same_row=False):
        if same_row:
            row_frame = ttk.Frame(parent, style="Content.TFrame")
            row_frame.pack(side=tk.LEFT, padx=(0, 30))
        else:
            row_frame = ttk.Frame(parent, style="Content.TFrame")
            row_frame.pack(fill=tk.X, pady=3)

        ttk.Label(row_frame, text=label_text, style="SubSection.TLabel", width=8).pack(side=tk.LEFT)
        ttk.Label(row_frame, textvariable=var, font=("Consolas", 10, "bold"),
                  background="#f5f6fa", foreground="#2c3e50").pack(side=tk.LEFT)

    def _draw_drop_hint(self, text):
        self.drop_canvas.delete("all")
        self.drop_canvas.create_text(self.drop_canvas.winfo_width() // 2 or 150,
                                     self.drop_canvas.winfo_height() // 2 or 85,
                                     text=text, justify=tk.CENTER,
                                     font=("Microsoft YaHei", 10),
                                     fill="#95a5a6", tags="hint")

    def _draw_preview_placeholder(self):
        self.preview_canvas.delete("all")
        self.preview_canvas.create_text(self.preview_canvas.winfo_width() // 2 or 190,
                                        self.preview_canvas.winfo_height() // 2 or 150,
                                        text="解码后的图片将显示在此处",
                                        font=("Microsoft YaHei", 11),
                                        fill="#bdc3c7", tags="placeholder")

    def _format_size(self, num):
        if num < 1024:
            return f"{num} B"
        if num < 1024 * 1024:
            return f"{num / 1024:.2f} KB"
        return f"{num / (1024 * 1024):.2f} MB"

    def _format_to_mime(self, fmt):
        fmt = (fmt or "").upper()
        mapping = {"PNG": "png", "JPEG": "jpeg", "GIF": "gif",
                   "WEBP": "webp", "BMP": "bmp"}
        return "image/" + mapping.get(fmt, fmt.lower())

    def _set_status(self, message, status_type="info"):
        if not hasattr(self, "status_label"):
            return
        colors = {"success": "#27ae60", "error": "#e74c3c",
                  "warning": "#f39c12", "info": "#3498db"}
        self.status_label.configure(text=message,
                                    foreground=colors.get(status_type, "#34495e"))

    def _set_duration(self, ms):
        if hasattr(self, "duration_label"):
            self.duration_label.configure(text=f"耗时：{ms:.1f} ms")

    # ------------------------------------------------------------------ drag&drop
    def _setup_dnd(self):
        try:
            import tkinterdnd2  # noqa: F401
        except ImportError:
            return
        try:
            self.drop_canvas.drop_target_register("files")
            self.drop_canvas.dnd_bind("<<Drop>>", self._on_drop)
            self.drop_canvas.dnd_bind("<<DragEnter>>", self._on_drag_enter)
            self.drop_canvas.dnd_bind("<<DragLeave>>", self._on_drag_leave)
        except (AttributeError, tk.TclError):
            pass

    def _on_drop(self, event):
        try:
            paths = self.drop_canvas.tk.splitlist(event.data)
        except Exception:
            paths = [event.data.strip().strip("{}")]
        if paths:
            self._load_image_file(paths[0])

    def _on_drag_enter(self, event):
        self.drop_canvas.configure(highlightbackground="#3498db")

    def _on_drag_leave(self, event):
        self.drop_canvas.configure(highlightbackground="#bdc3c7")

    # ------------------------------------------------------------------ mode 1
    def _select_file(self):
        file_path = filedialog.askopenfilename(
            title="选择图片文件",
            filetypes=[
                ("图片文件", "*.png *.jpg *.jpeg *.gif *.webp *.bmp"),
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("GIF", "*.gif"),
                ("WebP", "*.webp"),
                ("BMP", "*.bmp"),
                ("所有文件", "*.*"),
            ],
        )
        if file_path:
            self._load_image_file(file_path)

    def _load_image_file(self, file_path):
        start = time.perf_counter()
        if not file_path or not os.path.isfile(file_path):
            self._set_status("文件不存在或无法访问", "error")
            return

        ext = os.path.splitext(file_path)[1].lower()
        if ext not in SUPPORTED_EXTS:
            self._set_status(f"不支持的文件格式：{ext}（仅支持 PNG/JPG/GIF/WebP/BMP）", "error")
            return

        try:
            with open(file_path, "rb") as f:
                raw = f.read()
        except Exception as e:
            self._set_status(f"读取文件失败：{e}", "error")
            return

        file_size = len(raw)
        try:
            with Image.open(io.BytesIO(raw)) as img:
                img_format = img.format
                width, height = img.size
        except Exception as e:
            self._set_status(f"无法识别为图片：{e}", "error")
            return

        b64_str = base64.b64encode(raw).decode("ascii")
        self._b64_result = b64_str
        self._data_uri = f"data:{self._format_to_mime(img_format)};base64,{b64_str}"

        self.file_name_var.set(os.path.basename(file_path))
        self.file_size_var.set(self._format_size(file_size))
        self.file_dims_var.set(f"{width} × {height}")
        self.file_format_var.set(SUPPORTED_FORMATS.get(img_format, img_format or "未知"))

        if file_size > MAX_SIZE_BYTES:
            self.size_warning_lbl.configure(
                text=f"⚠ 文件较大（{self._format_size(file_size)}，超过 2MB），"
                     "Base64 结果较长，复制可能较慢",
                fg="#f39c12")
        else:
            self.size_warning_lbl.configure(text="", fg="#f39c12")

        self.b64_output.delete("1.0", tk.END)
        self.b64_output.insert("1.0", b64_str)

        self._draw_drop_hint(f"✓ {os.path.basename(file_path)}")

        elapsed_ms = (time.perf_counter() - start) * 1000
        self._set_status("图片转 Base64 完成", "success")
        self._set_duration(elapsed_ms)

    def _copy_base64(self):
        if not self._b64_result:
            self._set_status("没有可复制的 Base64 结果", "warning")
            return
        self.clipboard_clear()
        self.clipboard_append(self._b64_result)
        self.update()
        self._set_status("Base64 已复制到剪贴板", "success")

    def _copy_data_uri(self):
        if not self._data_uri:
            self._set_status("没有可复制的 Data URI", "warning")
            return
        self.clipboard_clear()
        self.clipboard_append(self._data_uri)
        self.update()
        self._set_status("Data URI 已复制到剪贴板", "success")

    # ------------------------------------------------------------------ mode 2
    def _decode_preview(self):
        start = time.perf_counter()
        raw_input = self.b64_input.get("1.0", tk.END).strip()
        if not raw_input:
            self._set_status("请先粘贴 Base64 字符串", "warning")
            return

        data = raw_input
        uri_match = _DATA_URI_RE.match(data)
        if uri_match:
            data = uri_match.group(1)
        data = re.sub(r"\s+", "", data)

        ok, error = self._validate_base64(data)
        if not ok:
            self._set_status(error, "error")
            self._clear_preview()
            return

        try:
            decoded = base64.b64decode(data, validate=True)
        except (binascii.Error, ValueError) as e:
            self._set_status(f"不是有效的 Base64 字符串：{e}", "error")
            self._clear_preview()
            return

        try:
            img = Image.open(io.BytesIO(decoded))
            img.load()
        except UnidentifiedImageError:
            self._set_status("是 Base64 数据，但不是有效的图片", "error")
            self._clear_preview()
            return
        except Exception as e:
            self._set_status(f"是 Base64 数据，但无法识别为图片：{e}", "error")
            self._clear_preview()
            return

        fmt = img.format
        if fmt not in SUPPORTED_FORMATS:
            self._set_status(f"图片格式不支持：{fmt}（仅支持 PNG/JPG/GIF/WebP/BMP）", "error")
            self._clear_preview()
            return

        self._decoded_image = img
        self._show_preview(img)
        w, h = img.size
        self.decoded_dims_var.set(f"{w} × {h}")
        self.decoded_format_var.set(SUPPORTED_FORMATS.get(fmt, fmt))

        elapsed_ms = (time.perf_counter() - start) * 1000
        self._set_status("Base64 转图片成功", "success")
        self._set_duration(elapsed_ms)

    def _validate_base64(self, data):
        if not data:
            return False, "Base64 字符串为空"
        if not re.fullmatch(r"[A-Za-z0-9+/=]+", data):
            return False, "不是有效的 Base64（包含非法字符）"
        if "=" in data.rstrip("="):
            return False, "不是有效的 Base64（填充符 = 位置错误）"
        if data.count("=") > 2:
            return False, "不是有效的 Base64（填充符 = 过多）"
        if len(data) % 4 != 0:
            return False, "不是有效的 Base64（长度或填充不正确）"
        return True, ""

    def _show_preview(self, img):
        self._preview_photo = None
        canvas_w = int(self.preview_canvas.cget("width")) or 380
        canvas_h = int(self.preview_canvas.cget("height")) or 300
        thumb = img.copy()
        thumb.thumbnail((canvas_w - 20, canvas_h - 20), Image.LANCZOS)
        self._preview_photo = ImageTk.PhotoImage(thumb)
        self.preview_canvas.delete("all")
        self.preview_canvas.create_image(canvas_w // 2, canvas_h // 2,
                                         anchor=tk.CENTER, image=self._preview_photo,
                                         tags="preview")

    def _clear_preview(self):
        self._decoded_image = None
        self._preview_photo = None
        self._draw_preview_placeholder()
        self.decoded_dims_var.set("-")
        self.decoded_format_var.set("-")

    # ------------------------------------------------------------------ switch
    def _switch_mode(self):
        if self.mode_var.get() == 0:
            self.mode1_frame.tkraise()
        else:
            self.mode2_frame.tkraise()
