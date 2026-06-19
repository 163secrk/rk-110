import tkinter as tk
from tkinter import ttk, scrolledtext
import re
import html


class MarkdownPreviewTool(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, style="Content.TFrame")
        self._setup_styles()
        self._create_widgets()
        self._setup_preview_tags()
        self._bind_events()
        self._refresh_preview()

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

    def _create_widgets(self):
        title_label = ttk.Label(self,
                                text="Markdown预览",
                                style="ToolTitle.TLabel")
        title_label.pack(anchor=tk.W, pady=(0, 15))

        main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)

        self._create_editor_area(main_paned)
        self._create_preview_area(main_paned)

    def _create_editor_area(self, parent):
        editor_frame = ttk.Frame(parent, style="Content.TFrame")

        editor_label = ttk.Label(editor_frame,
                                 text="Markdown 原文：",
                                 style="Section.TLabel")
        editor_label.pack(anchor=tk.W, pady=(0, 5))

        text_container = ttk.Frame(editor_frame)
        text_container.pack(fill=tk.BOTH, expand=True)

        self.editor_text = scrolledtext.ScrolledText(
            text_container,
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
            highlightcolor="#3498db"
        )
        self.editor_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sample_md = """# Markdown 预览示例

## 二级标题
### 三级标题

这是一段普通文本，支持 **加粗**、*斜体*、***加粗斜体***。

## 列表示例

无序列表：
- 项目一
- 项目二
  - 嵌套项目
- 项目三

有序列表：
1. 第一步
2. 第二步
3. 第三步

## 链接与图片

这是一个 [链接示例](https://example.com)。

图片示例：
![示例图片](https://picsum.photos/200/100)

## 代码块

行内代码：`print("Hello World")`

代码块：
```python
def hello():
    print("Hello, Markdown!")
    return True
```

## 引用

> 这是一段引用文字。
> 可以有多行。
>
>> 嵌套引用也是支持的。

## 表格

| 姓名 | 年龄 | 城市 |
|------|------|------|
| 张三 | 25   | 北京 |
| 李四 | 30   | 上海 |
| 王五 | 28   | 广州 |
"""
        self.editor_text.insert(tk.END, sample_md)

        parent.add(editor_frame, weight=1)

    def _create_preview_area(self, parent):
        preview_frame = ttk.Frame(parent, style="Content.TFrame")

        preview_label = ttk.Label(preview_frame,
                                  text="HTML 预览：",
                                  style="Section.TLabel")
        preview_label.pack(anchor=tk.W, pady=(0, 5))

        text_container = ttk.Frame(preview_frame)
        text_container.pack(fill=tk.BOTH, expand=True)

        self.preview_text = scrolledtext.ScrolledText(
            text_container,
            font=("Microsoft YaHei", 11),
            bg="white",
            fg="#2c3e50",
            wrap=tk.WORD,
            padx=15,
            pady=15,
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground="#bdc3c7",
            highlightcolor="#3498db",
            state=tk.DISABLED
        )
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        parent.add(preview_frame, weight=1)

    def _setup_preview_tags(self):
        pt = self.preview_text
        pt.tag_configure("h1", font=("Microsoft YaHei", 24, "bold"), spacing3=15, foreground="#2c3e50")
        pt.tag_configure("h2", font=("Microsoft YaHei", 20, "bold"), spacing1=15, spacing3=10, foreground="#2c3e50")
        pt.tag_configure("h3", font=("Microsoft YaHei", 17, "bold"), spacing1=12, spacing3=8, foreground="#34495e")
        pt.tag_configure("h4", font=("Microsoft YaHei", 14, "bold"), spacing1=10, spacing3=6, foreground="#34495e")
        pt.tag_configure("h5", font=("Microsoft YaHei", 12, "bold"), spacing1=8, spacing3=5, foreground="#34495e")
        pt.tag_configure("h6", font=("Microsoft YaHei", 11, "bold"), spacing1=6, spacing3=4, foreground="#7f8c8d")

        pt.tag_configure("bold", font=("Microsoft YaHei", 11, "bold"))
        pt.tag_configure("italic", font=("Microsoft YaHei", 11, "italic"))
        pt.tag_configure("bold_italic", font=("Microsoft YaHei", 11, "bold", "italic"))

        pt.tag_configure("code", font=("Consolas", 10), background="#f4f4f4", foreground="#e74c3c")
        pt.tag_configure("codeblock", font=("Consolas", 10), background="#f8f9fa", foreground="#2c3e50",
                         lmargin1=20, lmargin2=20)
        pt.tag_configure("codeblock_bg", background="#f8f9fa")

        pt.tag_configure("quote", font=("Microsoft YaHei", 11), foreground="#7f8c8d",
                         lmargin1=20, lmargin2=20, borderwidth=1)
        pt.tag_configure("quote_bar", background="#bdc3c7")

        pt.tag_configure("link", foreground="#3498db", underline=True)

        pt.tag_configure("ul_bullet", foreground="#3498db", font=("Microsoft YaHei", 11, "bold"))
        pt.tag_configure("ol_num", foreground="#e67e22", font=("Microsoft YaHei", 11, "bold"))

        pt.tag_configure("table_cell", font=("Microsoft YaHei", 10))
        pt.tag_configure("table_header", font=("Microsoft YaHei", 10, "bold"), background="#ecf0f1")
        pt.tag_configure("table_sep", background="#bdc3c7")

        pt.tag_configure("hr", background="#bdc3c7")

        pt.tag_configure("para", spacing3=8)

    def _bind_events(self):
        self.editor_text.bind("<KeyRelease>", self._on_text_changed)
        self.editor_text.bind("<<Modified>>", self._on_text_changed)

    def _on_text_changed(self, event=None):
        self._refresh_preview()
        if event and event.type == "38":
            self.editor_text.edit_modified(False)

    def _refresh_preview(self):
        md_text = self.editor_text.get("1.0", tk.END)
        self.preview_text.configure(state=tk.NORMAL)
        self.preview_text.delete("1.0", tk.END)
        self._render_markdown(md_text)
        self.preview_text.configure(state=tk.DISABLED)

    def _render_markdown(self, text):
        lines = text.split("\n")
        i = 0
        in_code_block = False
        code_block_lines = []
        code_lang = ""

        while i < len(lines):
            line = lines[i]

            if line.strip().startswith("```"):
                if not in_code_block:
                    in_code_block = True
                    code_lang = line.strip()[3:].strip()
                    code_block_lines = []
                else:
                    self._render_code_block("\n".join(code_block_lines), code_lang)
                    in_code_block = False
                    code_block_lines = []
                    code_lang = ""
                i += 1
                continue

            if in_code_block:
                code_block_lines.append(line)
                i += 1
                continue

            if re.match(r"^#{1,6}\s+", line):
                self._render_heading(line)
                i += 1
                continue

            if re.match(r"^\s*[-*_]{3,}\s*$", line):
                self._render_hr()
                i += 1
                continue

            if re.match(r"^\s*>\s?", line):
                quote_lines = []
                while i < len(lines) and re.match(r"^\s*>\s?", lines[i]):
                    quote_lines.append(re.sub(r"^\s*>\s?", "", lines[i]))
                    i += 1
                self._render_quote("\n".join(quote_lines))
                continue

            if re.match(r"^\s*[-*+]\s+", line):
                ul_items = []
                while i < len(lines) and re.match(r"^\s*[-*+]\s+", lines[i]):
                    item_text = re.sub(r"^\s*[-*+]\s+", "", lines[i])
                    indent = len(lines[i]) - len(lines[i].lstrip())
                    ul_items.append((indent, item_text))
                    i += 1
                self._render_unordered_list(ul_items)
                continue

            if re.match(r"^\s*\d+\.\s+", line):
                ol_items = []
                while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                    item_text = re.sub(r"^\s*\d+\.\s+", "", lines[i])
                    indent = len(lines[i]) - len(lines[i].lstrip())
                    ol_items.append((indent, item_text))
                    i += 1
                self._render_ordered_list(ol_items)
                continue

            if self._is_table_separator(lines, i):
                table_lines = []
                while i < len(lines) and lines[i].strip() != "":
                    table_lines.append(lines[i])
                    i += 1
                self._render_table(table_lines)
                continue

            if line.strip() == "":
                self.preview_text.insert(tk.END, "\n")
                i += 1
                continue

            self._render_paragraph(line)
            i += 1

        if in_code_block and code_block_lines:
            self._render_code_block("\n".join(code_block_lines), code_lang)

    def _render_heading(self, line):
        match = re.match(r"^(#{1,6})\s+(.*)", line)
        if match:
            level = len(match.group(1))
            content = match.group(2).strip()
            tag = f"h{level}"
            self._render_inline(content, [tag])
            self.preview_text.insert(tk.END, "\n")

    def _render_hr(self):
        self.preview_text.insert(tk.END, "\n")
        self.preview_text.insert(tk.END, " " * 80 + "\n", "hr")
        self.preview_text.insert(tk.END, "\n")

    def _render_code_block(self, code, lang):
        self.preview_text.insert(tk.END, "\n")
        for j, line in enumerate(code.split("\n")):
            self.preview_text.insert(tk.END, "  ", "codeblock_bg")
            self.preview_text.insert(tk.END, line + "\n", ("codeblock", "codeblock_bg"))
        self.preview_text.insert(tk.END, "\n")

    def _render_quote(self, text):
        for line in text.split("\n"):
            self.preview_text.insert(tk.END, " ", "quote_bar")
            self.preview_text.insert(tk.END, "  ", "quote")
            self._render_inline(line, ["quote"])
            self.preview_text.insert(tk.END, "\n")
        self.preview_text.insert(tk.END, "\n")

    def _render_unordered_list(self, items):
        for indent, text in items:
            bullet_indent = "  " * (indent // 2)
            self.preview_text.insert(tk.END, bullet_indent, "para")
            self.preview_text.insert(tk.END, "● ", "ul_bullet")
            self._render_inline(text, ["para"])
            self.preview_text.insert(tk.END, "\n")
        self.preview_text.insert(tk.END, "\n")

    def _render_ordered_list(self, items):
        num = 1
        for indent, text in items:
            bullet_indent = "  " * (indent // 2)
            self.preview_text.insert(tk.END, bullet_indent, "para")
            self.preview_text.insert(tk.END, f"{num}. ", "ol_num")
            self._render_inline(text, ["para"])
            self.preview_text.insert(tk.END, "\n")
            num += 1
        self.preview_text.insert(tk.END, "\n")

    def _is_table_separator(self, lines, i):
        if i + 1 >= len(lines):
            return False
        if "|" not in lines[i]:
            return False
        next_line = lines[i + 1]
        if "|" not in next_line:
            return False
        cells = [c.strip() for c in next_line.split("|") if c.strip() != ""]
        if not cells:
            return False
        for cell in cells:
            if not re.match(r"^:?-{2,}:?$", cell):
                return False
        return True

    def _render_table(self, table_lines):
        if len(table_lines) < 2:
            return

        header_cells = [c.strip() for c in table_lines[0].split("|")]
        header_cells = [c for c in header_cells if c != ""]

        sep_cells = [c.strip() for c in table_lines[1].split("|")]
        sep_cells = [c for c in sep_cells if c != ""]

        data_rows = []
        for row_line in table_lines[2:]:
            cells = [c.strip() for c in row_line.split("|")]
            cells = [c for c in cells if c != ""]
            data_rows.append(cells)

        col_widths = []
        for j, h in enumerate(header_cells):
            max_w = len(h)
            for row in data_rows:
                if j < len(row):
                    max_w = max(max_w, len(row[j]))
            col_widths.append(min(max_w + 4, 30))

        self.preview_text.insert(tk.END, "\n")

        header_str = ""
        for j, h in enumerate(header_cells):
            w = col_widths[j]
            header_str += f" {h.ljust(w - 2)} "
        self.preview_text.insert(tk.END, header_str + "\n", "table_header")

        sep_str = ""
        for j, s in enumerate(sep_cells):
            w = col_widths[j]
            sep_str += "-" * w
        self.preview_text.insert(tk.END, sep_str + "\n", "table_sep")

        for row in data_rows:
            row_str = ""
            for j in range(len(header_cells)):
                w = col_widths[j]
                cell = row[j] if j < len(row) else ""
                row_str += f" {cell.ljust(w - 2)} "
            self.preview_text.insert(tk.END, row_str + "\n", "table_cell")

        self.preview_text.insert(tk.END, "\n")

    def _render_paragraph(self, line):
        self._render_inline(line, ["para"])
        self.preview_text.insert(tk.END, "\n")

    def _render_inline(self, text, base_tags):
        pos = 0
        pattern = re.compile(
            r"(\*\*\*[^*]+\*\*\*)"
            r"|(\*\*[^*]+\*\*)"
            r"|(\*[^*]+\*)"
            r"|(`[^`]+`)"
            r"|(!\[[^\]]*\]\([^)]+\))"
            r"|(\[[^\]]+\]\([^)]+\))"
        )

        for match in pattern.finditer(text):
            start, end = match.span()
            if start > pos:
                self.preview_text.insert(tk.END, text[pos:start], base_tags)

            matched_text = match.group(0)

            if matched_text.startswith("***") and matched_text.endswith("***"):
                content = matched_text[3:-3]
                self.preview_text.insert(tk.END, content, base_tags + ["bold_italic"])
            elif matched_text.startswith("**") and matched_text.endswith("**"):
                content = matched_text[2:-2]
                self.preview_text.insert(tk.END, content, base_tags + ["bold"])
            elif matched_text.startswith("*") and matched_text.endswith("*"):
                content = matched_text[1:-1]
                self.preview_text.insert(tk.END, content, base_tags + ["italic"])
            elif matched_text.startswith("`") and matched_text.endswith("`"):
                content = matched_text[1:-1]
                self.preview_text.insert(tk.END, content, base_tags + ["code"])
            elif matched_text.startswith("!["):
                img_match = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", matched_text)
                if img_match:
                    alt = img_match.group(1) or "图片"
                    self.preview_text.insert(tk.END, f"[图片: {alt}]", base_tags + ["link"])
            elif matched_text.startswith("["):
                link_match = re.match(r"\[([^\]]+)\]\(([^)]+)\)", matched_text)
                if link_match:
                    link_text = link_match.group(1)
                    self.preview_text.insert(tk.END, link_text, base_tags + ["link"])

            pos = end

        if pos < len(text):
            self.preview_text.insert(tk.END, text[pos:], base_tags)
