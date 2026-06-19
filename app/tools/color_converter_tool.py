import tkinter as tk
from tkinter import ttk
import re


class ColorConverterTool(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, style="Content.TFrame")
        self.r = tk.IntVar(value=100)
        self.g = tk.IntVar(value=150)
        self.b = tk.IntVar(value=200)
        self._updating = False
        self._setup_styles()
        self._create_widgets()
        self._update_from_rgb()

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
                        padding=6)
        style.configure("Status.TLabel",
                        font=("Microsoft YaHei", 10),
                        background="#f5f6fa")
        style.configure("TScale",
                        background="#f5f6fa",
                        troughcolor="#bdc3c7")
        style.configure("ColorValue.TEntry",
                        font=("Consolas", 11),
                        padding=8)

    def _create_widgets(self):
        title_label = ttk.Label(self,
                                text="颜色转换",
                                style="ToolTitle.TLabel")
        title_label.pack(anchor=tk.W, pady=(0, 15))

        main_frame = ttk.Frame(self, style="Content.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(main_frame, style="Content.TFrame")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))

        right_frame = ttk.Frame(main_frame, style="Content.TFrame")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._create_sliders(left_frame)
        self._create_color_preview(right_frame)
        self._create_value_inputs(right_frame)
        self._create_status_area()

    def _create_sliders(self, parent):
        slider_frame = ttk.LabelFrame(parent, text="RGB 滑块", style="Content.TFrame", padding=15)
        slider_frame.pack(fill=tk.X, pady=(0, 15))

        self._create_rgb_slider(slider_frame, "R", self.r, "#e74c3c", 0)
        self._create_rgb_slider(slider_frame, "G", self.g, "#27ae60", 1)
        self._create_rgb_slider(slider_frame, "B", self.b, "#3498db", 2)

    def _create_rgb_slider(self, parent, label, var, color, row):
        row_frame = ttk.Frame(parent, style="Content.TFrame")
        row_frame.pack(fill=tk.X, pady=8)

        lbl = ttk.Label(row_frame, text=label, style="SubSection.TLabel", width=3)
        lbl.pack(side=tk.LEFT)

        slider = ttk.Scale(row_frame,
                           from_=0,
                           to=255,
                           orient=tk.HORIZONTAL,
                           variable=var,
                           command=lambda e, v=var: self._on_slider_change())
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        value_label = ttk.Label(row_frame,
                                textvariable=var,
                                font=("Consolas", 11, "bold"),
                                background="#f5f6fa",
                                foreground=color,
                                width=4)
        value_label.pack(side=tk.LEFT)

    def _create_color_preview(self, parent):
        preview_frame = ttk.LabelFrame(parent, text="颜色预览", style="Content.TFrame", padding=15)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        self.color_preview = tk.Frame(preview_frame,
                                      bg=self._rgb_to_hex(self.r.get(), self.g.get(), self.b.get()),
                                      relief=tk.FLAT,
                                      borderwidth=2,
                                      highlightbackground="#bdc3c7",
                                      highlightthickness=1)
        self.color_preview.pack(fill=tk.BOTH, expand=True, ipady=60)

    def _create_value_inputs(self, parent):
        input_frame = ttk.LabelFrame(parent, text="颜色值", style="Content.TFrame", padding=15)
        input_frame.pack(fill=tk.X)

        self.hex_var = tk.StringVar()
        self.rgb_var = tk.StringVar()
        self.hsl_var = tk.StringVar()

        self.hex_error = ttk.Label(input_frame, text="", font=("Microsoft YaHei", 9), background="#f5f6fa", foreground="#e74c3c")
        self.rgb_error = ttk.Label(input_frame, text="", font=("Microsoft YaHei", 9), background="#f5f6fa", foreground="#e74c3c")
        self.hsl_error = ttk.Label(input_frame, text="", font=("Microsoft YaHei", 9), background="#f5f6fa", foreground="#e74c3c")

        self._create_value_row(input_frame, "HEX:", self.hex_var, self._on_hex_change, self.hex_error, 0)
        self._create_value_row(input_frame, "RGB:", self.rgb_var, self._on_rgb_change, self.rgb_error, 1)
        self._create_value_row(input_frame, "HSL:", self.hsl_var, self._on_hsl_change, self.hsl_error, 2)

    def _create_value_row(self, parent, label_text, var, callback, error_label, row):
        row_frame = ttk.Frame(parent, style="Content.TFrame")
        row_frame.pack(fill=tk.X, pady=6)

        lbl = ttk.Label(row_frame, text=label_text, style="SubSection.TLabel", width=6)
        lbl.pack(side=tk.LEFT)

        entry = ttk.Entry(row_frame,
                          textvariable=var,
                          font=("Consolas", 11),
                          style="ColorValue.TEntry")
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        entry.bind("<KeyRelease>", lambda e: callback())
        entry.bind("<FocusOut>", lambda e: callback())

        copy_btn = ttk.Button(row_frame,
                              text="复制",
                              style="Action.TButton",
                              width=8,
                              command=lambda v=var: self._copy_value(v))
        copy_btn.pack(side=tk.LEFT)

        error_label.pack(fill=tk.X, pady=(2, 0))

    def _create_status_area(self):
        status_frame = ttk.Frame(self, style="Content.TFrame")
        status_frame.pack(fill=tk.X, pady=(10, 0))

        self.status_label = ttk.Label(status_frame,
                                      text="就绪",
                                      style="Status.TLabel")
        self.status_label.pack(anchor=tk.W)

    def _on_slider_change(self):
        if self._updating:
            return
        self._updating = True
        try:
            self._update_from_rgb()
        finally:
            self._updating = False

    def _on_hex_change(self):
        if self._updating:
            return
        self._updating = True
        try:
            hex_str = self.hex_var.get().strip()
            if not hex_str:
                self.hex_error.configure(text="")
                return

            r, g, b = self._parse_hex(hex_str)
            if r is not None:
                self.r.set(r)
                self.g.set(g)
                self.b.set(b)
                self._update_from_rgb(skip_hex=True)
                self.hex_error.configure(text="")
                self._set_status("HEX 颜色已更新", "success")
            else:
                self.hex_error.configure(text="格式错误，正确格式如 #FF5733 或 FF5733")
                self._set_status("HEX 格式错误", "error")
        finally:
            self._updating = False

    def _on_rgb_change(self):
        if self._updating:
            return
        self._updating = True
        try:
            rgb_str = self.rgb_var.get().strip()
            if not rgb_str:
                self.rgb_error.configure(text="")
                return

            r, g, b = self._parse_rgb(rgb_str)
            if r is not None:
                self.r.set(r)
                self.g.set(g)
                self.b.set(b)
                self._update_from_rgb(skip_rgb=True)
                self.rgb_error.configure(text="")
                self._set_status("RGB 颜色已更新", "success")
            else:
                self.rgb_error.configure(text="格式错误，正确格式如 rgb(255, 87, 51) 或 255, 87, 51")
                self._set_status("RGB 格式错误", "error")
        finally:
            self._updating = False

    def _on_hsl_change(self):
        if self._updating:
            return
        self._updating = True
        try:
            hsl_str = self.hsl_var.get().strip()
            if not hsl_str:
                self.hsl_error.configure(text="")
                return

            r, g, b = self._parse_hsl(hsl_str)
            if r is not None:
                self.r.set(r)
                self.g.set(g)
                self.b.set(b)
                self._update_from_rgb(skip_hsl=True)
                self.hsl_error.configure(text="")
                self._set_status("HSL 颜色已更新", "success")
            else:
                self.hsl_error.configure(text="格式错误，正确格式如 hsl(10, 100%, 60%) 或 10, 100%, 60%")
                self._set_status("HSL 格式错误", "error")
        finally:
            self._updating = False

    def _update_from_rgb(self, skip_hex=False, skip_rgb=False, skip_hsl=False):
        r = self.r.get()
        g = self.g.get()
        b = self.b.get()

        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))

        hex_color = self._rgb_to_hex(r, g, b)
        self.color_preview.configure(bg=hex_color)

        if not skip_hex:
            self.hex_var.set(hex_color.upper())
            self.hex_error.configure(text="")

        if not skip_rgb:
            self.rgb_var.set(f"rgb({r}, {g}, {b})")
            self.rgb_error.configure(text="")

        if not skip_hsl:
            h, s, l = self._rgb_to_hsl(r, g, b)
            self.hsl_var.set(f"hsl({h}, {s}%, {l}%)")
            self.hsl_error.configure(text="")

    def _rgb_to_hex(self, r, g, b):
        return f"#{r:02x}{g:02x}{b:02x}"

    def _parse_hex(self, hex_str):
        hex_str = hex_str.lstrip("#")
        if len(hex_str) == 3:
            hex_str = "".join(c * 2 for c in hex_str)
        if len(hex_str) != 6:
            return None, None, None
        try:
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            return r, g, b
        except ValueError:
            return None, None, None

    def _parse_rgb(self, rgb_str):
        match = re.match(r"^rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$", rgb_str, re.IGNORECASE)
        if not match:
            match = re.match(r"^(\d+)\s*,\s*(\d+)\s*,\s*(\d+)$", rgb_str)
        if not match:
            return None, None, None
        try:
            r = int(match.group(1))
            g = int(match.group(2))
            b = int(match.group(3))
            if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
                return r, g, b
        except ValueError:
            pass
        return None, None, None

    def _parse_hsl(self, hsl_str):
        match = re.match(r"^hsl\s*\(\s*(\d+)\s*,\s*(\d+)%?\s*,\s*(\d+)%?\s*\)$", hsl_str, re.IGNORECASE)
        if not match:
            match = re.match(r"^(\d+)\s*,\s*(\d+)%?\s*,\s*(\d+)%?$", hsl_str)
        if not match:
            return None, None, None
        try:
            h = int(match.group(1))
            s = int(match.group(2))
            l = int(match.group(3))
            if 0 <= h <= 360 and 0 <= s <= 100 and 0 <= l <= 100:
                return self._hsl_to_rgb(h, s, l)
        except ValueError:
            pass
        return None, None, None

    def _rgb_to_hsl(self, r, g, b):
        r /= 255.0
        g /= 255.0
        b /= 255.0

        max_val = max(r, g, b)
        min_val = min(r, g, b)
        h, s, l = 0, 0, (max_val + min_val) / 2

        if max_val != min_val:
            d = max_val - min_val
            s = d / (2 - max_val - min_val) if l > 0.5 else d / (max_val + min_val)
            if max_val == r:
                h = ((g - b) / d + (6 if g < b else 0)) / 6
            elif max_val == g:
                h = ((b - r) / d + 2) / 6
            else:
                h = ((r - g) / d + 4) / 6

        return int(h * 360), int(s * 100), int(l * 100)

    def _hsl_to_rgb(self, h, s, l):
        h /= 360.0
        s /= 100.0
        l /= 100.0

        if s == 0:
            r = g = b = l
        else:
            def hue2rgb(p, q, t):
                if t < 0:
                    t += 1
                if t > 1:
                    t -= 1
                if t < 1 / 6:
                    return p + (q - p) * 6 * t
                if t < 1 / 2:
                    return q
                if t < 2 / 3:
                    return p + (q - p) * (2 / 3 - t) * 6
                return p

            q = l * (1 + s) if l < 0.5 else l + s - l * s
            p = 2 * l - q
            r = hue2rgb(p, q, h + 1 / 3)
            g = hue2rgb(p, q, h)
            b = hue2rgb(p, q, h - 1 / 3)

        return int(round(r * 255)), int(round(g * 255)), int(round(b * 255))

    def _copy_value(self, var):
        content = var.get()
        if not content:
            self._set_status("没有可复制的内容", "warning")
            return

        self.clipboard_clear()
        self.clipboard_append(content)
        self.update()
        self._set_status("颜色值已复制到剪贴板", "success")

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
