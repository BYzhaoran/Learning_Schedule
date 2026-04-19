from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tkinter import BOTH, END, X, Tk, StringVar, messagebox, ttk
from tkinter.scrolledtext import ScrolledText


BASE_DIR = Path(__file__).resolve().parent
MONTH_DIR = BASE_DIR / "月计划"
STATE_DIR = Path.home() / ".local" / "share" / "learning_schedule_planner"
STATE_FILE = STATE_DIR / "state.json"

TASK_HEADINGS = {"核心任务", "关键实验", "交付物", "验收标准"}
MONTH_FILE_PATTERN = re.compile(r"^M(\d{2})\.md$")
LIST_ITEM_PATTERN = re.compile(r"^\s*(?:[-*]|\d+\.)\s+(.*)$")


@dataclass
class TaskItem:
    key: str
    section: str
    text: str
    source: str
    done: bool = False


@dataclass
class MonthDocument:
    number: int
    path: Path
    title: str
    lines: list[str]


class StateStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.data = {"version": 1, "months": {}}
        self.load()

    def load(self) -> None:
        if self.path.exists():
            try:
                self.data = json.loads(self.path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                self.data = {"version": 1, "months": {}}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")

    def month_bucket(self, month_key: str) -> dict:
        months = self.data.setdefault("months", {})
        bucket = months.setdefault(month_key, {})
        bucket.setdefault("task_states", {})
        bucket.setdefault("custom_tasks", [])
        bucket.setdefault("note", "")
        return bucket


def discover_month_documents() -> list[MonthDocument]:
    documents: list[MonthDocument] = []
    for path in sorted(MONTH_DIR.glob("M*.md")):
        match = MONTH_FILE_PATTERN.match(path.name)
        if not match:
            continue
        number = int(match.group(1))
        lines = path.read_text(encoding="utf-8").splitlines()
        title = next((line.lstrip("# ").strip() for line in lines if line.startswith("# ")), path.stem)
        documents.append(MonthDocument(number=number, path=path, title=title, lines=lines))
    return documents


def extract_tasks(document: MonthDocument, state: dict) -> list[TaskItem]:
    task_states = state.setdefault("task_states", {})
    tasks: list[TaskItem] = []
    current_section = ""

    for line in document.lines:
        heading_match = re.match(r"^##\s+(.*)$", line)
        if heading_match:
            current_section = heading_match.group(1).strip()
            continue

        if current_section not in TASK_HEADINGS:
            continue

        item_match = LIST_ITEM_PATTERN.match(line)
        if not item_match:
            continue

        text = item_match.group(1).strip()
        key = uuid.uuid5(uuid.NAMESPACE_URL, f"{document.path.name}:{current_section}:{text}").hex
        done = bool(task_states.get(key, False))
        tasks.append(TaskItem(key=key, section=current_section, text=text, source="markdown", done=done))

    for item in state.get("custom_tasks", []):
        tasks.append(
            TaskItem(
                key=f"custom:{item['id']}",
                section="自定义待办",
                text=item["text"],
                source="custom",
                done=bool(item.get("done", False)),
            )
        )

    return tasks


class LearningPlannerApp(Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Learning Schedule Planner")
        self.geometry("1320x860")
        self.minsize(1100, 720)

        self.store = StateStore(STATE_FILE)
        self.documents = discover_month_documents()
        if not self.documents:
            raise RuntimeError("未找到月计划文件，请确认 月计划/M01.md 到 M24.md 已存在。")

        self.current_document: MonthDocument | None = None
        self.current_tasks: list[TaskItem] = []
        self.current_task_lookup: dict[str, TaskItem] = {}
        self.current_month_key = ""

        self.selection_var = StringVar(value="")
        self.progress_var = StringVar(value="")
        self.status_var = StringVar(value="")
        self.task_input_var = StringVar(value="")

        self._setup_style()
        self._build_layout()
        self._bind_events()
        self._open_initial_month()

    def _setup_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Root.TFrame", background="#0f172a")
        style.configure("Sidebar.TFrame", background="#111827")
        style.configure("Main.TFrame", background="#0f172a")
        style.configure("Card.TFrame", background="#111827", relief="flat")
        style.configure("CardTitle.TLabel", background="#111827", foreground="#f8fafc", font=("Sans", 12, "bold"))
        style.configure("CardText.TLabel", background="#111827", foreground="#cbd5e1", font=("Sans", 10))
        style.configure("Sidebar.TLabel", background="#111827", foreground="#e5e7eb", font=("Sans", 10))
        style.configure("Header.TLabel", background="#0f172a", foreground="#f8fafc", font=("Sans", 18, "bold"))
        style.configure("SubHeader.TLabel", background="#0f172a", foreground="#cbd5e1", font=("Sans", 10))
        style.configure("Accent.TButton", padding=(12, 8), background="#2563eb", foreground="white")
        style.map("Accent.TButton", background=[("active", "#1d4ed8")])
        style.configure("TButton", padding=(10, 6))
        style.configure("TEntry", fieldbackground="#1f2937", foreground="#f8fafc", insertcolor="#f8fafc")
        style.configure("Treeview", background="#111827", fieldbackground="#111827", foreground="#f8fafc", rowheight=28)
        style.configure("Treeview.Heading", background="#1f2937", foreground="#e5e7eb", font=("Sans", 10, "bold"))

    def _build_layout(self) -> None:
        self.configure(background="#0f172a")

        root = ttk.Frame(self, style="Root.TFrame")
        root.pack(fill=BOTH, expand=True)

        header = ttk.Frame(root, style="Main.TFrame")
        header.pack(fill=X, padx=20, pady=(18, 10))

        ttk.Label(header, text="计划与待办面板", style="Header.TLabel").pack(anchor="w")
        ttk.Label(header, text="直接读取月计划 Markdown，并把完成状态保存到本地。", style="SubHeader.TLabel").pack(anchor="w", pady=(4, 0))

        body = ttk.Frame(root, style="Main.TFrame")
        body.pack(fill=BOTH, expand=True, padx=20, pady=(0, 18))

        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=3)
        body.columnconfigure(2, weight=2)
        body.rowconfigure(0, weight=1)

        sidebar = ttk.Frame(body, style="Sidebar.TFrame")
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        sidebar.columnconfigure(0, weight=1)
        sidebar.rowconfigure(1, weight=1)

        month_card = ttk.Frame(sidebar, style="Card.TFrame")
        month_card.grid(row=0, column=0, sticky="nsew", pady=(0, 12))
        month_card.columnconfigure(0, weight=1)

        ttk.Label(month_card, text="月份", style="CardTitle.TLabel").pack(anchor="w", padx=14, pady=(12, 8))
        self.month_list = ttk.Treeview(month_card, columns=("title",), show="tree", selectmode="browse", height=18)
        self.month_list.column("#0", width=72, anchor="center")
        self.month_list.pack(fill=BOTH, expand=True, padx=12, pady=(0, 12))

        self.progress_label = ttk.Label(sidebar, textvariable=self.progress_var, style="Sidebar.TLabel", wraplength=280, justify="left")
        self.progress_label.grid(row=1, column=0, sticky="sw", pady=(0, 10))

        main = ttk.Frame(body, style="Main.TFrame")
        main.grid(row=0, column=1, sticky="nsew", padx=(0, 12))
        main.columnconfigure(0, weight=1)
        main.rowconfigure(1, weight=1)

        summary_card = ttk.Frame(main, style="Card.TFrame")
        summary_card.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        summary_card.columnconfigure(0, weight=1)
        ttk.Label(summary_card, textvariable=self.selection_var, style="CardTitle.TLabel").pack(anchor="w", padx=14, pady=(12, 4))
        ttk.Label(summary_card, textvariable=self.status_var, style="CardText.TLabel").pack(anchor="w", padx=14, pady=(0, 12))

        content_card = ttk.Frame(main, style="Card.TFrame")
        content_card.grid(row=1, column=0, sticky="nsew")
        content_card.columnconfigure(0, weight=1)
        content_card.rowconfigure(0, weight=1)

        self.doc_text = ScrolledText(content_card, wrap="word", bg="#111827", fg="#e5e7eb", insertbackground="#e5e7eb", relief="flat", padx=16, pady=16)
        self.doc_text.grid(row=0, column=0, sticky="nsew")
        self.doc_text.configure(state="disabled")
        self.doc_text.tag_configure("h1", font=("Sans", 18, "bold"), foreground="#f8fafc", spacing1=8, spacing3=10)
        self.doc_text.tag_configure("h2", font=("Sans", 14, "bold"), foreground="#93c5fd", spacing1=10, spacing3=6)
        self.doc_text.tag_configure("h3", font=("Sans", 11, "bold"), foreground="#cbd5e1", spacing1=4, spacing3=4)
        self.doc_text.tag_configure("bullet", lmargin1=16, lmargin2=32, foreground="#cbd5e1", spacing1=2, spacing3=2)
        self.doc_text.tag_configure("body", foreground="#e5e7eb", spacing1=2, spacing3=2)

        task_card = ttk.Frame(body, style="Card.TFrame")
        task_card.grid(row=0, column=2, sticky="nsew")
        task_card.columnconfigure(0, weight=1)
        task_card.rowconfigure(1, weight=1)

        task_header = ttk.Frame(task_card, style="Card.TFrame")
        task_header.grid(row=0, column=0, sticky="ew")
        task_header.columnconfigure(0, weight=1)
        ttk.Label(task_header, text="待办", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w", padx=14, pady=(12, 4))

        add_bar = ttk.Frame(task_header, style="Card.TFrame")
        add_bar.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 10))
        add_bar.columnconfigure(0, weight=1)
        ttk.Entry(add_bar, textvariable=self.task_input_var).grid(row=0, column=0, sticky="ew", padx=(2, 8))
        ttk.Button(add_bar, text="新增", style="Accent.TButton", command=self._add_custom_task).grid(row=0, column=1)

        self.task_tree = ttk.Treeview(task_card, columns=("section", "status"), show="headings", selectmode="browse")
        self.task_tree.heading("section", text="模块")
        self.task_tree.heading("status", text="状态")
        self.task_tree.column("section", width=110, anchor="w")
        self.task_tree.column("status", width=70, anchor="center")
        self.task_tree.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.task_tree.bind("<Double-1>", self._toggle_selected_task)
        self.task_tree.bind("<space>", self._toggle_selected_task)

    def _bind_events(self) -> None:
        self.month_list.bind("<<TreeviewSelect>>", self._on_month_selected)
        self.bind("<Delete>", self._delete_selected_custom_task)

    def _open_initial_month(self) -> None:
        current_month = datetime.now().month
        target = next((doc for doc in self.documents if doc.number == current_month), self.documents[0])
        for doc in self.documents:
            self.month_list.insert("", END, iid=doc.path.name, text=f"M{doc.number:02d}")

        self.month_list.selection_set(target.path.name)
        self.month_list.focus(target.path.name)
        self.month_list.see(target.path.name)
        self._load_month(target.path.name)

    def _load_month(self, month_key: str) -> None:
        document = next((doc for doc in self.documents if doc.path.name == month_key), self.documents[0])
        self.current_document = document
        self.current_month_key = month_key

        bucket = self.store.month_bucket(month_key)
        self.current_tasks = extract_tasks(document, bucket)
        self.current_task_lookup = {item.key: item for item in self.current_tasks}

        self.selection_var.set(f"{document.title} · {month_key}")
        self.status_var.set(f"文件路径：{document.path.relative_to(BASE_DIR)}")
        self.progress_var.set(self._progress_text())

        self._render_document(document.lines)
        self._refresh_task_tree()

    def _render_document(self, lines: list[str]) -> None:
        self.doc_text.configure(state="normal")
        self.doc_text.delete("1.0", END)

        for line in lines:
            stripped = line.rstrip()
            if stripped.startswith("# "):
                tag = "h1"
                text = stripped[2:].strip()
            elif stripped.startswith("## "):
                tag = "h2"
                text = stripped[3:].strip()
            elif stripped.startswith("### "):
                tag = "h3"
                text = stripped[4:].strip()
            else:
                match = LIST_ITEM_PATTERN.match(stripped)
                if match:
                    tag = "bullet"
                    text = "• " + match.group(1).strip()
                else:
                    tag = "body"
                    text = stripped

            self.doc_text.insert(END, text + "\n", tag)

        self.doc_text.configure(state="disabled")

    def _refresh_task_tree(self) -> None:
        for item_id in self.task_tree.get_children():
            self.task_tree.delete(item_id)

        grouped: dict[str, list[TaskItem]] = {}
        for task in self.current_tasks:
            grouped.setdefault(task.section, []).append(task)

        section_order = ["核心任务", "关键实验", "交付物", "验收标准", "自定义待办"]
        self.task_tree.configure(displaycolumns=("section", "status"), show="tree headings")
        self.task_tree.column("#0", width=360, anchor="w")
        self.task_tree.heading("#0", text="任务")

        for section in section_order:
            for task in grouped.get(section, []):
                status = "完成" if task.done else "未做"
                label = task.text if task.source != "custom" else f"[自定义] {task.text}"
                self.task_tree.insert("", END, iid=task.key, text=label, values=(task.section, status))

        self.progress_var.set(self._progress_text())

    def _progress_text(self) -> str:
        total = len(self.current_tasks)
        done = sum(1 for task in self.current_tasks if task.done)
        if total == 0:
            return "当前月还没有可勾选任务。"
        percent = round(done / total * 100)
        return f"完成进度：{done}/{total}，约 {percent}%\n双击任务可切换完成状态；输入框可新增自定义待办。"

    def _on_month_selected(self, event: object) -> None:
        selection = self.month_list.selection()
        if not selection:
            return
        self._load_month(selection[0])

    def _toggle_selected_task(self, event: object | None = None) -> None:
        selection = self.task_tree.selection()
        if not selection:
            return

        task = self.current_task_lookup.get(selection[0])
        if not task:
            return

        task.done = not task.done
        bucket = self.store.month_bucket(self.current_month_key)
        if task.source == "markdown":
            bucket["task_states"][task.key] = task.done
        else:
            custom_id = task.key.split(":", 1)[1]
            for item in bucket["custom_tasks"]:
                if item["id"] == custom_id:
                    item["done"] = task.done
                    break

        self.store.save()
        self._refresh_task_tree()

    def _add_custom_task(self) -> None:
        text = self.task_input_var.get().strip()
        if not text:
            return

        bucket = self.store.month_bucket(self.current_month_key)
        custom_id = uuid.uuid4().hex
        bucket["custom_tasks"].append(
            {
                "id": custom_id,
                "text": text,
                "done": False,
                "created_at": datetime.now().isoformat(timespec="seconds"),
            }
        )
        self.store.save()
        self.task_input_var.set("")
        self._load_month(self.current_month_key)

    def _delete_selected_custom_task(self, event: object | None = None) -> None:
        selection = self.task_tree.selection()
        if not selection:
            return

        task = self.current_task_lookup.get(selection[0])
        if not task or task.source != "custom":
            return

        if not messagebox.askyesno("删除待办", f"确认删除：{task.text}"):
            return

        custom_id = task.key.split(":", 1)[1]
        bucket = self.store.month_bucket(self.current_month_key)
        bucket["custom_tasks"] = [item for item in bucket["custom_tasks"] if item["id"] != custom_id]
        self.store.save()
        self._load_month(self.current_month_key)


def main() -> None:
    app = LearningPlannerApp()
    app.mainloop()


if __name__ == "__main__":
    main()