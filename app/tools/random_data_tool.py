import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import string
import json
import csv
import io
from datetime import datetime, timedelta
from collections import OrderedDict

DATA_TYPES = OrderedDict([
    ("chinese_name", "中文姓名"),
    ("english_name", "英文名"),
    ("phone", "手机号"),
    ("email", "邮箱"),
    ("id_card", "身份证号"),
    ("company", "公司名"),
    ("datetime", "日期时间"),
    ("ip", "IP地址"),
    ("url", "URL"),
    ("custom", "自定义字符串"),
    ("integer", "整数"),
    ("float", "小数"),
])

TYPE_COLORS = {
    "chinese_name": "#e74c3c",
    "english_name": "#e67e22",
    "phone": "#f39c12",
    "email": "#27ae60",
    "id_card": "#1abc9c",
    "company": "#3498db",
    "datetime": "#9b59b6",
    "ip": "#34495e",
    "url": "#8e44ad",
    "custom": "#16a085",
    "integer": "#2c3e50",
    "float": "#d35400",
}


class RandomDataGenerator:
    def __init__(self, seed=None):
        self.random = random.Random(seed)

    def _reseed(self, seed):
        self.random = random.Random(seed)

    def generate_chinese_name(self, config=None):
        surnames = "赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜"
        given_chars = "伟芳娜敏静丽强磊军洋勇艳杰娟涛明超秀霞平刚桂英文华建国建华玉兰晓明红梅"
        surname = self.random.choice(surnames)
        given_len = self.random.choice([1, 2])
        given = "".join(self.random.choice(given_chars) for _ in range(given_len))
        return surname + given

    def generate_english_name(self, config=None):
        first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
                       "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
                       "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
                      "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
                      "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White"]
        return f"{self.random.choice(first_names)} {self.random.choice(last_names)}"

    def generate_phone(self, config=None):
        prefixes = ["130", "131", "132", "133", "134", "135", "136", "137", "138", "139",
                    "150", "151", "152", "153", "155", "156", "157", "158", "159",
                    "170", "171", "173", "175", "176", "177", "178",
                    "180", "181", "182", "183", "184", "185", "186", "187", "188", "189"]
        prefix = self.random.choice(prefixes)
        suffix = "".join(self.random.choice(string.digits) for _ in range(8))
        return prefix + suffix

    def generate_email(self, config=None):
        usernames = ["user", "admin", "test", "info", "contact", "support", "hello", "service",
                     "sales", "team", "dev", "manager", "ceo", "cto", "hr", "finance"]
        domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "qq.com",
                   "163.com", "126.com", "sina.com", "sohu.com", "foxmail.com",
                   "company.com", "example.com", "test.org", "mail.cn", "corp.net"]
        username = self.random.choice(usernames) + str(self.random.randint(100, 9999))
        domain = self.random.choice(domains)
        return f"{username}@{domain}"

    def generate_id_card(self, config=None):
        area_codes = ["110101", "110102", "310101", "310104", "440103", "440106",
                      "320102", "320106", "330102", "330106", "510104", "510107",
                      "420102", "420106", "610102", "610103", "370102", "370112"]
        area = self.random.choice(area_codes)
        start_year = 1950
        end_year = 2005
        year = self.random.randint(start_year, end_year)
        month = self.random.randint(1, 12)
        day = self.random.randint(1, 28)
        birth = f"{year:04d}{month:02d}{day:02d}"
        seq = f"{self.random.randint(1, 999):03d}"
        partial = area + birth + seq
        weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        check_chars = ["1", "0", "X", "9", "8", "7", "6", "5", "4", "3", "2"]
        total = sum(int(partial[i]) * weights[i] for i in range(17))
        check = check_chars[total % 11]
        return partial + check

    def generate_company(self, config=None):
        prefixes = ["华为", "中兴", "腾讯", "阿里", "百度", "字节", "美团", "京东",
                    "小米", "网易", "滴滴", "紫光", "浪潮", "联想", "方正", "东软"]
        suffixes = ["科技有限公司", "信息技术有限公司", "网络科技有限公司", "软件有限公司",
                    "电子有限公司", "通信技术有限公司", "数据服务有限公司", "云计算有限公司",
                    "智能科技有限公司", "互联网有限公司"]
        cities = ["北京", "上海", "广州", "深圳", "杭州", "南京", "成都", "武汉", "西安", "苏州"]
        prefix = self.random.choice(prefixes)
        city = self.random.choice(cities)
        suffix = self.random.choice(suffixes)
        use_city = self.random.choice([True, False])
        if use_city:
            return city + prefix + suffix
        return prefix + suffix

    def generate_datetime(self, config=None):
        config = config or {}
        start_str = config.get("start", "2020-01-01 00:00:00")
        end_str = config.get("end", "2025-12-31 23:59:59")
        try:
            start = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S")
            if end <= start:
                start, end = end, start
        except (ValueError, TypeError):
            start = datetime(2020, 1, 1)
            end = datetime(2025, 12, 31)
        delta = end - start
        random_seconds = self.random.randint(0, int(delta.total_seconds()))
        result = start + timedelta(seconds=random_seconds)
        format_str = config.get("format", "%Y-%m-%d %H:%M:%S")
        return result.strftime(format_str)

    def generate_ip(self, config=None):
        parts = [self.random.randint(1, 255) for _ in range(4)]
        parts[0] = self.random.choice([10, 172, 192, 203, 118, 114, 223, 36, 61])
        if parts[0] == 172:
            parts[1] = self.random.randint(16, 31)
        elif parts[0] == 192:
            parts[1] = 168
        return ".".join(str(p) for p in parts)

    def generate_url(self, config=None):
        protocols = ["https://", "http://"]
        subdomains = ["www.", "app.", "api.", "blog.", "m.", "shop.", "news.", ""]
        domains = ["baidu.com", "taobao.com", "jd.com", "qq.com", "sina.com.cn",
                   "sohu.com", "163.com", "csdn.net", "github.com", "example.com",
                   "test.org", "company.cn", "myapp.net", "dev.io"]
        paths = ["", "/index.html", "/about", "/contact", "/api/v1/users", "/products",
                 "/blog/post", "/login", "/register", "/search?q=test", "/category/123",
                 "/item/456.html", "/user/profile", "/docs/guide"]
        protocol = self.random.choice(protocols)
        subdomain = self.random.choice(subdomains)
        domain = self.random.choice(domains)
        path = self.random.choice(paths)
        return f"{protocol}{subdomain}{domain}{path}"

    def generate_custom(self, config=None):
        config = config or {}
        template = config.get("template", "TEST-{num}")
        result = template
        if "{num}" in result:
            num_digits = 6
            num = "".join(self.random.choice(string.digits) for _ in range(num_digits))
            result = result.replace("{num}", num)
        if "{uuid}" in result:
            import uuid
            result = result.replace("{uuid}", str(uuid.UUID(int=self.random.getrandbits(128))))
        if "{rand}" in result:
            rand_len = 8
            rand_str = "".join(self.random.choice(string.ascii_letters + string.digits) for _ in range(rand_len))
            result = result.replace("{rand}", rand_str)
        if "{date}" in result:
            dt = datetime(2020, 1, 1) + timedelta(days=self.random.randint(0, 2000))
            result = result.replace("{date}", dt.strftime("%Y%m%d"))
        if "{letter}" in result:
            letter = "".join(self.random.choice(string.ascii_uppercase) for _ in range(3))
            result = result.replace("{letter}", letter)
        return result

    def generate_integer(self, config=None):
        config = config or {}
        min_val = int(config.get("min", 0))
        max_val = int(config.get("max", 10000))
        if max_val < min_val:
            min_val, max_val = max_val, min_val
        return str(self.random.randint(min_val, max_val))

    def generate_float(self, config=None):
        config = config or {}
        min_val = float(config.get("min", 0.0))
        max_val = float(config.get("max", 100.0))
        decimal_places = int(config.get("decimal_places", 2))
        if max_val < min_val:
            min_val, max_val = max_val, min_val
        value = self.random.uniform(min_val, max_val)
        return f"{value:.{decimal_places}f}"

    def generate(self, col_type, config=None):
        generators = {
            "chinese_name": self.generate_chinese_name,
            "english_name": self.generate_english_name,
            "phone": self.generate_phone,
            "email": self.generate_email,
            "id_card": self.generate_id_card,
            "company": self.generate_company,
            "datetime": self.generate_datetime,
            "ip": self.generate_ip,
            "url": self.generate_url,
            "custom": self.generate_custom,
            "integer": self.generate_integer,
            "float": self.generate_float,
        }
        gen_func = generators.get(col_type)
        if gen_func:
            return gen_func(config)
        return ""


