import tkinter as tk
from tkinter import ttk
from app.tools.json_tool import JsonTool
from app.tools.timestamp_tool import TimestampTool


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("开发者工具箱")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)

        self.tools = {
            "JSON 格式化校验": JsonTool,
            "时间戳转换": TimestampTool,
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

    def _create_layout(self):
        self.paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        self._create_content_area()
        self._create_sidebar()

        self.paned_window.add(self.sidebar_frame, weight=1)
        self.paned_window.add(self.content_frame, weight=4)

    def _create_sidebar(self):
        self.sidebar_frame = ttk.Frame(self.paned_window, style="Sidebar.TFrame", width=200)
        self.sidebar_frame.pack_propagate(False)

        title_label = ttk.Label(self.sidebar_frame,
                                text="工具箱",
                                style="SidebarTitle.TLabel",
                                padding=(20, 20, 20, 10))
        title_label.pack(anchor=tk.W)

        separator = tk.Frame(self.sidebar_frame, bg="#3d566e", height=1)
        separator.pack(fill=tk.X, padx=15)

        list_label = ttk.Label(self.sidebar_frame,
                               text="可用工具",
                               style="Sidebar.TLabel",
                               padding=(20, 15, 20, 5))
        list_label.pack(anchor=tk.W)

        self.tool_listbox = tk.Listbox(self.sidebar_frame,
                                       bg="#34495e",
                                       fg="#ecf0f1",
                                       selectbackground="#3498db",
                                       selectforeground="#ffffff",
                                       font=("Microsoft YaHei", 11),
                                       borderwidth=0,
                                       highlightthickness=0,
                                       activestyle="none",
                                       cursor="hand2")
        self.tool_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        for tool_name in self.tools.keys():
            self.tool_listbox.insert(tk.END, f"  {tool_name}")

        self.tool_listbox.bind("<<ListboxSelect>>", self._on_tool_select)
        self.tool_listbox.selection_set(0)
        self.tool_listbox.event_generate("<<ListboxSelect>>")

    def _create_content_area(self):
        self.content_frame = ttk.Frame(self.paned_window, style="Content.TFrame")
        self.tool_container = ttk.Frame(self.content_frame, style="Content.TFrame")
        self.tool_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _on_tool_select(self, event):
        selection = self.tool_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        tool_name = list(self.tools.keys())[index]
        self._load_tool(tool_name)

    def _load_tool(self, tool_name):
        for widget in self.tool_container.winfo_children():
            widget.destroy()

        tool_class = self.tools[tool_name]
        self.current_tool = tool_class(self.tool_container)
        self.current_tool.pack(fill=tk.BOTH, expand=True)
