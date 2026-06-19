import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog, colorchooser
import uuid
import time
import copy
from PIL import Image, ImageDraw, ImageFont
import io

from app.tools.mindmap_storage import MindMapStorage


NODE_COLORS = [
    "#3498db", "#2ecc71", "#e74c3c", "#f39c12", "#9b59b6",
    "#1abc9c", "#34495e", "#e67e22", "#16a085", "#8e44ad"
]

NODE_ICONS = ["⭐", "🔥", "💡", "📌", "✅", "❌", "⚠️", "🎯", "🚀", "❤️", "📝", "📊"]

PRESET_PROJECTS = ["全部", "默认项目", "产品规划", "技术方案", "会议纪要", "学习笔记"]


class MindMapTool(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, style="Content.TFrame")
        self.storage = MindMapStorage()
        self._setup_styles()
        self._create_main_widgets()
        self._show_list_view()

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
        style.configure("Card.TFrame",
                        background="white",
                        relief=tk.RAISED,
                        borderwidth=1)
        style.configure("CardTitle.TLabel",
                        font=("Microsoft YaHei", 12, "bold"),
                        background="white",
                        foreground="#2c3e50")
        style.configure("CardMeta.TLabel",
                        font=("Microsoft YaHei", 9),
                        background="white",
                        foreground="#7f8c8d")
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
                        padding=6,
                        background="#e74c3c",
                        foreground="white")
        style.map("Danger.TButton",
                  background=[("active", "#c0392b")])
        style.configure("Action.TButton",
                        font=("Microsoft YaHei", 10),
                        padding=6)
        style.configure("Toolbar.TButton",
                        font=("Microsoft YaHei", 10),
                        padding=4)
        style.configure("Status.TLabel",
                        font=("Microsoft YaHei", 10),
                        background="#f5f6fa")

    def _create_main_widgets(self):
        self.main_container = ttk.Frame(self, style="Content.TFrame")
        self.main_container.pack(fill=tk.BOTH, expand=True)

    def _clear_main(self):
        for w in self.main_container.winfo_children():
            w.destroy()

    # ==================== 列表页面 ====================
    def _show_list_view(self):
        self._clear_main()
        self.list_view = MindMapListView(self.main_container, self)
        self.list_view.pack(fill=tk.BOTH, expand=True)

    def open_map_editor(self, map_data=None, is_new=False):
        self._clear_main()
        self.editor_view = MindMapEditorView(self.main_container, self, map_data, is_new)
        self.editor_view.pack(fill=tk.BOTH, expand=True)

    def back_to_list(self):
        self._show_list_view()


class MindMapListView(ttk.Frame):
    def __init__(self, master, parent_tool):
        super().__init__(master, style="Content.TFrame")
        self.parent = parent_tool
        self.storage = parent_tool.storage
        self._create_widgets()
        self._refresh_list()

    def _create_widgets(self):
        header = ttk.Frame(self, style="Content.TFrame")
        header.pack(fill=tk.X, pady=(0, 15))

        title_label = ttk.Label(header,
                                text="思维导图",
                                style="ToolTitle.TLabel")
        title_label.pack(side=tk.LEFT)

        new_btn = ttk.Button(header,
                             text="  +  新建导图  ",
                             style="Primary.TButton",
                             command=self._create_new_map)
        new_btn.pack(side=tk.RIGHT)

        filter_frame = ttk.Frame(self, style="Content.TFrame")
        filter_frame.pack(fill=tk.X, pady=(0, 15))

        search_label = ttk.Label(filter_frame,
                                 text="搜索：",
                                 style="Section.TLabel")
        search_label.pack(side=tk.LEFT)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self._refresh_list())
        search_entry = ttk.Entry(filter_frame,
                                 textvariable=self.search_var,
                                 width=25,
                                 font=("Microsoft YaHei", 10))
        search_entry.pack(side=tk.LEFT, padx=(5, 20))

        project_label = ttk.Label(filter_frame,
                                  text="项目：",
                                  style="Section.TLabel")
        project_label.pack(side=tk.LEFT)

        self.project_var = tk.StringVar(value="全部")
        projects = self._get_projects()
        self.project_combo = ttk.Combobox(filter_frame,
                                          textvariable=self.project_var,
                                          values=projects,
                                          state="readonly",
                                          width=15,
                                          font=("Microsoft YaHei", 10))
        self.project_combo.pack(side=tk.LEFT, padx=(5, 0))
        self.project_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_list())

        self.canvas_frame = ttk.Frame(self, style="Content.TFrame")
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.h_scroll = ttk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        self.v_scroll = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.cards_canvas = tk.Canvas(self.canvas_frame,
                                      bg="#f5f6fa",
                                      highlightthickness=0,
                                      xscrollcommand=self.h_scroll.set,
                                      yscrollcommand=self.v_scroll.set)
        self.cards_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.h_scroll.config(command=self.cards_canvas.xview)
        self.v_scroll.config(command=self.cards_canvas.yview)

        self.cards_inner = ttk.Frame(self.cards_canvas, style="Content.TFrame")
        self.cards_window = self.cards_canvas.create_window((0, 0),
                                                            window=self.cards_inner,
                                                            anchor="nw")

        self.cards_inner.bind("<Configure>",
                              lambda e: self.cards_canvas.configure(scrollregion=self.cards_canvas.bbox("all")))
        self.cards_canvas.bind("<Configure>",
                               lambda e: self.cards_canvas.itemconfigure(self.cards_window, width=e.width))

        self.cards_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _get_projects(self):
        stored = self.storage.list_projects()
        all_projects = list(set(PRESET_PROJECTS + stored))
        if "全部" not in all_projects:
            all_projects.insert(0, "全部")
        return all_projects

    def _on_mousewheel(self, event):
        self.cards_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _refresh_list(self):
        for w in self.cards_inner.winfo_children():
            w.destroy()

        project_filter = self.project_var.get()
        search_query = self.search_var.get()
        maps = self.storage.list_maps(project_filter=project_filter,
                                      search_query=search_query)

        if not maps:
            empty_frame = ttk.Frame(self.cards_inner, style="Content.TFrame")
            empty_frame.pack(fill=tk.BOTH, expand=True, pady=80)

            empty_label = ttk.Label(empty_frame,
                                    text="还没有思维导图\n点击右上角「新建导图」开始创建",
                                    font=("Microsoft YaHei", 14),
                                    background="#f5f6fa",
                                    foreground="#95a5a6",
                                    justify=tk.CENTER)
            empty_label.pack()
            return

        cols = 3
        for i, m in enumerate(maps):
            row, col = divmod(i, cols)
            card = MindMapCard(self.cards_inner, self, m)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        for c in range(cols):
            self.cards_inner.grid_columnconfigure(c, weight=1, uniform="col")

    def _create_new_map(self):
        NewMapDialog(self, self._on_map_created)

    def _on_map_created(self, title, project):
        map_data = self.storage.create_map(title=title, project=project)
        self.parent.open_map_editor(map_data, is_new=True)

    def _edit_map(self, map_id):
        map_data = self.storage.get_map(map_id)
        if map_data:
            self.parent.open_map_editor(map_data, is_new=False)

    def _delete_map(self, map_id, title):
        if messagebox.askyesno("确认删除", f"确定要删除思维导图「{title}」吗？\n此操作不可恢复！"):
            self.storage.delete_map(map_id)
            self._refresh_list()