class ColumnConfigDialog(tk.Toplevel):
    def __init__(self, master, col_type, col_name="", col_config=None, on_save=None, on_cancel=None):
        super().__init__(master)
        self.col_type = col_type
        self.col_name_var = tk.StringVar(value=col_name or DATA_TYPES[col_type])
        self.col_config = dict(col_config) if col_config else {}
        self.on_save = on_save
        self.on_cancel = on_cancel

        self.title(f"配置列 - {DATA_TYPES[col_type]}")
        self.geometry("420x380")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self._setup_styles()
        self._create_widgets()
        self._center_window()

    def _setup_styles(self):
        style = ttk.Style()
        style.configure("Dialog.TLabel",
                        font=("Microsoft YaHei", 10),
                        background="#ffffff",
                        foreground="#2c3e50")
        style.configure("DialogTitle.TLabel",
                        font=("Microsoft YaHei", 12, "bold"),
                        background="#ffffff",
                        foreground="#2c3e50")
        style.configure("Dialog.TEntry",
                        font=("Consolas", 11),
                        padding=6)
        style.configure("Dialog.TButton",
                        font=("Microsoft YaHei", 10),
                        padding=8)
        style.configure("DialogPrimary.TButton",
                        font=("Microsoft YaHei", 10, "bold"),
                        padding=8,
                        background="#3498db",
                        foreground="white")
        style.map("DialogPrimary.TButton",
                  background=[("active", "#2980b9")])

    def _center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        container = tk.Frame(self, bg="#ffffff")
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        title = ttk.Label(container,
                          text=f"列配置 - {DATA_TYPES[self.col_type]}",
                          style="DialogTitle.TLabel")
        title.pack(anchor=tk.W, pady=(0, 15))

        sep = tk.Frame(container, bg="#ecf0f1", height=1)
        sep.pack(fill=tk.X, pady=(0, 15))

        form_frame = ttk.Frame(container)
        form_frame.pack(fill=tk.BOTH, expand=True)

        self._create_name_row(form_frame, 0)

        if self.col_type == "datetime":
            self._create_datetime_config(form_frame)
        elif self.col_type in ("integer", "float"):
            self._create_number_config(form_frame)
        elif self.col_type == "custom":
            self._create_custom_config(form_frame)

        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill=tk.X, pady=(20, 0))

        cancel_btn = ttk.Button(btn_frame,
                                text="取消",
                                style="Dialog.TButton",
                                command=self._on_cancel)
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))

        save_btn = ttk.Button(btn_frame,
                              text="确定",
                              style="DialogPrimary.TButton",
                              command=self._on_save)
        save_btn.pack(side=tk.RIGHT)

    def _create_name_row(self, parent, row):
        label = ttk.Label(parent, text="列名称:", style="Dialog.TLabel")
        label.grid(row=row, column=0, sticky=tk.W, pady=8)

        entry = ttk.Entry(parent,
                          textvariable=self.col_name_var,
                          style="Dialog.TEntry",
                          width=35)
        entry.grid(row=row, column=1, sticky=tk.EW, pady=8, padx=(15, 0))

        parent.grid_columnconfigure(1, weight=1)

    def _create_datetime_config(self, parent):
        self.start_var = tk.StringVar(value=self.col_config.get("start", "2020-01-01 00:00:00"))
        self.end_var = tk.StringVar(value=self.col_config.get("end", "2025-12-31 23:59:59"))
        self.format_var = tk.StringVar(value=self.col_config.get("format", "%Y-%m-%d %H:%M:%S"))

        labels = [
            ("开始时间:", self.start_var, "%Y-%m-%d %H:%M:%S"),
            ("结束时间:", self.end_var, "%Y-%m-%d %H:%M:%S"),
            ("格式模板:", self.format_var, "%Y-%m-%d %H:%M:%S"),
        ]

        for i, (lbl, var, hint) in enumerate(labels, start=1):
            ttk.Label(parent, text=lbl, style="Dialog.TLabel").grid(row=i, column=0, sticky=tk.W, pady=8)
            entry = ttk.Entry(parent, textvariable=var, style="Dialog.TEntry", width=35)
            entry.grid(row=i, column=1, sticky=tk.EW, pady=8, padx=(15, 0))

        hint_lbl = ttk.Label(parent,
                             text="提示: 格式符 %Y年 %m月 %d日 %H时 %M分 %S秒",
                             style="Dialog.TLabel",
                             foreground="#7f8c8d",
                             font=("Microsoft YaHei", 9))
        hint_lbl.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))

    def _create_number_config(self, parent):
        if self.col_type == "integer":
            default_min, default_max = "0", "10000"
        else:
            default_min, default_max = "0.0", "100.0"

        self.min_var = tk.StringVar(value=str(self.col_config.get("min", default_min)))
        self.max_var = tk.StringVar(value=str(self.col_config.get("max", default_max)))

        labels = [("最小值:", self.min_var), ("最大值:", self.max_var)]
        for i, (lbl, var) in enumerate(labels, start=1):
            ttk.Label(parent, text=lbl, style="Dialog.TLabel").grid(row=i, column=0, sticky=tk.W, pady=8)
            entry = ttk.Entry(parent, textvariable=var, style="Dialog.TEntry", width=35)
            entry.grid(row=i, column=1, sticky=tk.EW, pady=8, padx=(15, 0))

        if self.col_type == "float":
            self.decimal_var = tk.StringVar(value=str(self.col_config.get("decimal_places", "2")))
            ttk.Label(parent, text="小数位数:", style="Dialog.TLabel").grid(row=3, column=0, sticky=tk.W, pady=8)
            entry = ttk.Entry(parent, textvariable=self.decimal_var, style="Dialog.TEntry", width=35)
            entry.grid(row=3, column=1, sticky=tk.EW, pady=8, padx=(15, 0))

    def _create_custom_config(self, parent):
        self.template_var = tk.StringVar(value=self.col_config.get("template", "XX-{num}-XX"))

        ttk.Label(parent, text="模板:", style="Dialog.TLabel").grid(row=1, column=0, sticky=tk.W, pady=8)
        entry = ttk.Entry(parent, textvariable=self.template_var, style="Dialog.TEntry", width=35)
        entry.grid(row=1, column=1, sticky=tk.EW, pady=8, padx=(15, 0))

        hint_lbl = ttk.Label(parent,
                             text="可用占位符: {num}数字 {rand}字母数字 {date}日期 {letter}字母 {uuid}",
                             style="Dialog.TLabel",
                             foreground="#7f8c8d",
                             font=("Microsoft YaHei", 9),
                             wraplength=380,
                             justify=tk.LEFT)
        hint_lbl.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))

    def _on_save(self):
        name = self.col_name_var.get().strip()
        if not name:
            messagebox.showwarning("提示", "列名称不能为空", parent=self)
            return

        config = {}
        if self.col_type == "datetime":
            config["start"] = self.start_var.get().strip()
            config["end"] = self.end_var.get().strip()
            config["format"] = self.format_var.get().strip()
        elif self.col_type == "integer":
            try:
                int(self.min_var.get())
                int(self.max_var.get())
            except ValueError:
                messagebox.showwarning("提示", "最小值和最大值必须为整数", parent=self)
                return
            config["min"] = self.min_var.get().strip()
            config["max"] = self.max_var.get().strip()
        elif self.col_type == "float":
            try:
                float(self.min_var.get())
                float(self.max_var.get())
                int(self.decimal_var.get())
            except ValueError:
                messagebox.showwarning("提示", "请输入有效的数值", parent=self)
                return
            config["min"] = self.min_var.get().strip()
            config["max"] = self.max_var.get().strip()
            config["decimal_places"] = self.decimal_var.get().strip()
        elif self.col_type == "custom":
            config["template"] = self.template_var.get().strip()

        if self.on_save:
            self.on_save(name, config)
        self.destroy()

    def _on_cancel(self):
        if self.on_cancel:
            self.on_cancel()
        self.destroy()


