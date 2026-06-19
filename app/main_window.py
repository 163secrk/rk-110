import tkinter as tk
from tkinter import ttk
from app.tools.json_tool import JsonTool
from app.tools.timestamp_tool import TimestampTool
from app.tools.base64_url_tool import Base64UrlTool
from app.tools.regex_tool import RegexTool
from app.tools.qrcode_tool import QRCodeTool
from app.tools.hash_tool import HashTool
from app.tools.mindmap_tool import MindMapTool
from app.tools.text_diff_tool import TextDiffTool
from app.tools.color_converter_tool import ColorConverterTool


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("开发者工具箱")
        self.root.geometry("1200x800")
        self.root.minsize(900, 650)

        self.tool_categories = {
            "开发工具": {
                "JSON 格式化校验": JsonTool,
                "时间戳转换": TimestampTool,
                "Base64 / URL 编解码": Base64UrlTool,
                "正则测试": RegexTool,
                "哈希计算": HashTool,
                "二维码生成": QRCodeTool,
                "文本比对": TextDiffTool,
                "颜色转换": ColorConverterTool,
            },
            "文档协作": {
                "思维导图": MindMapTool,
            }
        }

        self.current_tool = None
        self._setup_styles()
        self._create_layout()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Sidebar.TFrame", background="#2c3e50")
        style.configure("Sidebar.TLabel",
                        background="#2c3e50",
                        foreground="#ecf0f1",
                        font=("Microsoft YaHei", 10, "bold"))
        style.configure("SidebarTitle.TLabel",
                        background="#2c3e50",
                        foreground="#ecf0f1",
                        font=("Microsoft YaHei", 14, "bold"))
        style.configure("Content.TFrame", background="#f5f6fa")

        style.configure("Sidebar.Treeview",
                        background="#2c3e50",
                        foreground="#ecf0f1",
                        fieldbackground="#2c3e50",
                        borderwidth=0,
                        font=("Microsoft YaHei", 11),
                        rowheight=32)
        style.configure("Sidebar.Treeview.Heading",
                        background="#2c3e50",
                        foreground="#ecf0f1",
                        relief=tk.FLAT,
                        font=("Microsoft YaHei", 10, "bold"))
        style.map("Sidebar.Treeview",
                  background=[("selected", "#3498db")],
                  foreground=[("selected", "#ffffff")])

    def _create_layout(self):
        self.paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        self._create_content_area()
        self._create_sidebar()

        self.paned_window.add(self.sidebar_frame, weight=1)
        self.paned_window.add(self.content_frame, weight=5)

    def _create_sidebar(self):
        self.sidebar_frame = ttk.Frame(self.paned_window, style="Sidebar.TFrame", width=240)
        self.sidebar_frame.pack_propagate(False)

        title_label = ttk.Label(self.sidebar_frame,
                                text="工具箱",
                                style="SidebarTitle.TLabel",
                                padding=(20, 20, 20, 10))
        title_label.pack(anchor=tk.W)

        separator = tk.Frame(self.sidebar_frame, bg="#3d566e", height=1)
        separator.pack(fill=tk.X, padx=15)

        list_label = ttk.Label(self.sidebar_frame,
                               text="功能导航",
                               style="Sidebar.TLabel",
                               padding=(20, 15, 20, 5))
        list_label.pack(anchor=tk.W)

        self.tool_tree = ttk.Treeview(self.sidebar_frame,
                                      style="Sidebar.Treeview",
                                      show="tree",
                                      selectmode="browse")
        self.tool_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.tool_mapping = {}
        for category, tools in self.tool_categories.items():
            cat_id = self.tool_tree.insert("", tk.END, text=f"  {category}", open=True)
            for tool_name, tool_class in tools.items():
                tool_id = self.tool_tree.insert(cat_id, tk.END, text=f"    {tool_name}")
                self.tool_mapping[tool_id] = tool_name

        self.tool_tree.bind("<<TreeviewSelect>>", self._on_tool_select)

        first_child = self.tool_tree.get_children()[0]
        first_tool = self.tool_tree.get_children(first_child)[0]
        self.tool_tree.selection_set(first_tool)
        self.tool_tree.event_generate("<<TreeviewSelect>>")

    def _create_content_area(self):
        self.content_frame = ttk.Frame(self.paned_window, style="Content.TFrame")

        self.content_scroll = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL)
        self.content_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.content_inner = ttk.Frame(self.content_frame, style="Content.TFrame")
        self.content_inner.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tool_container = ttk.Frame(self.content_inner, style="Content.TFrame")
        self.tool_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _on_tool_select(self, event):
        selection = self.tool_tree.selection()
        if not selection:
            return

        item_id = selection[0]
        if item_id not in self.tool_mapping:
            return

        tool_name = self.tool_mapping[item_id]
        self._load_tool(tool_name)

    def _load_tool(self, tool_name):
        for widget in self.tool_container.winfo_children():
            widget.destroy()

        for category, tools in self.tool_categories.items():
            if tool_name in tools:
                tool_class = tools[tool_name]
                self.current_tool = tool_class(self.tool_container)
                self.current_tool.pack(fill=tk.BOTH, expand=True)
                break
