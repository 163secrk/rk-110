import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class QRCodeTool(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, style="Content.TFrame")
        self._setup_styles()
        self._create_widgets()
        self._qr_image = None

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
        style.configure("Status.TLabel",
                        font=("Microsoft YaHei", 10),
                        background="#f5f6fa")

    def _create_widgets(self):
        title_label = ttk.Label(self,
                                text="二维码生成",
                                style="ToolTitle.TLabel")
        title_label.pack(anchor=tk.W, pady=(0, 15))

        self._create_input_area()
        self._create_button_area()
        self._create_qr_area()
        self._create_status_area()

    def _create_input_area(self):
        input_frame = ttk.LabelFrame(self, text="输入内容", style="Content.TFrame", padding=15)
        input_frame.pack(fill=tk.X, pady=(0, 15))

        hint_label = ttk.Label(input_frame,
                               text="请输入文本或 URL（支持中文）：",
                               style="Section.TLabel")
        hint_label.pack(anchor=tk.W, pady=(0, 8))

        text_container = ttk.Frame(input_frame)
        text_container.pack(fill=tk.X)

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

    def _create_button_area(self):
        button_frame = ttk.Frame(self, style="Content.TFrame")
        button_frame.pack(fill=tk.X, pady=(0, 15))

        generate_btn = ttk.Button(button_frame,
                                  text="生成",
                                  style="Primary.TButton",
                                  command=self._generate_qr)
        generate_btn.pack(side=tk.LEFT, padx=5)

    def _create_qr_area(self):
        qr_frame = ttk.LabelFrame(self, text="二维码", style="Content.TFrame", padding=15)
        qr_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        content_frame = ttk.Frame(qr_frame, style="Content.TFrame")
        content_frame.pack(fill=tk.BOTH, expand=True)

        canvas_container = ttk.Frame(content_frame, style="Content.TFrame")
        canvas_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.qr_canvas = tk.Canvas(canvas_container,
                                   bg="white",
                                   width=400,
                                   height=400,
                                   relief=tk.FLAT,
                                   borderwidth=1,
                                   highlightthickness=1,
                                   highlightbackground="#bdc3c7",
                                   highlightcolor="#3498db")
        self.qr_canvas.pack(anchor=tk.CENTER, expand=True)

        self.qr_canvas.create_text(200, 200,
                                   text="二维码将显示在此处",
                                   font=("Microsoft YaHei", 12),
                                   fill="#95a5a6",
                                   tags="placeholder")

        btn_container = ttk.Frame(content_frame, style="Content.TFrame")
        btn_container.pack(side=tk.LEFT, padx=(20, 0), anchor=tk.N)

        self.save_btn = ttk.Button(btn_container,
                                   text="保存图片",
                                   style="Success.TButton",
                                   command=self._save_qr,
                                   state=tk.DISABLED)
        self.save_btn.pack(anchor=tk.N)

    def _create_status_area(self):
        status_frame = ttk.Frame(self, style="Content.TFrame")
        status_frame.pack(fill=tk.X, pady=(10, 0))

        self.status_label = ttk.Label(status_frame,
                                      text="就绪",
                                      style="Status.TLabel")
        self.status_label.pack(anchor=tk.W)

    def _generate_qr(self):
        try:
            import qrcode
        except ImportError:
            self._set_status("缺少 qrcode 依赖库，请先运行: pip install qrcode[pil]", "error")
            messagebox.showerror("缺少依赖", "请先安装 qrcode 库：\n\npip install qrcode[pil]")
            return

        content = self.input_text.get("1.0", tk.END).strip()
        if not content:
            self._set_status("请输入要生成二维码的内容", "warning")
            messagebox.showwarning("提示", "请输入要生成二维码的内容")
            return

        try:
            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=4,
            )
            qr.add_data(content)
            qr.make(fit=True)

            self._qr_matrix = qr.get_matrix()
            self._qr_image = qr.make_image(fill_color="black", back_color="white")

            self._draw_qr_on_canvas()
            self.save_btn.configure(state=tk.NORMAL)
            self._set_status("二维码生成成功", "success")
        except Exception as e:
            self._set_status(f"生成失败：{str(e)}", "error")
            messagebox.showerror("生成失败", f"二维码生成失败：\n\n{str(e)}")

    def _draw_qr_on_canvas(self):
        self.qr_canvas.delete("all")

        matrix = self._qr_matrix
        matrix_size = len(matrix)

        canvas_size = 400
        padding = 20
        drawable_size = canvas_size - 2 * padding

        cell_size = drawable_size // matrix_size
        actual_draw_size = cell_size * matrix_size
        offset_x = (canvas_size - actual_draw_size) // 2
        offset_y = (canvas_size - actual_draw_size) // 2

        self.qr_canvas.create_rectangle(
            offset_x - 5, offset_y - 5,
            offset_x + actual_draw_size + 5, offset_y + actual_draw_size + 5,
            fill="white", outline=""
        )

        for row in range(matrix_size):
            for col in range(matrix_size):
                if matrix[row][col]:
                    x1 = offset_x + col * cell_size
                    y1 = offset_y + row * cell_size
                    x2 = x1 + cell_size
                    y2 = y1 + cell_size
                    self.qr_canvas.create_rectangle(x1, y1, x2, y2,
                                                    fill="black", outline="")

    def _save_qr(self):
        if self._qr_image is None:
            self._set_status("没有可保存的二维码", "warning")
            return

        try:
            from PIL import Image
        except ImportError:
            self._set_status("缺少 Pillow 依赖库，请先运行: pip install Pillow", "error")
            messagebox.showerror("缺少依赖", "请先安装 Pillow 库：\n\npip install Pillow")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG 图片", "*.png"), ("所有文件", "*.*")],
            title="保存二维码图片",
            initialfile="qrcode.png"
        )

        if not file_path:
            return

        try:
            self._qr_image.save(file_path)
            self._set_status(f"二维码已保存到：{file_path}", "success")
            messagebox.showinfo("保存成功", f"二维码图片已保存到：\n\n{file_path}")
        except Exception as e:
            self._set_status(f"保存失败：{str(e)}", "error")
            messagebox.showerror("保存失败", f"保存图片失败：\n\n{str(e)}")

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