class RandomDataTool(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, style="Content.TFrame")
        self.columns = []
        self.data = []
        self.sort_column = None
        self.sort_ascending = True
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
                        font=("Microsoft YaHei", 9),
                        padding=4,
                        background="#e74c3c",
                        foreground="white")
        style.map("Danger.TButton",
                  background=[("active", "#c0392b")])
        style.configure("Status.TLabel",
                        font=("Microsoft YaHei", 10),
                        background="#f5f6fa")

    def _create_widgets(self):
        title_label = ttk.Label(self,
                                text="随机数据生成",
                                style="ToolTitle.TLabel")
        title_label.pack(anchor=tk.W, pady=(0, 15))

        main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)

        self._create_left_panel(main_paned)
        self._create_right_panel(main_paned)
        self._create_data_table(main_paned)

        main_paned.add(self.left_frame, weight=2)
        main_paned.add(self.right_frame, weight=3)

        self._create_status_area()

    def _create_left_panel(self, parent):
        self.left_frame = ttk.Frame(parent, style="Content.TFrame")

        section_lbl = ttk.Label(self.left_frame,
                                text="数据列配置",
                                style="Section.TLabel")
        section_lbl.pack(anchor=tk.W, pady=(0, 10))

        list_container = ttk.Frame(self.left_frame)
        list_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.col_canvas = tk.Canvas(list_container,
                                    bg="white",
                                    highlightthickness=1,
                                    highlightbackground="#bdc3c7",
                                    borderwidth=0)
        self.col_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        col_scroll = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.col_canvas.yview)
        col_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.col_canvas.configure(yscrollcommand=col_scroll.set)

        self.col_list_inner = tk.Frame(self.col_canvas, bg="white")
        self.col_canvas_window = self.col_canvas.create_window((0, 0), window=self.col_list_inner, anchor=tk.NW)
        self.col_list_inner.bind("<Configure>", self._on_col_list_configure)
        self.col_canvas.bind("<Configure>", lambda e: self.col_canvas.itemconfigure(self.col_canvas_window, width=e.width))

        self._refresh_column_list()

        add_container = ttk.Frame(self.left_frame)
        add_container.pack(fill=tk.X, pady=(0, 5))

        self.add_btn = ttk.Button(add_container,
                                  text=" 添加列 ▾",
                                  style="Primary.TButton",
                                  command=self._show_add_menu)
        self.add_btn.pack(fill=tk.X)

        self.add_menu = tk.Menu(self, tearoff=0)
        for type_key, type_name in DATA_TYPES.items():
            self.add_menu.add_command(label=type_name, command=lambda k=type_key: self._add_column(k))

        count_lbl = ttk.Label(self.left_frame,
                              text="",
                              style="Status.TLabel")
        count_lbl.pack(anchor=tk.W, pady=(5, 0))
        self.column_count_label = count_lbl
        self._update_column_count()

    def _on_col_list_configure(self, event):
        self.col_canvas.configure(scrollregion=self.col_canvas.bbox("all"))

    def _refresh_column_list(self):
        for w in self.col_list_inner.winfo_children():
            w.destroy()

        if not self.columns:
            empty_lbl = tk.Label(self.col_list_inner,
                                 text="  暂无列，请点击\"添加列\"按钮",
                                 font=("Microsoft YaHei", 10),
                                 bg="white",
                                 fg="#95a5a6",
                                 pady=20)
            empty_lbl.pack(fill=tk.X)
            return

        for idx, col in enumerate(self.columns):
            self._create_column_item(idx, col)

    def _create_column_item(self, idx, col):
        item_frame = tk.Frame(self.col_list_inner, bg="white", padx=8, pady=6)
        item_frame.pack(fill=tk.X, padx=5, pady=3)

        type_color = TYPE_COLORS.get(col["type"], "#7f8c8d")
        type_tag = tk.Label(item_frame,
                            text=f" {DATA_TYPES[col['type']]} ",
                            font=("Microsoft YaHei", 9, "bold"),
                            bg=type_color,
                            fg="white",
                            padx=6,
                            pady=2)
        type_tag.pack(side=tk.LEFT)

        name_lbl = tk.Label(item_frame,
                            text=col["name"],
                            font=("Microsoft YaHei", 10),
                            bg="white",
                            fg="#2c3e50",
                            padx=8,
                            anchor=tk.W)
        name_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)

        edit_btn = tk.Label(item_frame,
                            text="⚙",
                            font=("Microsoft YaHei", 12),
                            bg="white",
                            fg="#3498db",
                            cursor="hand2")
        edit_btn.pack(side=tk.LEFT, padx=3)
        edit_btn.bind("<Button-1>", lambda e, i=idx: self._edit_column(i))

        del_btn = tk.Label(item_frame,
                           text="✕",
                           font=("Microsoft YaHei", 12, "bold"),
                           bg="white",
                           fg="#e74c3c",
                           cursor="hand2")
        del_btn.pack(side=tk.LEFT, padx=3)
        del_btn.bind("<Button-1>", lambda e, i=idx: self._delete_column(i))

    def _show_add_menu(self):
        x = self.add_btn.winfo_rootx()
        y = self.add_btn.winfo_rooty() + self.add_btn.winfo_height()
        self.add_menu.tk_popup(x, y)

    def _add_column(self, col_type):
        def on_save(name, config):
            self.columns.append({
                "type": col_type,
                "name": name,
                "config": config,
            })
            self._refresh_column_list()
            self._update_column_count()
            self._set_status(f"已添加列: {name}", "success")

        ColumnConfigDialog(self, col_type=col_type, on_save=on_save)

    def _edit_column(self, idx):
        col = self.columns[idx]

        def on_save(name, config):
            self.columns[idx]["name"] = name
            self.columns[idx]["config"] = config
            self._refresh_column_list()
            self._update_column_count()
            self._set_status(f"已更新列: {name}", "success")

        ColumnConfigDialog(self,
                           col_type=col["type"],
                           col_name=col["name"],
                           col_config=col["config"],
                           on_save=on_save)

    def _delete_column(self, idx):
        col = self.columns[idx]
        if not messagebox.askyesno("确认删除", f"确定要删除列 \"{col['name']}\" 吗？"):
            return
        del self.columns[idx]
        self._refresh_column_list()
        self._update_column_count()
        self._set_status(f"已删除列: {col['name']}", "info")

    def _update_column_count(self):
        self.column_count_label.configure(text=f"共 {len(self.columns)} 列")

    def _create_right_panel(self, parent):
        self.right_frame = ttk.Frame(parent, style="Content.TFrame")

        config_section = ttk.LabelFrame(self.right_frame,
                                        text=" 生成配置 ",
                                        style="Content.TFrame",
                                        padding=15)
        config_section.pack(fill=tk.X, pady=(0, 15))

        row1 = ttk.Frame(config_section, style="Content.TFrame")
        row1.pack(fill=tk.X, pady=5)

        ttk.Label(row1, text="生成条数:", style="SubSection.TLabel", width=10).pack(side=tk.LEFT)
        self.count_var = tk.IntVar(value=100)
        self.count_spin = ttk.Spinbox(row1,
                                      from_=1,
                                      to=1000,
                                      textvariable=self.count_var,
                                      width=15,
                                      font=("Consolas", 11))
        self.count_spin.pack(side=tk.LEFT, padx=(10, 0))

        row2 = ttk.Frame(config_section, style="Content.TFrame")
        row2.pack(fill=tk.X, pady=5)

        ttk.Label(row2, text="随机种子:", style="SubSection.TLabel", width=10).pack(side=tk.LEFT)
        self.seed_var = tk.StringVar()
        self.seed_entry = ttk.Entry(row2,
                                    textvariable=self.seed_var,
                                    font=("Consolas", 11),
                                    width=20)
        self.seed_entry.pack(side=tk.LEFT, padx=(10, 0))

        seed_hint = ttk.Label(config_section,
                              text="(留空则使用系统随机种子，指定种子可复现相同数据)",
                              style="Status.TLabel",
                              foreground="#7f8c8d",
                              font=("Microsoft YaHei", 9))
        seed_hint.pack(anchor=tk.W, padx=(80, 0), pady=(2, 5))

        btn_section = ttk.Frame(self.right_frame, style="Content.TFrame")
        btn_section.pack(fill=tk.X, pady=(0, 15))

        preview_btn = ttk.Button(btn_section,
                                 text="预览 (5条)",
                                 style="Action.TButton",
                                 command=self._preview_data)
        preview_btn.pack(side=tk.LEFT, padx=(0, 10))

        generate_btn = ttk.Button(btn_section,
                                  text="批量生成",
                                  style="Success.TButton",
                                  command=self._generate_data)
        generate_btn.pack(side=tk.LEFT)

        preview_section = ttk.LabelFrame(self.right_frame,
                                         text=" 数据预览 ",
                                         style="Content.TFrame",
                                         padding=10)
        preview_section.pack(fill=tk.BOTH, expand=True)

        preview_container = ttk.Frame(preview_section)
        preview_container.pack(fill=tk.BOTH, expand=True)

        self.preview_tree = ttk.Treeview(preview_container, show="headings", height=8)
        self.preview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        preview_scroll_y = ttk.Scrollbar(preview_container, orient=tk.VERTICAL, command=self.preview_tree.yview)
        preview_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_tree.configure(yscrollcommand=preview_scroll_y.set)

        preview_scroll_x = ttk.Scrollbar(preview_section, orient=tk.HORIZONTAL, command=self.preview_tree.xview)
        preview_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.preview_tree.configure(xscrollcommand=preview_scroll_x.set)

        self._init_tree_style(self.preview_tree)

    def _init_tree_style(self, tree):
        style = ttk.Style()
        style.configure("Data.Treeview",
                        font=("Consolas", 10),
                        rowheight=28,
                        background="white",
                        fieldbackground="white")
        style.configure("Data.Treeview.Heading",
                        font=("Microsoft YaHei", 10, "bold"),
                        padding=6)
        tree.configure(style="Data.Treeview")

    def _create_data_table(self, parent):
        self.table_frame = ttk.Frame(self, style="Content.TFrame")
        self.table_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))

        action_bar = ttk.Frame(self.table_frame, style="Content.TFrame")
        action_bar.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(action_bar,
                  text=" 生成结果：",
                  style="Section.TLabel").pack(side=tk.LEFT)

        self.data_count_label = ttk.Label(action_bar,
                                          text="(0 条)",
                                          style="Status.TLabel",
                                          foreground="#7f8c8d")
        self.data_count_label.pack(side=tk.LEFT, padx=(5, 15))

        self.copy_json_btn = ttk.Button(action_bar,
                                        text="复制 JSON",
                                        style="Action.TButton",
                                        command=self._copy_json,
                                        state=tk.DISABLED)
        self.copy_json_btn.pack(side=tk.RIGHT, padx=5)

        self.export_sql_btn = ttk.Button(action_bar,
                                         text="导出 SQL INSERT",
                                         style="Action.TButton",
                                         command=self._export_sql,
                                         state=tk.DISABLED)
        self.export_sql_btn.pack(side=tk.RIGHT, padx=5)

        self.export_csv_btn = ttk.Button(action_bar,
                                         text="导出 CSV",
                                         style="Action.TButton",
                                         command=self._export_csv,
                                         state=tk.DISABLED)
        self.export_csv_btn.pack(side=tk.RIGHT, padx=5)

        table_container = ttk.Frame(self.table_frame)
        table_container.pack(fill=tk.BOTH, expand=True)

        self.data_tree = ttk.Treeview(table_container, show="headings")
        self.data_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll_y = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.data_tree.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.data_tree.configure(yscrollcommand=scroll_y.set)

        scroll_x = ttk.Scrollbar(self.table_frame, orient=tk.HORIZONTAL, command=self.data_tree.xview)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.data_tree.configure(xscrollcommand=scroll_x.set)

        self._init_tree_style(self.data_tree)

    def _get_seed(self):
        seed_str = self.seed_var.get().strip()
        if seed_str:
            try:
                return int(seed_str)
            except ValueError:
                return seed_str
        return None

    def _validate_columns(self):
        if not self.columns:
            messagebox.showwarning("提示", "请先添加至少一个数据列")
            return False
        return True

    def _setup_tree_columns(self, tree, clear=True):
        if clear:
            for col in tree.get_children():
                tree.delete(col)

        col_ids = [f"col_{i}" for i in range(len(self.columns))]
        tree.configure(columns=col_ids)

        for i, col in enumerate(self.columns):
            col_id = f"col_{i}"
            tree.heading(col_id,
                         text=col["name"],
                         command=lambda c=i: self._sort_column(c))
            tree.column(col_id, width=150, minwidth=80, anchor=tk.W, stretch=True)

    def _generate_rows(self, count):
        seed = self._get_seed()
        gen = RandomDataGenerator(seed)
        rows = []
        for _ in range(count):
            row = []
            for col in self.columns:
                value = gen.generate(col["type"], col.get("config"))
                row.append(value)
            rows.append(row)
        return rows

    def _preview_data(self):
        if not self._validate_columns():
            return
        self._setup_tree_columns(self.preview_tree)
        rows = self._generate_rows(5)
        for row in rows:
            self.preview_tree.insert("", tk.END, values=row)
        self._set_status("预览数据已生成", "success")

    def _generate_data(self):
        if not self._validate_columns():
            return
        count = self.count_var.get()
        if count < 1 or count > 1000:
            messagebox.showwarning("提示", "生成条数必须在 1-1000 之间")
            return

        self.data = self._generate_rows(count)
        self.sort_column = None
        self._setup_tree_columns(self.data_tree)
        self._populate_data_tree()

        self.copy_json_btn.configure(state=tk.NORMAL)
        self.export_csv_btn.configure(state=tk.NORMAL)
        self.export_sql_btn.configure(state=tk.NORMAL)
        self.data_count_label.configure(text=f"({len(self.data)} 条)")
        self._set_status(f"成功生成 {len(self.data)} 条数据", "success")

    def _populate_data_tree(self):
        for col in self.data_tree.get_children():
            self.data_tree.delete(col)
        for row in self.data:
            self.data_tree.insert("", tk.END, values=row)

    def _sort_column(self, col_idx):
        if not self.data:
            return
        if self.sort_column == col_idx:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_column = col_idx
            self.sort_ascending = True

        def sort_key(row):
            val = row[col_idx]
            try:
                return (0, float(val))
            except (ValueError, TypeError):
                return (1, str(val))

        self.data.sort(key=sort_key, reverse=not self.sort_ascending)
        self._populate_data_tree()

        arrow = " ▲" if self.sort_ascending else " ▼"
        for i, col in enumerate(self.columns):
            col_id = f"col_{i}"
            header_text = col["name"]
            if i == col_idx:
                header_text += arrow
            self.data_tree.heading(col_id, text=header_text)

    def _build_list_of_dicts(self):
        return [
            {col["name"]: row[i] for i, col in enumerate(self.columns)}
            for row in self.data
        ]

    def _copy_json(self):
        if not self.data:
            return
        data_list = self._build_list_of_dicts()
        json_str = json.dumps(data_list, ensure_ascii=False, indent=2)
        self.clipboard_clear()
        self.clipboard_append(json_str)
        self.update()
        self._set_status(f"JSON 数据已复制到剪贴板 ({len(self.data)} 条)", "success")

    def _export_csv(self):
        if not self.data:
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV 文件", "*.csv"), ("所有文件", "*.*")],
            initialfile=f"random_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        if not file_path:
            return
        try:
            with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow([col["name"] for col in self.columns])
                writer.writerows(self.data)
            self._set_status(f"CSV 已导出到: {file_path}", "success")
            messagebox.showinfo("导出成功", f"CSV 文件已保存到:\n{file_path}")
        except Exception as e:
            self._set_status(f"导出失败: {str(e)}", "error")
            messagebox.showerror("导出失败", str(e))

    def _export_sql(self):
        if not self.data:
            return

        table_name = "random_data"

        def sql_dialog():
            dialog = tk.Toplevel(self)
            dialog.title("导出 SQL INSERT")
            dialog.geometry("400x200")
            dialog.transient(self)
            dialog.grab_set()

            tk.Label(dialog, text="表名:", font=("Microsoft YaHei", 10)).pack(anchor=tk.W, padx=20, pady=(20, 5))
            table_var = tk.StringVar(value=table_name)
            entry = ttk.Entry(dialog, textvariable=table_var, font=("Consolas", 11), width=30)
            entry.pack(padx=20, pady=5)
            entry.select_range(0, tk.END)
            entry.focus_set()

            btn_frame = ttk.Frame(dialog)
            btn_frame.pack(pady=20)

            result = {"value": None}

            def on_ok():
                result["value"] = table_var.get().strip()
                dialog.destroy()

            def on_cancel():
                dialog.destroy()

            ttk.Button(btn_frame, text="取消", command=on_cancel, width=10).pack(side=tk.LEFT, padx=10)
            ttk.Button(btn_frame, text="确定", command=on_ok, width=10).pack(side=tk.LEFT, padx=10)

            dialog.wait_window()
            return result["value"]

        table = sql_dialog()
        if not table:
            return
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table):
            messagebox.showerror("错误", "表名不合法，只能包含字母、数字和下划线")
            return

        columns_sql = ", ".join(f"`{col['name']}`" for col in self.columns)
        sql_lines = []
        for row in self.data:
            values_sql = ", ".join(self._sql_escape(v) for v in row)
            sql_lines.append(f"INSERT INTO `{table}` ({columns_sql}) VALUES ({values_sql});")

        full_sql = "\n".join(sql_lines)

        file_path = filedialog.asksaveasfilename(
            defaultextension=".sql",
            filetypes=[("SQL 文件", "*.sql"), ("所有文件", "*.*")],
            initialfile=f"{table}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        )
        if not file_path:
            return
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(full_sql)
            self._set_status(f"SQL 已导出到: {file_path}", "success")
            messagebox.showinfo("导出成功", f"SQL 文件已保存到:\n{file_path}")
        except Exception as e:
            self._set_status(f"导出失败: {str(e)}", "error")
            messagebox.showerror("导出失败", str(e))

    def _sql_escape(self, value):
        if value is None:
            return "NULL"
        s = str(value)
        s = s.replace("\\", "\\\\")
        s = s.replace("'", "\\'")
        s = s.replace('"', '\\"')
        s = s.replace("\x00", "\\0")
        s = s.replace("\n", "\\n")
        s = s.replace("\r", "\\r")
        return f"'{s}'"

    def _create_status_area(self):
        status_frame = ttk.Frame(self, style="Content.TFrame")
        status_frame.pack(fill=tk.X, pady=(10, 0))

        self.status_label = ttk.Label(status_frame,
                                      text="就绪",
                                      style="Status.TLabel")
        self.status_label.pack(anchor=tk.W)

    def _set_status(self, message, status_type="info"):
        colors = {
            "success": "#27ae60",
            "error": "#e74c3c",
            "warning": "#f39c12",
            "info": "#3498db"
        }
        color = colors.get(status_type, "#34495e")
        self.status_label.configure(text=message, foreground=color)