class MindMapCard(ttk.Frame):
    def __init__(self, master, list_view, map_info):
        super().__init__(master, style="Card.TFrame")
        self.list_view = list_view
        self.map_info = map_info
        self.map_id = map_info["id"]
        self._create_widgets()
        self._bind_events()

    def _create_widgets(self):
        self.configure(padding=12)

        thumb = MindMapThumbnail(self, self.map_id, width=240, height=130,
                                 bg="#ecf0f1")
        thumb.pack(fill=tk.X, pady=(0, 10))

        title = self.map_info.get("title", "未命名导图")
        if len(title) > 18:
            title = title[:18] + "..."
        title_label = ttk.Label(self,
                                text=title,
                                style="CardTitle.TLabel")
        title_label.pack(anchor=tk.W)

        meta_frame = ttk.Frame(self, background="white")
        meta_frame.pack(fill=tk.X, pady=(8, 0))

        project = self.map_info.get("project", "默认项目")
        proj_label = ttk.Label(meta_frame,
                               text=f"📁 {project}",
                               style="CardMeta.TLabel",
                               background="white")
        proj_label.pack(side=tk.LEFT)

        creator = self.map_info.get("creator", "-")
        creator_label = ttk.Label(meta_frame,
                                  text=f"👤 {creator}",
                                  style="CardMeta.TLabel",
                                  background="white")
        creator_label.pack(side=tk.LEFT, padx=(10, 0))

        updated = MindMapStorage.format_timestamp(self.map_info.get("updated_at", time.time()))
        time_label = ttk.Label(self,
                               text=f"🕐 {updated}",
                               style="CardMeta.TLabel",
                               background="white")
        time_label.pack(anchor=tk.W, pady=(4, 10))

        btn_frame = ttk.Frame(self, background="white")
        btn_frame.pack(fill=tk.X)

        open_btn = ttk.Button(btn_frame,
                              text="编辑",
                              style="Primary.TButton",
                              command=self._on_open)
        open_btn.pack(side=tk.LEFT)

        del_btn = ttk.Button(btn_frame,
                             text="删除",
                             style="Danger.TButton",
                             command=self._on_delete)
        del_btn.pack(side=tk.RIGHT)

    def _bind_events(self):
        for widget in [self] + self.winfo_children():
            widget.bind("<Double-Button-1>", lambda e: self._on_open())
            if isinstance(widget, tk.Canvas):
                for child in widget.find_all():
                    widget.tag_bind(child, "<Double-Button-1>", lambda e: self._on_open())

    def _on_open(self):
        self.list_view._edit_map(self.map_id)

    def _on_delete(self):
        title = self.map_info.get("title", "未命名导图")
        self.list_view._delete_map(self.map_id, title)


class MindMapThumbnail(tk.Canvas):
    def __init__(self, master, map_id, **kwargs):
        super().__init__(master, **kwargs)
        self.map_id = map_id
        self.storage = MindMapStorage()
        self.bind("<Configure>", lambda e: self._draw_thumbnail())
        self.after(50, self._draw_thumbnail)

    def _draw_thumbnail(self):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 10 or h < 10:
            return

        map_data = self.storage.get_map(self.map_id)
        if not map_data:
            self.create_rectangle(5, 5, w - 5, h - 5,
                                  fill="#dfe6e9", outline="#b2bec3", width=2)
            self.create_text(w // 2, h // 2, text="无数据",
                             font=("Microsoft YaHei", 10), fill="#636e72")
            return

        root = map_data.get("root")
        if not root:
            return

        cx, cy = w // 2, h // 2
        scale = min(w, h) / 400
        self._draw_node_thumbnail(root, cx, cy, scale, 0, 0)

    def _draw_node_thumbnail(self, node, cx, cy, scale, depth, side):
        color = node.get("color", "#3498db")
        text = node.get("text", "")
        if len(text) > 6:
            text = text[:6] + ".."

        if depth == 0:
            rw, rh = 70 * scale, 30 * scale
            x1, y1 = cx - rw / 2, cy - rh / 2
            x2, y2 = cx + rw / 2, cy + rh / 2
            self.create_rounded_rect(x1, y1, x2, y2, radius=6 * scale,
                                     fill=color, outline="")
            self.create_text(cx, cy, text=text,
                             font=("Microsoft YaHei", max(7, int(9 * scale))),
                             fill="white")

            children = node.get("children", [])
            n = len(children)
            for i, ch in enumerate(children):
                ch_side = -1 if i % 2 == 0 else 1
                angle = ((i // 2) + 1) * 35
                import math
                rad = math.radians(angle)
                dist = 80 * scale
                ch_x = cx + ch_side * math.cos(rad) * dist
                ch_y = cy + math.sin(rad) * dist * 0.6

                self.create_line(cx + rw / 2 * ch_side, cy,
                                 ch_x, ch_y,
                                 fill=color, width=max(1, 2 * scale),
                                 smooth=True)
                self._draw_node_thumbnail(ch, ch_x, ch_y, scale * 0.9,
                                          depth + 1, ch_side)
        else:
            rw, rh = 50 * scale, 22 * scale
            x1, y1 = cx - rw / 2, cy - rh / 2
            x2, y2 = cx + rw / 2, cy + rh / 2
            self.create_rounded_rect(x1, y1, x2, y2, radius=5 * scale,
                                     fill=color, outline="", stipple="gray50")
            self.create_text(cx, cy, text=text,
                             font=("Microsoft YaHei", max(6, int(7 * scale))),
                             fill="white")

            children = node.get("children", [])[:2]
            for i, ch in enumerate(children):
                dist = 55 * scale
                ch_x = cx + (1 if side >= 0 else -1) * dist
                ch_y = cy + (i - 0.5) * 30 * scale
                self.create_line(cx + rw / 2 * (1 if side >= 0 else -1), cy,
                                 ch_x, ch_y,
                                 fill=color, width=max(1, 1.5 * scale),
                                 smooth=True)
                self._draw_node_thumbnail(ch, ch_x, ch_y, scale * 0.85,
                                          depth + 1, side)

    def create_rounded_rect(self, x1, y1, x2, y2, radius=5, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)


class NewMapDialog(tk.Toplevel):
    def __init__(self, master, callback):
        super().__init__(master)
        self.callback = callback
        self.title("新建思维导图")
        self.geometry("400x240")
        self.resizable(False, False)
        self.transient(master.winfo_toplevel())
        self.grab_set()

        self._create_widgets()

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.update_idletasks()
        x = master.winfo_toplevel().winfo_rootx() + 200
        y = master.winfo_toplevel().winfo_rooty() + 150
        self.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=25)
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame,
                                text="导图标题：",
                                font=("Microsoft YaHei", 11, "bold"))
        title_label.pack(anchor=tk.W, pady=(0, 5))

        self.title_var = tk.StringVar(value="我的思维导图")
        title_entry = ttk.Entry(main_frame,
                                textvariable=self.title_var,
                                font=("Microsoft YaHei", 11))
        title_entry.pack(fill=tk.X, pady=(0, 15))
        title_entry.select_range(0, tk.END)
        title_entry.focus_set()

        proj_label = ttk.Label(main_frame,
                               text="所属项目：",
                               font=("Microsoft YaHei", 11, "bold"))
        proj_label.pack(anchor=tk.W, pady=(0, 5))

        self.project_var = tk.StringVar(value="默认项目")
        project_combo = ttk.Combobox(main_frame,
                                     textvariable=self.project_var,
                                     values=[p for p in PRESET_PROJECTS if p != "全部"],
                                     font=("Microsoft YaHei", 11))
        project_combo.pack(fill=tk.X, pady=(0, 20))

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)

        cancel_btn = ttk.Button(btn_frame,
                                text="取消",
                                style="Action.TButton",
                                command=self._on_cancel)
        cancel_btn.pack(side=tk.RIGHT, padx=(8, 0))

        create_btn = ttk.Button(btn_frame,
                                text="创建",
                                style="Primary.TButton",
                                command=self._on_create)
        create_btn.pack(side=tk.RIGHT)

        self.bind("<Return>", lambda e: self._on_create())
        self.bind("<Escape>", lambda e: self._on_cancel())

    def _on_create(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("提示", "请输入导图标题")
            return
        project = self.project_var.get().strip() or "默认项目"
        self.callback(title, project)
        self.destroy()

    def _on_cancel(self):
        self.destroy()


class MindMapEditorView(ttk.Frame):
    NODE_PADDING_X = 18
    NODE_PADDING_Y = 10
    NODE_RADIUS = 10
    AUTO_SAVE_DELAY = 3000
    HORIZONTAL_GAP = 180
    VERTICAL_GAP = 55

    def __init__(self, master, parent_tool, map_data, is_new=False):
        super().__init__(master, style="Content.TFrame")
        self.parent = parent_tool
        self.storage = parent_tool.storage
        self.map_data = map_data
        self.is_new = is_new

        self.scale = map_data.get("scale", 1.0)
        self.offset_x = map_data.get("offset_x", 0)
        self.offset_y = map_data.get("offset_y", 0)

        self.selected_node_id = None
        self.editing_node_id = None
        self.dragging_node_id = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.node_start_x = 0
        self.node_start_y = 0
        self.is_panning = False
        self.pan_start_x = 0
        self.pan_start_y = 0
        self.auto_save_job = None
        self.history = []
        self.history_index = -1
        self.node_elements = {}
        self.line_elements = []

        self._create_widgets()
        self._bind_canvas_events()
        self._save_to_history()
        self._render_all()

        if self.is_new:
            self._select_node(self.map_data["root"]["id"])

    def _create_widgets(self):
        top_bar = ttk.Frame(self, style="Content.TFrame")
        top_bar.pack(fill=tk.X, pady=(0, 8))

        back_btn = ttk.Button(top_bar,
                              text="← 返回列表",
                              style="Action.TButton",
                              command=self._on_back)
        back_btn.pack(side=tk.LEFT)

        self.title_var = tk.StringVar(value=self.map_data.get("title", ""))
        self.title_var.trace_add("write", lambda *args: self._on_title_change())
        title_entry = ttk.Entry(top_bar,
                                textvariable=self.title_var,
                                font=("Microsoft YaHei", 14, "bold"),
                                width=30)
        title_entry.pack(side=tk.LEFT, padx=20)

        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(top_bar,
                                 textvariable=self.status_var,
                                 style="Status.TLabel")
        status_label.pack(side=tk.LEFT)

        toolbar = ttk.Frame(self, style="Content.TFrame")
        toolbar.pack(fill=tk.X, pady=(0, 5))

        zoom_out_btn = ttk.Button(toolbar,
                                  text="−",
                                  style="Toolbar.TButton",
                                  width=3,
                                  command=self._zoom_out)
        zoom_out_btn.pack(side=tk.LEFT)

        self.zoom_label = ttk.Label(toolbar,
                                    text=f"{int(self.scale * 100)}%",
                                    font=("Microsoft YaHei", 10, "bold"),
                                    width=6,
                                    anchor="center",
                                    background="#f5f6fa")
        self.zoom_label.pack(side=tk.LEFT, padx=2)

        zoom_in_btn = ttk.Button(toolbar,
                                 text="+",
                                 style="Toolbar.TButton",
                                 width=3,
                                 command=self._zoom_in)
        zoom_in_btn.pack(side=tk.LEFT)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=8, fill=tk.Y)

        fit_btn = ttk.Button(toolbar,
                             text="⛶ 适应画布",
                             style="Toolbar.TButton",
                             command=self._fit_to_screen)
        fit_btn.pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=8, fill=tk.Y)

        undo_btn = ttk.Button(toolbar,
                              text="↶ 撤销",
                              style="Toolbar.TButton",
                              command=self._undo)
        undo_btn.pack(side=tk.LEFT, padx=2)

        redo_btn = ttk.Button(toolbar,
                              text="↷ 重做",
                              style="Toolbar.TButton",
                              command=self._redo)
        redo_btn.pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=8, fill=tk.Y)

        export_btn = ttk.Button(toolbar,
                                text="📷 导出PNG",
                                style="Success.TButton",
                                command=self._export_png)
        export_btn.pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=8, fill=tk.Y)

        hint_label = ttk.Label(toolbar,
                               text="提示: Tab=子节点 | Enter=同级 | 双击=编辑 | 拖拽=移动 | 右键=菜单",
                               font=("Microsoft YaHei", 9),
                               background="#f5f6fa",
                               foreground="#7f8c8d")
        hint_label.pack(side=tk.LEFT, padx=5)

        canvas_container = ttk.Frame(self, style="Content.TFrame")
        canvas_container.pack(fill=tk.BOTH, expand=True)

        self.h_scroll = ttk.Scrollbar(canvas_container, orient=tk.HORIZONTAL)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        self.v_scroll = ttk.Scrollbar(canvas_container, orient=tk.VERTICAL)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas = tk.Canvas(canvas_container,
                                bg="#fafbfc",
                                highlightthickness=0,
                                xscrollcommand=self.h_scroll.set,
                                yscrollcommand=self.v_scroll.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.h_scroll.config(command=self.canvas.xview)
        self.v_scroll.config(command=self.canvas.yview)

    def _bind_canvas_events(self):
        self.canvas.bind("<ButtonPress-1>", self._on_canvas_press)
        self.canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_canvas_release)
        self.canvas.bind("<Double-Button-1>", self._on_canvas_double_click)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", lambda e: self._zoom_at(e.x, e.y, 1.1))
        self.canvas.bind("<Button-5>", lambda e: self._zoom_at(e.x, e.y, 0.9))
        self.canvas.bind("<Button-3>", self._on_canvas_right_click)
        self.canvas.bind("<Key>", self._on_key_press)
        self.canvas.focus_set()

    def _world_to_screen(self, wx, wy):
        return (wx * self.scale + self.offset_x,
                wy * self.scale + self.offset_y)

    def _screen_to_world(self, sx, sy):
        return ((sx - self.offset_x) / self.scale,
                (sy - self.offset_y) / self.scale)

    # ---------- 节点数据操作 ----------
    def _find_node(self, node_id, node=None, parent=None):
        if node is None:
            node = self.map_data["root"]
        if node["id"] == node_id:
            return node, parent
        for child in node.get("children", []):
            result = self._find_node(node_id, child, node)
            if result[0]:
                return result
        return None, None

    def _get_all_nodes_flat(self, node=None, depth=0, result=None):
        if result is None:
            result = []
        if node is None:
            node = self.map_data["root"]
        result.append((node, depth))
        for child in node.get("children", []):
            self._get_all_nodes_flat(child, depth + 1, result)
        return result

    def _calculate_auto_positions(self):
        root = self.map_data["root"]
        left_branch, right_branch = [], []
        children = root.get("children", [])
        for i, ch in enumerate(children):
            if i % 2 == 0:
                right_branch.append(ch)
            else:
                left_branch.append(ch)

        root_x = root.get("x", 0)
        root_y = root.get("y", 0)

        self._layout_branch(right_branch, root_x + self.HORIZONTAL_GAP * self.scale, root_y, 1)
        self._layout_branch(left_branch, root_x - self.HORIZONTAL_GAP * self.scale, root_y, -1)

    def _layout_branch(self, branch, start_x, center_y, direction):
        if not branch:
            return
        n = len(branch)
        total_h = (n - 1) * self.VERTICAL_GAP * self.scale
        start_y = center_y - total_h / 2
        for i, node in enumerate(branch):
            node["x"] = start_x
            node["y"] = start_y + i * self.VERTICAL_GAP * self.scale
            children = node.get("children", [])
            left_ch = children[:len(children) // 2]
            right_ch = children[len(children) // 2:]
            ch_dir = 1 if direction >= 0 else -1
            self._layout_branch(right_ch,
                                node["x"] + self.HORIZONTAL_GAP * 0.7 * self.scale * ch_dir,
                                node["y"], ch_dir)

    # ---------- 渲染 ----------
    def _render_all(self):
        self.canvas.delete("all")
        self.node_elements.clear()
        self.line_elements.clear()

        self._draw_grid()

        nodes_flat = self._get_all_nodes_flat()
        node_list = [n[0] for n in nodes_flat]

        if self.selected_node_id is None and node_list:
            self._calculate_auto_positions()

        self._render_connections(self.map_data["root"], None)
        self._render_node(self.map_data["root"])

    def _draw_grid(self):
        try:
            cw = self.canvas.winfo_width()
            ch = self.canvas.winfo_height()
            if cw < 2:
                return
        except:
            return

        grid_size = 50 * self.scale
        ox = self.offset_x % grid_size
        oy = self.offset_y % grid_size

        for x in self._frange(ox, cw, grid_size):
            self.canvas.create_line(x, 0, x, ch, fill="#eef1f5", width=1)
        for y in self._frange(oy, ch, grid_size):
            self.canvas.create_line(0, y, cw, y, fill="#eef1f5", width=1)

    def _frange(self, start, stop, step):
        while start < stop:
            yield start
            start += step

    def _render_connections(self, node, parent):
        if parent is not None:
            self._draw_bezier_connection(parent, node)
        for child in node.get("children", []):
            self._render_connections(child, node)

    def _draw_bezier_connection(self, parent, child):
        px, py = self._world_to_screen(parent["x"], parent["y"])
        cx, cy = self._world_to_screen(child["x"], child["y"])

        dx = abs(cx - px) * 0.5
        cp1x = px + dx if cx > px else px - dx
        cp1y = py
        cp2x = cx - dx if cx > px else cx + dx
        cp2y = cy

        color = parent.get("color", "#3498db")
        line_id = self.canvas.create_line(px, py, cp1x, cp1y, cp2x, cp2y, cx, cy,
                                          fill=color,
                                          width=max(1, int(2 * self.scale)),
                                          smooth=True,
                                          splinesteps=24)
        self.line_elements.append(line_id)

    def _render_node(self, node):
        x, y = self._world_to_screen(node["x"], node["y"])
        color = node.get("color", "#3498db")
        text = node.get("text", "")
        icon = node.get("icon")
        link = node.get("link")

        font_size = max(10, int(12 * self.scale))
        is_root = node is self.map_data["root"]
        if is_root:
            font_size = max(12, int(14 * self.scale))

        font = ("Microsoft YaHei", font_size, "bold" if is_root else "normal")

        display_text = text
        if icon:
            display_text = f"{icon} {text}"

        pad_x = self.NODE_PADDING_X * self.scale
        pad_y = self.NODE_PADDING_Y * self.scale

        text_item = self.canvas.create_text(x, y, text=display_text,
                                            font=font, fill="white")
        bbox = self.canvas.bbox(text_item)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]

        w = tw + 2 * pad_x
        h = th + 2 * pad_y
        radius = self.NODE_RADIUS * self.scale

        rect_id = self._create_rounded_rect(x - w / 2, y - h / 2,
                                            x + w / 2, y + h / 2,
                                            radius=radius,
                                            fill=color, outline="")

        self.canvas.tag_raise(text_item)

        is_selected = self.selected_node_id == node["id"]
        if is_selected:
            sel_w = w + 8 * self.scale
            sel_h = h + 8 * self.scale
            sel_r = radius + 4
            self._create_rounded_rect(x - sel_w / 2, y - sel_h / 2,
                                      x + sel_w / 2, y + sel_h / 2,
                                      radius=sel_r,
                                      outline="#e74c3c",
                                      width=max(2, int(3 * self.scale)))
            self.canvas.tag_raise(text_item)

        if link:
            lx = x + w / 2 + 2
            ly = y - h / 2 - 2
            self.canvas.create_text(lx, ly, text="🔗",
                                    font=("Microsoft YaHei", max(8, int(10 * self.scale))),
                                    anchor="se")

        self.node_elements[node["id"]] = {
            "rect": rect_id,
            "text": text_item,
            "cx": x, "cy": y,
            "half_w": w / 2, "half_h": h / 2
        }

        for child in node.get("children", []):
            self._render_node(child)

        elem = self.node_elements[node["id"]]
        for tag in [elem["rect"], elem["text"]]:
            self.canvas.tag_bind(tag, "<ButtonPress-1>",
                                 lambda e, nid=node["id"]: self._on_node_press(e, nid))
            self.canvas.tag_bind(tag, "<Double-Button-1>",
                                 lambda e, nid=node["id"]: self._on_node_double_click(e, nid))
            self.canvas.tag_bind(tag, "<Button-3>",
                                 lambda e, nid=node["id"]: self._on_node_right_click(e, nid))

    def _create_rounded_rect(self, x1, y1, x2, y2, radius=8, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

    # ---------- 交互事件 ----------
    def _on_canvas_press(self, event):
        clicked_node = self._hit_test_node(event.x, event.y)
        if clicked_node:
            self._on_node_press(event, clicked_node)
            return

        self.is_panning = True
        self.pan_start_x = event.x - self.offset_x
        self.pan_start_y = event.y - self.offset_y
        self._select_node(None)
        self.canvas.focus_set()

    def _on_canvas_drag(self, event):
        if self.dragging_node_id:
            dx = (event.x - self.drag_start_x) / self.scale
            dy = (event.y - self.drag_start_y) / self.scale
            node, _ = self._find_node(self.dragging_node_id)
            if node:
                node["x"] = self.node_start_x + dx
                node["y"] = self.node_start_y + dy
                self._render_all()
            return

        if self.is_panning:
            self.offset_x = event.x - self.pan_start_x
            self.offset_y = event.y - self.pan_start_y
            self._render_all()

    def _on_canvas_release(self, event):
        if self.dragging_node_id:
            self.dragging_node_id = None
            self._mark_changed()
            return
        self.is_panning = False

    def _on_canvas_double_click(self, event):
        pass

    def _on_canvas_right_click(self, event):
        self._select_node(None)
        self.canvas.focus_set()

    def _hit_test_node(self, sx, sy):
        best_id = None
        best_z = -1
        for nid, elem in self.node_elements.items():
            dx = abs(sx - elem["cx"])
            dy = abs(sy - elem["cy"])
            if dx <= elem["half_w"] and dy <= elem["half_h"]:
                node, _ = self._find_node(nid)
                depth = self._get_node_depth(nid)
                if depth > best_z:
                    best_z = depth
                    best_id = nid
        return best_id

    def _get_node_depth(self, node_id):
        flat = self._get_all_nodes_flat()
        for n, d in flat:
            if n["id"] == node_id:
                return d
        return 0

    def _on_node_press(self, event, node_id):
        self._select_node(node_id)
        self.dragging_node_id = node_id
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        node, _ = self._find_node(node_id)
        if node:
            self.node_start_x = node["x"]
            self.node_start_y = node["y"]
        self.canvas.focus_set()

    def _on_node_double_click(self, event, node_id):
        self._start_edit_node(node_id)

    def _on_node_right_click(self, event, node_id):
        self._select_node(node_id)
        self._show_context_menu(event.x_root, event.y_root, node_id)

    def _select_node(self, node_id):
        self.selected_node_id = node_id
        self._render_all()

    def _on_key_press(self, event):
        if self.editing_node_id:
            return

        if event.keysym == "Tab":
            if self.selected_node_id:
                self._add_child_node(self.selected_node_id)
            return "break"
        elif event.keysym == "Return" and not event.state & 0x0001:
            if self.selected_node_id and self.selected_node_id != self.map_data["root"]["id"]:
                self._add_sibling_node(self.selected_node_id)
            return "break"
        elif event.keysym in ("Delete", "BackSpace"):
            if self.selected_node_id and self.selected_node_id != self.map_data["root"]["id"]:
                self._delete_node(self.selected_node_id)
            return "break"
        elif event.keysym == "F2":
            if self.selected_node_id:
                self._start_edit_node(self.selected_node_id)
            return "break"
        elif event.state & 0x0004:
            if event.keysym == "z":
                self._undo()
                return "break"
            elif event.keysym == "y":
                self._redo()
                return "break"

    # ---------- 节点操作 ----------
    def _start_edit_node(self, node_id):
        node, _ = self._find_node(node_id)
        if not node:
            return

        self.editing_node_id = node_id
        x, y = self._world_to_screen(node["x"], node["y"])
        elem = self.node_elements.get(node_id)
        if not elem:
            return

        self.edit_var = tk.StringVar(value=node.get("text", ""))
        self.edit_entry = ttk.Entry(self.canvas,
                                    textvariable=self.edit_var,
                                    font=("Microsoft YaHei", max(11, int(12 * self.scale))),
                                    justify="center")
        w = int(elem["half_w"] * 2 * 0.9)
        self.edit_entry.configure(width=max(5, w // 10))

        entry_win = self.canvas.create_window(x, y, window=self.edit_entry)
        self.edit_entry.focus_set()
        self.edit_entry.select_range(0, tk.END)

        def _commit(event=None):
            new_text = self.edit_var.get().strip()
            if new_text:
                node["text"] = new_text
                if node is self.map_data["root"]:
                    self.map_data["title"] = new_text
                    self.title_var.set(new_text)
            self.edit_entry.destroy()
            self.canvas.delete(entry_win)
            self.editing_node_id = None
            self._render_all()
            self._mark_changed()

        def _cancel(event=None):
            self.edit_entry.destroy()
            self.canvas.delete(entry_win)
            self.editing_node_id = None
            self._render_all()

        self.edit_entry.bind("<Return>", _commit)
        self.edit_entry.bind("<Escape>", _cancel)
        self.edit_entry.bind("<FocusOut>", _commit)

    def _add_child_node(self, parent_id):
        parent, _ = self._find_node(parent_id)
        if not parent:
            return

        new_node = {
            "id": str(uuid.uuid4()),
            "text": "新节点",
            "x": parent["x"] + self.HORIZONTAL_GAP * self.scale * (1 if len(parent.get("children", [])) % 2 == 0 else -1),
            "y": parent["y"] + (len(parent.get("children", [])) - 1) * self.VERTICAL_GAP * self.scale * 0.5,
            "color": NODE_COLORS[len(parent.get("children", [])) % len(NODE_COLORS)],
            "icon": None,
            "link": None,
            "children": []
        }

        if "children" not in parent:
            parent["children"] = []
        parent["children"].append(new_node)

        self._calculate_auto_positions()
        self._render_all()
        self._select_node(new_node["id"])
        self._mark_changed()
        self.after(200, lambda: self._start_edit_node(new_node["id"]))

    def _add_sibling_node(self, node_id):
        node, parent = self._find_node(node_id)
        if not node or not parent:
            return

        idx = parent["children"].index(node)
        new_node = {
            "id": str(uuid.uuid4()),
            "text": "新节点",
            "x": node["x"],
            "y": node["y"] + self.VERTICAL_GAP * self.scale,
            "color": node.get("color", "#3498db"),
            "icon": None,
            "link": None,
            "children": []
        }
        parent["children"].insert(idx + 1, new_node)

        self._calculate_auto_positions()
        self._render_all()
        self._select_node(new_node["id"])
        self._mark_changed()
        self.after(200, lambda: self._start_edit_node(new_node["id"]))

    def _delete_node(self, node_id):
        if node_id == self.map_data["root"]["id"]:
            return
        if not messagebox.askyesno("删除节点", "确定删除该节点及其所有子节点吗？"):
            return
        node, parent = self._find_node(node_id)
        if parent and node:
            parent["children"].remove(node)
            self._calculate_auto_positions()
            self._render_all()
            self._select_node(parent["id"])
            self._mark_changed()

    # ---------- 右键菜单 ----------
    def _show_context_menu(self, x, y, node_id):
        node, _ = self._find_node(node_id)
        if not node:
            return

        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="✏️ 编辑文字", command=lambda: self._start_edit_node(node_id))
        menu.add_separator()

        color_menu = tk.Menu(menu, tearoff=0)
        for c in NODE_COLORS:
            color_menu.add_command(label="      ",
                                   background=c,
                                   command=lambda col=c: self._set_node_color(node_id, col))
        menu.add_cascade(label="🎨 更改颜色", menu=color_menu)

        icon_menu = tk.Menu(menu, tearoff=0)
        for ic in NODE_ICONS:
            icon_menu.add_command(label=ic,
                                  command=lambda i=ic: self._set_node_icon(node_id, i))
        icon_menu.add_command(label="清除图标",
                              command=lambda: self._set_node_icon(node_id, None))
        menu.add_cascade(label="🏷 添加图标", menu=icon_menu)

        menu.add_command(label="🔗 插入链接", command=lambda: self._set_node_link(node_id))
        if node.get("link"):
            menu.add_command(label="🌐 打开链接", command=lambda: self._open_node_link(node_id))
        menu.add_separator()
        if node_id != self.map_data["root"]["id"]:
            menu.add_command(label="🗑 删除节点", command=lambda: self._delete_node(node_id))

        try:
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

    def _set_node_color(self, node_id, color):
        node, _ = self._find_node(node_id)
        if node:
            node["color"] = color
            self._render_all()
            self._mark_changed()

    def _set_node_icon(self, node_id, icon):
        node, _ = self._find_node(node_id)
        if node:
            node["icon"] = icon
            self._render_all()
            self._mark_changed()

    def _set_node_link(self, node_id):
        node, _ = self._find_node(node_id)
        if not node:
            return
        current = node.get("link", "")
        link = simpledialog.askstring("插入链接", "请输入链接地址：",
                                      initialvalue=current,
                                      parent=self.winfo_toplevel())
        if link is not None:
            node["link"] = link.strip() or None
            self._render_all()
            self._mark_changed()

    def _open_node_link(self, node_id):
        node, _ = self._find_node(node_id)
        if node and node.get("link"):
            import webbrowser
            link = node["link"]
            if not link.startswith(("http://", "https://")):
                link = "https://" + link
            webbrowser.open(link)

    # ---------- 工具栏 ----------
    def _zoom_in(self):
        cx = self.canvas.winfo_width() / 2
        cy = self.canvas.winfo_height() / 2
        self._zoom_at(cx, cy, 1.2)

    def _zoom_out(self):
        cx = self.canvas.winfo_width() / 2
        cy = self.canvas.winfo_height() / 2
        self._zoom_at(cx, cy, 0.8)

    def _zoom_at(self, sx, sy, factor):
        new_scale = self.scale * factor
        new_scale = max(0.3, min(3.0, new_scale))
        actual_factor = new_scale / self.scale

        wx, wy = self._screen_to_world(sx, sy)
        self.scale = new_scale
        new_sx, new_sy = self._world_to_screen(wx, wy)
        self.offset_x += (sx - new_sx)
        self.offset_y += (sy - new_sy)

        self.zoom_label.configure(text=f"{int(self.scale * 100)}%")
        self._render_all()

    def _on_mousewheel(self, event):
        if event.state & 0x0004:
            factor = 1.1 if event.delta > 0 else 0.9
            self._zoom_at(event.x, event.y, factor)
        else:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _fit_to_screen(self):
        nodes = self._get_all_nodes_flat()
        if not nodes:
            return

        xs = [n[0]["x"] for n in nodes]
        ys = [n[0]["y"] for n in nodes]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        padding = 150
        cw = self.canvas.winfo_width() - 40
        ch = self.canvas.winfo_height() - 40

        world_w = (max_x - min_x) + 200
        world_h = (max_y - min_y) + 200

        if world_w <= 0 or world_h <= 0 or cw <= 0 or ch <= 0:
            return

        scale = min(cw / world_w, ch / world_h)
        scale = max(0.3, min(2.0, scale))
        self.scale = scale

        center_wx = (min_x + max_x) / 2
        center_wy = (min_y + max_y) / 2
        self.offset_x = cw / 2 + 20 - center_wx * self.scale
        self.offset_y = ch / 2 + 20 - center_wy * self.scale

        self.zoom_label.configure(text=f"{int(self.scale * 100)}%")
        self._render_all()

    # ---------- 撤销重做 ----------
    def _save_to_history(self):
        state = copy.deepcopy({
            "root": self.map_data["root"],
            "title": self.map_data["title"],
            "scale": self.scale,
            "offset_x": self.offset_x,
            "offset_y": self.offset_y
        })
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        self.history.append(state)
        self.history_index = len(self.history) - 1
        if len(self.history) > 100:
            self.history.pop(0)
            self.history_index -= 1

    def _undo(self):
        if self.history_index <= 0:
            self._set_status("已无历史记录")
            return
        self.history_index -= 1
        self._restore_from_history()

    def _redo(self):
        if self.history_index >= len(self.history) - 1:
            self._set_status("已无重做记录")
            return
        self.history_index += 1
        self._restore_from_history()

    def _restore_from_history(self):
        state = self.history[self.history_index]
        self.map_data["root"] = copy.deepcopy(state["root"])
        self.map_data["title"] = state["title"]
        self.title_var.set(state["title"])
        self.scale = state["scale"]
        self.offset_x = state["offset_x"]
        self.offset_y = state["offset_y"]
        self.zoom_label.configure(text=f"{int(self.scale * 100)}%")
        self._render_all()
        self._set_status("已恢复")

    # ---------- 自动保存 ----------
    def _on_title_change(self):
        new_title = self.title_var.get()
        self.map_data["title"] = new_title
        self.map_data["root"]["text"] = new_title
        self._mark_changed(render=False)

    def _mark_changed(self, render=True):
        self._save_to_history()
        if render:
            pass
        self._set_status("修改中...")
        self._schedule_auto_save()

    def _schedule_auto_save(self):
        if self.auto_save_job:
            self.after_cancel(self.auto_save_job)
        self.auto_save_job = self.after(self.AUTO_SAVE_DELAY, self._do_auto_save)

    def _do_auto_save(self):
        self.map_data["scale"] = self.scale
        self.map_data["offset_x"] = self.offset_x
        self.map_data["offset_y"] = self.offset_y
        try:
            self.storage.save_map(self.map_data)
            self._set_status(f"✓ 已自动保存  {MindMapStorage.format_timestamp(time.time())}")
        except Exception as e:
            self._set_status(f"保存失败: {e}")
        self.auto_save_job = None

    def _set_status(self, msg):
        self.status_var.set(msg)
        self.after(3000, lambda: self.status_var.set("") if self.status_var.get() == msg else None)

    # ---------- 导出PNG ----------
    def _export_png(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG 图片", "*.png")],
            initialfile=f"{self.map_data.get('title', 'mindmap')}.png",
            title="导出思维导图为PNG"
        )
        if not file_path:
            return

        try:
            self._render_to_png(file_path)
            messagebox.showinfo("导出成功", f"思维导图已保存到:\n{file_path}")
        except Exception as e:
            messagebox.showerror("导出失败", f"导出过程中出错：\n{e}")

    def _render_to_png(self, file_path):
        nodes = self._get_all_nodes_flat()
        if not nodes:
            return

        padding = 100
        node_size_est = 120

        xs = [n[0]["x"] for n in nodes]
        ys = [n[0]["y"] for n in nodes]
        min_x, max_x = min(xs) - node_size_est, max(xs) + node_size_est
        min_y, max_y = min(ys) - node_size_est, max(ys) + node_size_est

        img_w = int(max_x - min_x + 2 * padding)
        img_h = int(max_y - min_y + 2 * padding)
        img_w = max(800, img_w)
        img_h = max(600, img_h)

        render_scale = 2
        img = Image.new("RGBA", (img_w * render_scale, img_h * render_scale), (250, 251, 252, 255))
        draw = ImageDraw.Draw(img)

        def tx(x):
            return int((x - min_x + padding) * render_scale)

        def ty(y):
            return int((y - min_y + padding) * render_scale)

        grid_step = 50 * render_scale
        for gx in range(0, img_w * render_scale, grid_step):
            draw.line([(gx, 0), (gx, img_h * render_scale)], fill=(238, 241, 245, 255), width=1)
        for gy in range(0, img_h * render_scale, grid_step):
            draw.line([(0, gy), (img_w * render_scale, gy)], fill=(238, 241, 245, 255), width=1)

        def _draw_connections(node, parent_node):
            if parent_node:
                px, py = tx(parent_node["x"]), ty(parent_node["y"])
                cx, cy = tx(node["x"]), ty(node["y"])
                color_hex = parent_node.get("color", "#3498db")
                color_rgb = self._hex_to_rgb(color_hex)
                mid_x = (px + cx) // 2
                draw.line([(px, py), (mid_x, py), (mid_x, cy), (cx, cy)],
                          fill=color_rgb, width=3 * render_scale // 2)
            for ch in node.get("children", []):
                _draw_connections(ch, node)

        _draw_connections(self.map_data["root"], None)

        def _draw_nodes(node):
            cx, cy = tx(node["x"]), ty(node["y"])
            color_hex = node.get("color", "#3498db")
            color_rgb = self._hex_to_rgb(color_hex)
            text = node.get("text", "")
            icon = node.get("icon")
            if icon:
                text = f"{icon} {text}"

            is_root = node is self.map_data["root"]
            font_size = (18 if is_root else 14) * render_scale
            try:
                font = ImageFont.truetype("msyh.ttc", font_size)
            except:
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()

            try:
                bbox = draw.textbbox((0, 0), text, font=font)
                tw = bbox[2] - bbox[0]
                th = bbox[3] - bbox[1]
            except:
                tw = len(text) * font_size * 0.6
                th = font_size * 1.2

            pad_x = 24 * render_scale
            pad_y = 16 * render_scale
            w = tw + 2 * pad_x
            h = th + 2 * pad_y
            r = 12 * render_scale

            self._draw_rounded_rect_pil(draw,
                                        cx - w // 2, cy - h // 2,
                                        cx + w // 2, cy + h // 2,
                                        r, color_rgb)

            text_color = (255, 255, 255, 255)
            draw.text((cx - tw // 2, cy - th // 2), text, fill=text_color, font=font)

            for ch in node.get("children", []):
                _draw_nodes(ch)

        _draw_nodes(self.map_data["root"])

        img = img.resize((img_w, img_h), Image.LANCZOS)
        img.save(file_path, "PNG")

    def _draw_rounded_rect_pil(self, draw, x1, y1, x2, y2, r, fill):
        draw.rounded_rectangle([x1, y1, x2, y2], radius=r, fill=fill)

    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4)) + (255,)

    # ---------- 返回 ----------
    def _on_back(self):
        if self.auto_save_job:
            self.after_cancel(self.auto_save_job)
            self._do_auto_save()
        self.parent.back_to_list()
