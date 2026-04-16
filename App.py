import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import calendar
import json
from pathlib import Path


class SchedulerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Scheduler")
        self.geometry("1200x760")
        self.minsize(980, 640)
        self.current_theme = "Light"
        self.configure(bg="#F6F8FB")

        self.tasks: list[dict[str, str]] = []
        self.sorted_task_indices: list[int] = []
        self.selected_task_index: int | None = None
        self.hovered_task_index: int | None = None
        self.time_slots = self._generate_time_slots(7, 22, 30)
        self.current_view = "Day"
        self.current_date = datetime.now().date()
        self.weekday_options = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        self.week_start_day = "Sunday"
        self.current_account = "default"
        self.selected_recurrence_days: list[str] = []
        self.sidebar_visible = False
        self.color_options = {
            "Blue": "#DDE9FF",
            "Green": "#DDF7EC",
            "Pink": "#FFE3EA",
            "Purple": "#EDE5FF",
            "Orange": "#FFEBD9",
            "Cyan": "#DDF2FF",
            "Yellow": "#FFF5CC",
        }
        self.default_color_name = "Blue"

        self._configure_styles()
        self._build_layout()
        if not self._load_account_data(self.current_account):
            self._seed_tasks()
            self._save_account_data()
        self._apply_theme()
        self._update_account_header()
        self._render_tasks()
        self._draw_timeline()

    @staticmethod
    def _generate_time_slots(start_hour: int, end_hour: int, interval_minutes: int) -> list[str]:
        slots: list[str] = []
        current_minutes = start_hour * 60
        end_minutes = end_hour * 60
        while current_minutes <= end_minutes:
            hour = current_minutes // 60
            minute = current_minutes % 60
            slots.append(f"{hour:02d}:{minute:02d}")
            current_minutes += interval_minutes
        return slots

    @staticmethod
    def _time_to_minutes(time_value: str) -> int:
        hour, minute = time_value.split(":")
        return (int(hour) * 60) + int(minute)

    def _get_theme_palette(self) -> dict[str, str]:
        if self.current_theme == "Dark":
            return {
                "app_bg": "#0F1218",
                "soft_bg": "#151A22",
                "card_bg": "#1C222D",
                "header_fg": "#E8EDF7",
                "subheader_fg": "#AFB8C8",
                "field_fg": "#C2CBD9",
                "task_fg": "#D3DCEB",
                "button_primary": "#6C8EFF",
                "button_primary_active": "#5A7FF0",
                "button_secondary": "#2A313D",
                "button_secondary_active": "#343D4B",
                "button_secondary_fg": "#E5ECF8",
                "list_bg": "#181E28",
                "list_select_bg": "#3E4758",
                "list_select_fg": "#F0F4FB",
                "canvas_bg": "#141A23",
                "line": "#4A4F59",
                "muted": "#9AA3B2",
                "text_strong": "#E6ECF8",
                "text_body": "#C0C9D7",
                "column_bg": "#1A202A",
                "column_outline": "#4A4F59",
                "month_cell_bg": "#1A202A",
                "month_cell_outline": "#4A4F59",
            }
        return {
            "app_bg": "#F6F8FB",
            "soft_bg": "#EEF3F9",
            "card_bg": "#FFFFFF",
            "header_fg": "#2C3E50",
            "subheader_fg": "#607087",
            "field_fg": "#4C6077",
            "task_fg": "#2F4156",
            "button_primary": "#6C8EFF",
            "button_primary_active": "#5A7FF0",
            "button_secondary": "#E8EEF8",
            "button_secondary_active": "#DFE8F5",
            "button_secondary_fg": "#2F4156",
            "list_bg": "#F9FBFE",
            "list_select_bg": "#D7E5FF",
            "list_select_fg": "#1F2A3A",
            "canvas_bg": "#FCFDFF",
            "line": "#DCE5F2",
            "muted": "#6A7D95",
            "text_strong": "#2F4260",
            "text_body": "#4C6077",
            "column_bg": "#FAFCFF",
            "column_outline": "#E4EBF6",
            "month_cell_bg": "#FBFCFE",
            "month_cell_outline": "#E1E9F4",
        }

    def _configure_styles(self) -> None:
        palette = self._get_theme_palette()
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("Card.TFrame", background=palette["card_bg"])
        style.configure("Soft.TFrame", background=palette["soft_bg"])
        style.configure(
            "Header.TLabel",
            background=palette["app_bg"],
            foreground=palette["header_fg"],
            font=("Segoe UI", 24, "bold"),
        )
        style.configure(
            "SubHeader.TLabel",
            background=palette["app_bg"],
            foreground=palette["subheader_fg"],
            font=("Segoe UI", 11),
        )
        style.configure(
            "Field.TLabel",
            background=palette["card_bg"],
            foreground=palette["field_fg"],
            font=("Segoe UI", 10, "bold"),
        )
        style.configure(
            "Task.TLabel",
            background=palette["card_bg"],
            foreground=palette["task_fg"],
            font=("Segoe UI", 10),
        )
        style.configure(
            "Period.TLabel",
            background=palette["card_bg"],
            foreground=palette["task_fg"],
            font=("Segoe UI", 13, "bold"),
        )
        style.configure(
            "Primary.TButton",
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
            padding=(12, 8),
        )
        style.map(
            "Primary.TButton",
            background=[("active", palette["button_primary_active"]), ("!disabled", palette["button_primary"])],
            foreground=[("!disabled", "#FFFFFF")],
        )
        style.configure(
            "Secondary.TButton",
            font=("Segoe UI", 10),
            borderwidth=0,
            padding=(10, 6),
        )
        style.map(
            "Secondary.TButton",
            background=[("active", palette["button_secondary_active"]), ("!disabled", palette["button_secondary"])],
            foreground=[("!disabled", palette["button_secondary_fg"])],
        )

    def _apply_theme(self) -> None:
        palette = self._get_theme_palette()
        self.configure(bg=palette["app_bg"])
        self._configure_styles()
        if hasattr(self, "timeline_canvas"):
            self.timeline_canvas.configure(background=palette["canvas_bg"])
        if hasattr(self, "task_listbox"):
            self.task_listbox.configure(
                background=palette["list_bg"],
                foreground=palette["task_fg"],
                selectbackground=palette["list_select_bg"],
                selectforeground=palette["list_select_fg"],
            )

    def _build_layout(self) -> None:
        outer = ttk.Frame(self, style="Soft.TFrame", padding=18)
        outer.pack(fill="both", expand=True)

        header = ttk.Frame(outer, style="Soft.TFrame")
        header.pack(fill="x", pady=(0, 14))
        header.columnconfigure(1, weight=1)
        header.columnconfigure(2, weight=0)

        self.sidebar_toggle_text = tk.StringVar(value="☰")
        ttk.Button(
            header,
            textvariable=self.sidebar_toggle_text,
            style="Secondary.TButton",
            command=self._toggle_sidebar,
            width=3,
        ).grid(row=0, column=0, sticky="nw", padx=(0, 10), pady=(4, 0))

        header_text = ttk.Frame(header, style="Soft.TFrame")
        header_text.grid(row=0, column=1, sticky="w")
        ttk.Label(header_text, text="Daily Scheduler", style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            header_text,
            text="Plan your day with a clean, light interface.",
            style="SubHeader.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        self.account_button_text = tk.StringVar(value=f"Account: {self.current_account}")
        ttk.Button(
            header,
            textvariable=self.account_button_text,
            style="Secondary.TButton",
            command=self._open_account_dialog,
        ).grid(row=0, column=2, sticky="ne")

        main_area = ttk.Frame(outer, style="Soft.TFrame")
        main_area.pack(fill="both", expand=True)
        main_area.columnconfigure(0, weight=0)
        main_area.columnconfigure(1, weight=1)
        main_area.rowconfigure(0, weight=1)

        self.sidebar_frame = ttk.Frame(main_area, style="Card.TFrame", padding=14, width=210)
        self.sidebar_frame.grid(row=0, column=0, sticky="ns", padx=(0, 10))
        self.sidebar_frame.grid_propagate(False)
        self._build_sidebar()
        self.sidebar_frame.grid_remove()

        body = ttk.Frame(main_area, style="Soft.TFrame")
        body.grid(row=0, column=1, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=7)
        body.rowconfigure(0, weight=1)

        self.left_card = ttk.Frame(body, style="Card.TFrame", padding=16, width=260)
        self.left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.left_card.grid_propagate(False)
        self.right_card = ttk.Frame(body, style="Card.TFrame", padding=16)
        self.right_card.grid(row=0, column=1, sticky="nsew")

        self._build_left_panel()
        self._build_right_panel()

    def _build_sidebar(self) -> None:
        ttk.Label(self.sidebar_frame, text="Settings", style="Field.TLabel").pack(anchor="w")
        ttk.Label(
            self.sidebar_frame,
            text="Use this panel for quick controls.",
            style="Task.TLabel",
            wraplength=180,
            justify="left",
        ).pack(anchor="w", pady=(6, 12))

        ttk.Button(
            self.sidebar_frame,
            text="Settings",
            style="Secondary.TButton",
            command=self._open_sidebar_settings,
        ).pack(fill="x", pady=(0, 12))

        ttk.Separator(self.sidebar_frame, orient="horizontal").pack(fill="x", pady=(0, 12))

        ttk.Label(self.sidebar_frame, text="Tips", style="Field.TLabel").pack(anchor="w")
        tips = [
            "Select a block in the planner to edit it.",
            "Use Recurring Days for weekly repeats.",
            "Switch Day / Week / Month / Year views above.",
        ]
        for tip in tips:
            ttk.Label(
                self.sidebar_frame,
                text=f"- {tip}",
                style="Task.TLabel",
                wraplength=180,
                justify="left",
            ).pack(anchor="w", pady=(2, 0))

    def _toggle_sidebar(self) -> None:
        self.sidebar_visible = not self.sidebar_visible
        if self.sidebar_visible:
            self.sidebar_frame.grid()
        else:
            self.sidebar_frame.grid_remove()

    def _open_account_dialog(self) -> None:
        dialog = tk.Toplevel(self)
        dialog.title("Account Login")
        dialog.configure(bg="#FFFFFF")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)

        frame = ttk.Frame(dialog, padding=14, style="Card.TFrame")
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Account", style="Field.TLabel").pack(anchor="w")
        ttk.Label(
            frame,
            text="Log into an existing account or create a new one.",
            style="Task.TLabel",
            wraplength=280,
            justify="left",
        ).pack(anchor="w", pady=(6, 10))

        account_var = tk.StringVar(value=self.current_account)
        ttk.Label(frame, text="Existing account", style="Task.TLabel").pack(anchor="w")
        account_combo = ttk.Combobox(
            frame,
            textvariable=account_var,
            values=self._list_accounts(),
            state="readonly",
        )
        account_combo.pack(fill="x", pady=(4, 10))

        new_account_var = tk.StringVar()
        ttk.Label(frame, text="Create account", style="Task.TLabel").pack(anchor="w")
        ttk.Entry(frame, textvariable=new_account_var).pack(fill="x", pady=(4, 12))

        def login_account() -> None:
            target = account_var.get().strip()
            if not target:
                return
            self._switch_account(target)
            dialog.destroy()

        def create_and_login() -> None:
            created = self._sanitize_account_name(new_account_var.get().strip())
            if not created:
                return
            self._create_account_if_missing(created)
            self._switch_account(created)
            dialog.destroy()

        button_row = ttk.Frame(frame, style="Card.TFrame")
        button_row.pack(fill="x")
        ttk.Button(button_row, text="Log In", style="Primary.TButton", command=login_account).pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(button_row, text="Create + Log In", style="Secondary.TButton", command=create_and_login).pack(
            side="left", fill="x", expand=True, padx=(8, 0)
        )

    def _open_sidebar_settings(self) -> None:
        settings_window = tk.Toplevel(self)
        settings_window.title("Settings")
        settings_window.configure(bg="#FFFFFF")
        settings_window.transient(self)
        settings_window.grab_set()
        settings_window.resizable(False, False)

        content = ttk.Frame(settings_window, padding=14, style="Card.TFrame")
        content.pack(fill="both", expand=True)
        ttk.Label(content, text="Sidebar Settings", style="Field.TLabel").pack(anchor="w")
        ttk.Label(
            content,
            text="Categories are scaffolded for future options.",
            style="Task.TLabel",
            wraplength=260,
            justify="left",
        ).pack(anchor="w", pady=(8, 12))

        accordion = ttk.Frame(content, style="Card.TFrame")
        accordion.pack(fill="x")
        week_start_var = tk.StringVar(value=self.week_start_day)
        theme_var = tk.StringVar(value=self.current_theme)

        def create_section(title: str, expanded: bool = False) -> ttk.Frame:
            section = ttk.Frame(accordion, style="Card.TFrame")
            section.pack(fill="x", pady=(0, 8))

            body = ttk.Frame(section, style="Card.TFrame")
            state_var = tk.StringVar(value=f"▼ {title}" if expanded else f"▶ {title}")

            def toggle_section() -> None:
                if body.winfo_ismapped():
                    body.pack_forget()
                    state_var.set(f"▶ {title}")
                else:
                    body.pack(fill="x", padx=(8, 0), pady=(4, 0))
                    state_var.set(f"▼ {title}")

            ttk.Button(
                section,
                textvariable=state_var,
                style="Secondary.TButton",
                command=toggle_section,
            ).pack(fill="x")

            if expanded:
                body.pack(fill="x", padx=(8, 0), pady=(4, 0))
            return body

        account_body = create_section("Account", expanded=True)
        ttk.Label(account_body, text="Active account", style="Task.TLabel").pack(anchor="w", pady=(0, 2))
        account_var = tk.StringVar(value=self.current_account)
        account_combo = ttk.Combobox(
            account_body,
            textvariable=account_var,
            values=self._list_accounts(),
            state="readonly",
        )
        account_combo.pack(fill="x", pady=(0, 8))

        ttk.Label(account_body, text="Create new account", style="Task.TLabel").pack(anchor="w", pady=(0, 2))
        new_account_var = tk.StringVar()
        ttk.Entry(account_body, textvariable=new_account_var).pack(fill="x")

        calendar_body = create_section("Calendar", expanded=True)
        ttk.Label(calendar_body, text="Start week on", style="Task.TLabel").pack(anchor="w", pady=(0, 2))
        ttk.Combobox(
            calendar_body,
            textvariable=week_start_var,
            values=self.weekday_options,
            state="readonly",
        ).pack(fill="x")

        ai_body = create_section("AI Assistant")
        ttk.Label(
            ai_body,
            text="- Suggest schedule improvements\n- Smart conflict hints",
            style="Task.TLabel",
            justify="left",
        ).pack(anchor="w")

        theme_body = create_section("Theme")
        ttk.Radiobutton(theme_body, text="Light", variable=theme_var, value="Light").pack(anchor="w")
        ttk.Radiobutton(theme_body, text="Dark", variable=theme_var, value="Dark").pack(anchor="w")

        advanced_body = create_section("Advanced")
        ttk.Label(
            advanced_body,
            text="- Data backup/export\n- Keyboard shortcuts\n- Integrations",
            style="Task.TLabel",
            justify="left",
        ).pack(anchor="w")

        button_row = ttk.Frame(content, style="Card.TFrame")
        button_row.pack(fill="x", pady=(4, 0))

        def save_settings() -> None:
            created_name = self._sanitize_account_name(new_account_var.get().strip())
            target_account = account_var.get().strip()
            if created_name:
                self._create_account_if_missing(created_name)
                target_account = created_name
            if target_account:
                self._switch_account(target_account)
            self.week_start_day = week_start_var.get()
            self.current_theme = theme_var.get()
            self._apply_theme()
            self._draw_timeline()
            self._save_account_data()
            settings_window.destroy()

        ttk.Button(button_row, text="Save", style="Primary.TButton", command=save_settings).pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(button_row, text="Close", style="Secondary.TButton", command=settings_window.destroy).pack(
            side="left", fill="x", expand=True, padx=(8, 0)
        )

    def _build_left_panel(self) -> None:
        ttk.Label(self.left_card, text="Add a Task", style="Field.TLabel").pack(anchor="w", pady=(0, 8))

        form = ttk.Frame(self.left_card, style="Card.TFrame")
        form.pack(fill="x")
        form.columnconfigure(0, weight=1)

        ttk.Label(form, text="Title", style="Field.TLabel").grid(row=0, column=0, sticky="w")
        self.title_var = tk.StringVar()
        title_entry = ttk.Entry(form, textvariable=self.title_var, font=("Segoe UI", 10))
        title_entry.grid(row=1, column=0, sticky="ew", pady=(4, 10))

        ttk.Label(form, text="Description", style="Field.TLabel").grid(row=2, column=0, sticky="w")
        self.desc_var = tk.StringVar()
        desc_entry = ttk.Entry(form, textvariable=self.desc_var, font=("Segoe UI", 10))
        desc_entry.grid(row=3, column=0, sticky="ew", pady=(4, 10))

        time_row = ttk.Frame(form, style="Card.TFrame")
        time_row.grid(row=4, column=0, sticky="ew", pady=(0, 12))
        time_row.columnconfigure(0, weight=1)
        time_row.columnconfigure(1, weight=1)

        ttk.Label(time_row, text="Start", style="Field.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(time_row, text="End", style="Field.TLabel").grid(row=0, column=1, sticky="w")

        self.start_var = tk.StringVar(value="09:00")
        self.end_var = tk.StringVar(value="10:00")
        ttk.Combobox(time_row, textvariable=self.start_var, values=self.time_slots, state="readonly").grid(
            row=1, column=0, sticky="ew", padx=(0, 8), pady=(4, 0)
        )
        ttk.Combobox(time_row, textvariable=self.end_var, values=self.time_slots, state="readonly").grid(
            row=1, column=1, sticky="ew", pady=(4, 0)
        )

        ttk.Label(form, text="Date (YYYY-MM-DD)", style="Field.TLabel").grid(row=5, column=0, sticky="w", pady=(2, 0))
        self.date_var = tk.StringVar(value=self.current_date.strftime("%Y-%m-%d"))
        ttk.Entry(form, textvariable=self.date_var, font=("Segoe UI", 10)).grid(row=6, column=0, sticky="ew", pady=(4, 10))

        ttk.Label(form, text="Recurring Days", style="Field.TLabel").grid(row=7, column=0, sticky="w", pady=(2, 0))
        self.recurrence_label_var = tk.StringVar(value="Does not repeat")
        ttk.Button(
            form,
            textvariable=self.recurrence_label_var,
            style="Secondary.TButton",
            command=self._open_recurrence_picker,
        ).grid(row=8, column=0, sticky="ew", pady=(4, 10))

        ttk.Label(form, text="Color", style="Field.TLabel").grid(row=9, column=0, sticky="w", pady=(2, 0))
        self.color_var = tk.StringVar(value=self.default_color_name)
        ttk.Combobox(
            form,
            textvariable=self.color_var,
            values=list(self.color_options.keys()),
            state="readonly",
        ).grid(row=10, column=0, sticky="ew", pady=(4, 10))

        actions = ttk.Frame(self.left_card, style="Card.TFrame")
        actions.pack(fill="x", pady=(4, 10))
        actions.columnconfigure((0, 1), weight=1)
        actions.rowconfigure((0, 1), weight=1)

        ttk.Button(actions, text="Add Task", style="Primary.TButton", command=self._add_task).grid(
            row=0, column=0, sticky="ew", padx=(0, 8)
        )
        ttk.Button(actions, text="Clear Form", style="Secondary.TButton", command=self._clear_form).grid(
            row=0, column=1, sticky="ew"
        )
        ttk.Button(
            actions,
            text="Save Selected",
            style="Secondary.TButton",
            command=self._save_selected_task,
        ).grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(8, 0))
        ttk.Button(
            actions,
            text="Remove Selected",
            style="Secondary.TButton",
            command=self._remove_selected_task,
        ).grid(row=1, column=1, sticky="ew", pady=(8, 0))

        ttk.Label(self.left_card, text="Today's Tasks", style="Field.TLabel").pack(anchor="w", pady=(10, 6))
        self.task_listbox = tk.Listbox(
            self.left_card,
            font=("Segoe UI", 10),
            bd=0,
            relief="flat",
            highlightthickness=0,
            activestyle="none",
            background=self._get_theme_palette()["list_bg"],
            foreground=self._get_theme_palette()["task_fg"],
            selectbackground=self._get_theme_palette()["list_select_bg"],
            selectforeground=self._get_theme_palette()["list_select_fg"],
        )
        self.task_listbox.pack(fill="both", expand=True)
        self.task_listbox.bind("<<ListboxSelect>>", self._on_task_selected)

    def _build_right_panel(self) -> None:
        top_row = ttk.Frame(self.right_card, style="Card.TFrame")
        top_row.pack(fill="x")

        ttk.Label(top_row, text="Timeline", style="Field.TLabel").pack(side="left")
        self.period_label = ttk.Label(
            top_row,
            text="",
            style="Period.TLabel",
        )
        self.period_label.pack(side="right")

        controls = ttk.Frame(self.right_card, style="Card.TFrame")
        controls.pack(fill="x", pady=(8, 0))
        controls.columnconfigure(3, weight=1)

        ttk.Button(controls, text="<", style="Secondary.TButton", command=lambda: self._shift_period(-1)).grid(
            row=0, column=0, padx=(0, 6), sticky="w"
        )
        ttk.Button(controls, text=">", style="Secondary.TButton", command=lambda: self._shift_period(1)).grid(
            row=0, column=1, padx=(0, 12), sticky="w"
        )
        ttk.Label(controls, text="View", style="Field.TLabel").grid(row=0, column=2, sticky="w", padx=(0, 6))
        self.view_var = tk.StringVar(value=self.current_view)
        ttk.Combobox(
            controls,
            textvariable=self.view_var,
            values=["Day", "Week", "Month", "Year"],
            state="readonly",
            width=10,
        ).grid(row=0, column=3, sticky="w")
        self.view_var.trace_add("write", lambda *_: self._on_view_changed())

        canvas_wrap = ttk.Frame(self.right_card, style="Card.TFrame")
        canvas_wrap.pack(fill="both", expand=True, pady=(10, 0))
        canvas_wrap.rowconfigure(0, weight=1)
        canvas_wrap.columnconfigure(0, weight=1)

        self.timeline_canvas = tk.Canvas(
            canvas_wrap,
            background=self._get_theme_palette()["canvas_bg"],
            highlightthickness=0,
            bd=0,
        )
        self.timeline_canvas.grid(row=0, column=0, sticky="nsew")
        self.timeline_canvas.bind("<Configure>", lambda _: self._draw_timeline())

    def _seed_tasks(self) -> None:
        self.tasks = [
            {
                "title": "Morning Focus",
                "description": "Deep work",
                "date": self.current_date.strftime("%Y-%m-%d"),
                "start": "09:00",
                "end": "11:00",
                "color": self.color_options["Blue"],
                "recurring_days": [],
            },
            {
                "title": "Lunch Break",
                "description": "Recharge",
                "date": self.current_date.strftime("%Y-%m-%d"),
                "start": "12:00",
                "end": "13:00",
                "color": self.color_options["Green"],
                "recurring_days": [],
            },
            {
                "title": "Wrap Up",
                "description": "Review progress",
                "date": self.current_date.strftime("%Y-%m-%d"),
                "start": "17:00",
                "end": "18:00",
                "color": self.color_options["Orange"],
                "recurring_days": [],
            },
        ]

    def _clear_form(self) -> None:
        self.title_var.set("")
        self.desc_var.set("")
        self.start_var.set("09:00")
        self.end_var.set("10:00")
        self.date_var.set(self.current_date.strftime("%Y-%m-%d"))
        self.selected_recurrence_days = []
        self.recurrence_label_var.set("Does not repeat")
        self.color_var.set(self.default_color_name)
        self.selected_task_index = None
        self.hovered_task_index = None
        self.task_listbox.selection_clear(0, tk.END)
        self._draw_timeline()

    def _add_task(self) -> None:
        title = self.title_var.get().strip()
        description = self.desc_var.get().strip() or "No description"
        start = self.start_var.get()
        end = self.end_var.get()
        date_text = self.date_var.get().strip()
        recurring_days = self.selected_recurrence_days.copy()
        color = self.color_options.get(self.color_var.get(), self.color_options[self.default_color_name])

        try:
            datetime.strptime(date_text, "%Y-%m-%d")
        except ValueError:
            return

        if not title:
            return
        if self.time_slots.index(end) <= self.time_slots.index(start):
            return

        self.tasks.append(
            {
                "title": title,
                "description": description,
                "date": date_text,
                "start": start,
                "end": end,
                "color": color,
                "recurring_days": recurring_days,
            }
        )
        self._save_account_data()
        self._render_tasks()
        self._draw_timeline()
        self._clear_form()

    def _render_tasks(self) -> None:
        self.task_listbox.delete(0, tk.END)
        sorted_pairs = sorted(
            enumerate(self.tasks),
            key=lambda pair: pair[1]["start"],
        )
        self.sorted_task_indices = [index for index, _ in sorted_pairs]
        for _, task in sorted_pairs:
            recurrence_text = self._format_recurrence_label(self._get_recurrence_days_from_task(task))
            self.task_listbox.insert(
                tk.END,
                f'{task["date"]} {task["start"]}-{task["end"]}  |  {task["title"]} - {task["description"]}'
                f'{" [" + recurrence_text + "]" if recurrence_text != "Does not repeat" else ""}',
            )

    def _on_task_selected(self, _event: tk.Event) -> None:
        selected = self.task_listbox.curselection()
        if not selected:
            return

        listbox_index = selected[0]
        if listbox_index >= len(self.sorted_task_indices):
            return

        task_index = self.sorted_task_indices[listbox_index]
        self._select_task(task_index, highlight_list=False)

    def _select_task(self, task_index: int, highlight_list: bool = True) -> None:
        if task_index < 0 or task_index >= len(self.tasks):
            return

        self.selected_task_index = task_index
        self.hovered_task_index = None

        task = self.tasks[task_index]
        self.title_var.set(task["title"])
        self.desc_var.set(task["description"])
        self.start_var.set(task["start"])
        self.end_var.set(task["end"])
        self.date_var.set(task.get("date", self.current_date.strftime("%Y-%m-%d")))
        self.selected_recurrence_days = self._get_recurrence_days_from_task(task)
        self.recurrence_label_var.set(self._format_recurrence_label(self.selected_recurrence_days))
        self.color_var.set(self._get_color_name(task.get("color", self.color_options[self.default_color_name])))

        if highlight_list and task_index in self.sorted_task_indices:
            listbox_index = self.sorted_task_indices.index(task_index)
            self.task_listbox.selection_clear(0, tk.END)
            self.task_listbox.selection_set(listbox_index)
            self.task_listbox.activate(listbox_index)
            self.task_listbox.see(listbox_index)

        self._draw_timeline()

    def _save_selected_task(self) -> None:
        if self.selected_task_index is None:
            return

        title = self.title_var.get().strip()
        description = self.desc_var.get().strip() or "No description"
        start = self.start_var.get()
        end = self.end_var.get()
        date_text = self.date_var.get().strip()
        recurring_days = self.selected_recurrence_days.copy()
        color = self.color_options.get(self.color_var.get(), self.color_options[self.default_color_name])

        if not title:
            return
        if self.time_slots.index(end) <= self.time_slots.index(start):
            return
        try:
            datetime.strptime(date_text, "%Y-%m-%d")
        except ValueError:
            return

        self.tasks[self.selected_task_index]["title"] = title
        self.tasks[self.selected_task_index]["description"] = description
        self.tasks[self.selected_task_index]["start"] = start
        self.tasks[self.selected_task_index]["end"] = end
        self.tasks[self.selected_task_index]["date"] = date_text
        self.tasks[self.selected_task_index]["color"] = color
        self.tasks[self.selected_task_index]["recurring_days"] = recurring_days
        self._save_account_data()
        self._render_tasks()
        self._draw_timeline()
        self._select_task(self.selected_task_index)

    def _remove_selected_task(self) -> None:
        if self.selected_task_index is None:
            return

        self.tasks.pop(self.selected_task_index)
        self.selected_task_index = None
        self.hovered_task_index = None
        self._render_tasks()
        self._draw_timeline()
        self._clear_form()
        self._save_account_data()

    def _draw_timeline(self) -> None:
        if self.current_view == "Day":
            self._draw_day_view()
        elif self.current_view == "Week":
            self._draw_week_view()
        elif self.current_view == "Month":
            self._draw_month_view()
        else:
            self._draw_year_view()

    def _draw_day_view(self) -> None:
        palette = self._get_theme_palette()
        canvas = self.timeline_canvas
        canvas.delete("all")
        canvas.configure(background=palette["canvas_bg"])

        width = max(canvas.winfo_width(), 420)
        height = max(canvas.winfo_height(), 400)
        left_gutter = 70
        top = 22
        bottom = height - 20
        line_color = palette["line"]

        start_minutes = self._time_to_minutes(self.time_slots[0])
        end_minutes = self._time_to_minutes(self.time_slots[-1])
        total_minutes = end_minutes - start_minutes
        minute_to_y = (bottom - top) / total_minutes

        for hour in range(7, 23):
            marker = f"{hour:02d}:00"
            marker_minutes = self._time_to_minutes(marker)
            y = top + ((marker_minutes - start_minutes) * minute_to_y)
            canvas.create_line(left_gutter, y, width - 20, y, fill=line_color, width=1)
            canvas.create_text(left_gutter - 10, y, text=marker, fill=palette["muted"], font=("Segoe UI", 9), anchor="e")

        current_date_text = self.current_date.strftime("%Y-%m-%d")
        visible_tasks = [
            (task_index, task)
            for task_index, task in enumerate(self.tasks)
            if self._task_occurs_on_date(task, self.current_date)
        ]

        for task_index, task in visible_tasks:
            start_task_minutes = self._time_to_minutes(task["start"])
            end_task_minutes = self._time_to_minutes(task["end"])
            duration_minutes = end_task_minutes - start_task_minutes
            y1 = top + ((start_task_minutes - start_minutes) * minute_to_y) + 2
            y2 = top + ((end_task_minutes - start_minutes) * minute_to_y) - 2

            if task_index == self.hovered_task_index:
                x_pad = 2
                y_pad = 2
            else:
                x_pad = 0
                y_pad = 0

            base_color = task.get("color", self.color_options[self.default_color_name])
            fill_color = base_color
            outline_color = self._shift_hex_color(base_color, -22)
            if task_index == self.selected_task_index:
                fill_color = self._shift_hex_color(base_color, -12)
                outline_color = self._shift_hex_color(base_color, -42)

            tag = f"task_{task_index}"
            self._create_rounded_rectangle(
                canvas,
                left_gutter + 12 - x_pad,
                y1 - y_pad,
                width - 26 + x_pad,
                y2 + y_pad,
                radius=10,
                fill_color=fill_color,
                outline_color=outline_color,
                line_width=1,
                tags=(tag, "task_block"),
            )
            canvas.create_text(
                left_gutter + 22,
                y1 + ((y2 - y1) * 0.40),
                text=f'{task["title"]} ({task["start"]}-{task["end"]})',
                fill=palette["text_strong"],
                font=("Segoe UI", 10, "bold"),
                anchor="w",
                tags=(tag, "task_block"),
            )
            if duration_minutes > 60:
                canvas.create_text(
                    left_gutter + 22,
                    y1 + ((y2 - y1) * 0.65),
                    text=task["description"],
                    fill=palette["text_body"],
                    font=("Segoe UI", 9),
                    anchor="w",
                    tags=(tag, "task_block"),
                )
            canvas.tag_bind(
                tag,
                "<Enter>",
                lambda _event, idx=task_index: self._on_task_hover(idx),
            )
            canvas.tag_bind(tag, "<Leave>", lambda _event: self._on_task_hover_leave())
            canvas.tag_bind(
                tag,
                "<Button-1>",
                lambda _event, idx=task_index: self._select_task(idx),
            )
        self.period_label.config(text=self.current_date.strftime("%A, %B %d, %Y"))

    def _draw_week_view(self) -> None:
        palette = self._get_theme_palette()
        canvas = self.timeline_canvas
        canvas.delete("all")
        canvas.configure(background=palette["canvas_bg"])
        self.hovered_task_index = None
        week_start = self._get_week_start(self.current_date)
        self.period_label.config(text=f"Week of {week_start.strftime('%b %d, %Y')}")

        width = max(canvas.winfo_width(), 420)
        height = max(canvas.winfo_height(), 400)
        days = [week_start + timedelta(days=offset) for offset in range(7)]
        left_gutter = 64
        right_margin = 18
        header_h = 34
        top = 14
        day_gap = 10
        grid_top = top + header_h
        grid_bottom = height - 16
        available_width = width - left_gutter - right_margin
        col_width = (available_width - (day_gap * 6)) / 7

        start_minutes = self._time_to_minutes(self.time_slots[0])
        end_minutes = self._time_to_minutes(self.time_slots[-1])
        total_minutes = end_minutes - start_minutes
        minute_to_y = (grid_bottom - grid_top) / total_minutes

        for idx, day in enumerate(days):
            x1 = left_gutter + (idx * (col_width + day_gap))
            x2 = x1 + col_width
            day_text = day.strftime("%Y-%m-%d")

            # Day header and subtle column background; gap remains visible between days.
            canvas.create_text(
                x1 + 2,
                top + 2,
                text=day.strftime("%a %d"),
                anchor="nw",
                fill=palette["muted"],
                font=("Segoe UI", 9, "bold"),
            )
            canvas.create_rectangle(
                x1,
                grid_top,
                x2,
                grid_bottom,
                fill=palette["column_bg"],
                outline=palette["column_outline"],
            )

            # Hour lines are drawn within each day column only.
            for hour in range(7, 23):
                marker = f"{hour:02d}:00"
                marker_minutes = self._time_to_minutes(marker)
                y = grid_top + ((marker_minutes - start_minutes) * minute_to_y)
                canvas.create_line(x1, y, x2, y, fill=palette["line"], width=1)
                if idx == 0:
                    canvas.create_text(
                        left_gutter - 8,
                        y,
                        text=marker,
                        anchor="e",
                        fill=palette["muted"],
                        font=("Segoe UI", 8),
                    )

            day_tasks = sorted(
                [task for task in self.tasks if self._task_occurs_on_date(task, day)],
                key=lambda task: task["start"],
            )

            for task in day_tasks:
                task_start_minutes = self._time_to_minutes(task["start"])
                task_end_minutes = self._time_to_minutes(task["end"])
                y1 = grid_top + ((task_start_minutes - start_minutes) * minute_to_y) + 1
                y2 = grid_top + ((task_end_minutes - start_minutes) * minute_to_y) - 1

                # Keep very short tasks readable in week view.
                if (y2 - y1) < 16:
                    y2 = y1 + 16

                base_color = task.get("color", self.color_options[self.default_color_name])
                self._create_rounded_rectangle(
                    canvas,
                    x1 + 2,
                    y1,
                    x2 - 2,
                    min(y2, grid_bottom - 1),
                    radius=7,
                    fill_color=base_color,
                    outline_color=self._shift_hex_color(base_color, -24),
                    line_width=1,
                    tags=("week_block",),
                )
                canvas.create_text(
                    x1 + 7,
                    y1 + 8,
                    text=f'{task["start"]} {task["title"]}',
                    anchor="w",
                    fill=palette["text_strong"],
                    font=("Segoe UI", 8, "bold"),
                )

    def _draw_month_view(self) -> None:
        palette = self._get_theme_palette()
        canvas = self.timeline_canvas
        canvas.delete("all")
        canvas.configure(background=palette["canvas_bg"])
        self.hovered_task_index = None
        self.period_label.config(text=self.current_date.strftime("%B %Y"))

        width = max(canvas.winfo_width(), 420)
        height = max(canvas.winfo_height(), 400)
        year = self.current_date.year
        month = self.current_date.month
        month_cal = calendar.Calendar(firstweekday=self._get_python_first_weekday())
        cal = month_cal.monthdayscalendar(year, month)
        cols = 7
        rows = len(cal)
        cell_w = (width - 30) / cols
        cell_h = (height - 50) / max(rows, 1)
        weekday_short = {
            "Sunday": "Sun",
            "Monday": "Mon",
            "Tuesday": "Tue",
            "Wednesday": "Wed",
            "Thursday": "Thu",
            "Friday": "Fri",
            "Saturday": "Sat",
        }
        start_idx = self.weekday_options.index(self.week_start_day)
        ordered_days = self.weekday_options[start_idx:] + self.weekday_options[:start_idx]
        day_names = [weekday_short[day] for day in ordered_days]

        for col, name in enumerate(day_names):
            x = 18 + (col * cell_w)
            canvas.create_text(x + 2, 16, text=name, anchor="nw", fill=palette["muted"], font=("Segoe UI", 9, "bold"))

        for row, week in enumerate(cal):
            for col, day in enumerate(week):
                x1 = 18 + (col * cell_w)
                y1 = 34 + (row * cell_h)
                x2 = x1 + cell_w - 4
                y2 = y1 + cell_h - 4
                canvas.create_rectangle(x1, y1, x2, y2, outline=palette["month_cell_outline"], fill=palette["month_cell_bg"])
                if day == 0:
                    continue
                day_date = datetime(year, month, day).strftime("%Y-%m-%d")
                day_obj = datetime(year, month, day).date()
                count = sum(1 for task in self.tasks if self._task_occurs_on_date(task, day_obj))
                canvas.create_text(x1 + 6, y1 + 6, text=str(day), anchor="nw", fill=palette["text_strong"], font=("Segoe UI", 9, "bold"))
                if count > 0:
                    canvas.create_text(
                        x1 + 6,
                        y1 + 24,
                        text=f"{count} task{'s' if count != 1 else ''}",
                        anchor="nw",
                        fill=palette["muted"],
                        font=("Segoe UI", 8),
                    )

    def _draw_year_view(self) -> None:
        palette = self._get_theme_palette()
        canvas = self.timeline_canvas
        canvas.delete("all")
        canvas.configure(background=palette["canvas_bg"])
        self.hovered_task_index = None
        self.period_label.config(text=str(self.current_date.year))

        year = self.current_date.year
        width = max(canvas.winfo_width(), 420)
        height = max(canvas.winfo_height(), 400)
        cols = 3
        rows = 4
        cell_w = (width - 30) / cols
        cell_h = (height - 30) / rows

        for month in range(1, 13):
            row = (month - 1) // cols
            col = (month - 1) % cols
            x1 = 18 + (col * cell_w)
            y1 = 18 + (row * cell_h)
            x2 = x1 + cell_w - 6
            y2 = y1 + cell_h - 6

            month_tasks = 0
            month_days = calendar.monthrange(year, month)[1]
            for day in range(1, month_days + 1):
                check_date = datetime(year, month, day).date()
                month_tasks += sum(1 for task in self.tasks if self._task_occurs_on_date(task, check_date))

            canvas.create_rectangle(x1, y1, x2, y2, outline=palette["month_cell_outline"], fill=palette["month_cell_bg"])
            canvas.create_text(
                x1 + 8,
                y1 + 10,
                text=calendar.month_name[month],
                anchor="nw",
                fill=palette["text_strong"],
                font=("Segoe UI", 10, "bold"),
            )
            canvas.create_text(
                x1 + 8,
                y1 + 32,
                text=f"{month_tasks} task{'s' if month_tasks != 1 else ''}",
                anchor="nw",
                fill=palette["muted"],
                font=("Segoe UI", 9),
            )

    def _on_task_hover(self, task_index: int) -> None:
        if self.current_view != "Day":
            return
        if self.hovered_task_index == task_index:
            return
        self.hovered_task_index = task_index
        self._draw_timeline()

    def _on_task_hover_leave(self) -> None:
        if self.current_view != "Day":
            return
        if self.hovered_task_index is None:
            return
        self.hovered_task_index = None
        self._draw_timeline()

    def _on_view_changed(self) -> None:
        self.current_view = self.view_var.get()
        self._draw_timeline()

    def _shift_period(self, direction: int) -> None:
        if self.current_view == "Day":
            self.current_date += timedelta(days=direction)
        elif self.current_view == "Week":
            self.current_date += timedelta(days=7 * direction)
        elif self.current_view == "Month":
            year = self.current_date.year
            month = self.current_date.month + direction
            if month < 1:
                month = 12
                year -= 1
            elif month > 12:
                month = 1
                year += 1
            day = min(self.current_date.day, calendar.monthrange(year, month)[1])
            self.current_date = datetime(year, month, day).date()
        else:
            self.current_date = datetime(
                self.current_date.year + direction,
                self.current_date.month,
                self.current_date.day,
            ).date()

        self.date_var.set(self.current_date.strftime("%Y-%m-%d"))
        self._draw_timeline()

    @staticmethod
    def _create_rounded_rectangle(
        canvas: tk.Canvas,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        radius: float,
        fill_color: str,
        outline_color: str,
        line_width: int,
        tags: tuple[str, ...],
    ) -> int:
        max_radius = max(1, min(radius, abs(x2 - x1) / 2, abs(y2 - y1) / 2))
        points = [
            x1 + max_radius,
            y1,
            x2 - max_radius,
            y1,
            x2,
            y1,
            x2,
            y1 + max_radius,
            x2,
            y2 - max_radius,
            x2,
            y2,
            x2 - max_radius,
            y2,
            x1 + max_radius,
            y2,
            x1,
            y2,
            x1,
            y2 - max_radius,
            x1,
            y1 + max_radius,
            x1,
            y1,
        ]
        return canvas.create_polygon(
            points,
            smooth=True,
            fill=fill_color,
            outline=outline_color,
            width=line_width,
            splinesteps=24,
            tags=tags,
        )

    @staticmethod
    def _shift_hex_color(hex_color: str, amount: int) -> str:
        color = hex_color.lstrip("#")
        if len(color) != 6:
            return "#DDE9FF"

        red = int(color[0:2], 16)
        green = int(color[2:4], 16)
        blue = int(color[4:6], 16)

        red = max(0, min(255, red + amount))
        green = max(0, min(255, green + amount))
        blue = max(0, min(255, blue + amount))

        return f"#{red:02X}{green:02X}{blue:02X}"

    def _get_color_name(self, hex_color: str) -> str:
        for name, value in self.color_options.items():
            if value.lower() == hex_color.lower():
                return name
        return self.default_color_name

    def _open_recurrence_picker(self) -> None:
        picker = tk.Toplevel(self)
        picker.title("Recurring Days")
        picker.configure(bg="#FFFFFF")
        picker.transient(self)
        picker.grab_set()
        picker.resizable(False, False)

        frame = ttk.Frame(picker, padding=12, style="Card.TFrame")
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Select weekdays", style="Field.TLabel").pack(anchor="w")

        list_wrap = ttk.Frame(frame, style="Card.TFrame")
        list_wrap.pack(fill="both", expand=True, pady=(8, 10))

        day_listbox = tk.Listbox(
            list_wrap,
            selectmode=tk.MULTIPLE,
            exportselection=False,
            height=7,
            font=("Segoe UI", 10),
            bd=0,
            highlightthickness=0,
            activestyle="none",
            background="#F9FBFE",
            selectbackground="#D7E5FF",
        )
        day_listbox.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(list_wrap, orient="vertical", command=day_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        day_listbox.config(yscrollcommand=scrollbar.set)

        for day in self.weekday_options:
            day_listbox.insert(tk.END, day)
        for idx, day in enumerate(self.weekday_options):
            if day in self.selected_recurrence_days:
                day_listbox.selection_set(idx)

        def save_days() -> None:
            self.selected_recurrence_days = [self.weekday_options[i] for i in day_listbox.curselection()]
            self.recurrence_label_var.set(self._format_recurrence_label(self.selected_recurrence_days))
            picker.destroy()

        buttons = ttk.Frame(frame, style="Card.TFrame")
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Save", style="Primary.TButton", command=save_days).pack(side="left", fill="x", expand=True)
        ttk.Button(buttons, text="Cancel", style="Secondary.TButton", command=picker.destroy).pack(side="left", fill="x", expand=True, padx=(8, 0))

    def _accounts_dir(self) -> Path:
        base_dir = Path(__file__).resolve().parent
        target = base_dir / "data" / "accounts"
        target.mkdir(parents=True, exist_ok=True)
        return target

    @staticmethod
    def _sanitize_account_name(raw_name: str) -> str:
        cleaned = "".join(char if char.isalnum() or char in ("-", "_") else "_" for char in raw_name)
        cleaned = cleaned.strip("_")
        return cleaned[:40]

    def _account_file_path(self, account_name: str) -> Path:
        return self._accounts_dir() / f"{self._sanitize_account_name(account_name)}.json"

    def _list_accounts(self) -> list[str]:
        names: list[str] = []
        for path in self._accounts_dir().glob("*.json"):
            names.append(path.stem)
        if "default" not in names:
            names.append("default")
        return sorted(names)

    def _create_account_if_missing(self, account_name: str) -> None:
        safe_name = self._sanitize_account_name(account_name)
        if not safe_name:
            return
        target = self._account_file_path(safe_name)
        if target.exists():
            return
        payload = {
            "account": safe_name,
            "preferences": {
                "theme": self.current_theme,
                "week_start_day": self.week_start_day,
            },
            "tasks": [],
        }
        target.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _switch_account(self, account_name: str) -> None:
        safe_name = self._sanitize_account_name(account_name)
        if not safe_name:
            return
        self.current_account = safe_name
        loaded = self._load_account_data(safe_name)
        if not loaded:
            self.tasks = []
            self._seed_tasks()
            self._save_account_data()
        self._apply_theme()
        self.selected_task_index = None
        self.hovered_task_index = None
        self._clear_form()
        self._render_tasks()
        self._draw_timeline()
        self._update_account_header()

    def _load_account_data(self, account_name: str) -> bool:
        file_path = self._account_file_path(account_name)
        if not file_path.exists():
            return False
        try:
            payload = json.loads(file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return False

        tasks_value = payload.get("tasks", [])
        if isinstance(tasks_value, list):
            self.tasks = [task for task in tasks_value if isinstance(task, dict)]
        else:
            self.tasks = []

        prefs = payload.get("preferences", {})
        if isinstance(prefs, dict):
            loaded_theme = prefs.get("theme", self.current_theme)
            loaded_week_start = prefs.get("week_start_day", self.week_start_day)
            if loaded_theme in ("Light", "Dark"):
                self.current_theme = loaded_theme
            if loaded_week_start in self.weekday_options:
                self.week_start_day = loaded_week_start

        return True

    def _save_account_data(self) -> None:
        payload = {
            "account": self.current_account,
            "preferences": {
                "theme": self.current_theme,
                "week_start_day": self.week_start_day,
            },
            "tasks": self.tasks,
        }
        try:
            self._account_file_path(self.current_account).write_text(
                json.dumps(payload, indent=2),
                encoding="utf-8",
            )
        except OSError:
            return

    def _update_account_header(self) -> None:
        if hasattr(self, "account_button_text"):
            self.account_button_text.set(f"Account: {self.current_account}")

    @staticmethod
    def _parse_task_date(task: dict[str, object]) -> datetime.date | None:
        date_text = task.get("date", "")
        if not isinstance(date_text, str):
            return None
        try:
            return datetime.strptime(date_text, "%Y-%m-%d").date()
        except ValueError:
            return None

    def _task_occurs_on_date(self, task: dict[str, object], target_date: datetime.date) -> bool:
        start_date = self._parse_task_date(task)
        if start_date is None:
            return False

        recurring_days = self._get_recurrence_days_from_task(task)
        if recurring_days:
            return target_date >= start_date and target_date.strftime("%A") in recurring_days
        return target_date == start_date

    def _get_week_start(self, date_value: datetime.date) -> datetime.date:
        day_index = (date_value.weekday() + 1) % 7
        start_index = self.weekday_options.index(self.week_start_day)
        days_back = (day_index - start_index) % 7
        return date_value - timedelta(days=days_back)

    def _get_python_first_weekday(self) -> int:
        start_index = self.weekday_options.index(self.week_start_day)
        return (start_index + 6) % 7

    def _get_recurrence_days_from_task(self, task: dict[str, object]) -> list[str]:
        value = task.get("recurring_days")
        if isinstance(value, list):
            valid_days = [day for day in value if isinstance(day, str) and day in self.weekday_options]
            return valid_days

        # Backwards compatibility for older saved data.
        if task.get("recurring_daily", False):
            return self.weekday_options.copy()
        return []

    def _format_recurrence_label(self, recurring_days: list[str]) -> str:
        if not recurring_days:
            return "Does not repeat"
        if len(recurring_days) == 7:
            return "Every day"
        if len(recurring_days) <= 2:
            return ", ".join(recurring_days)
        return f"{', '.join(recurring_days[:2])} +{len(recurring_days) - 2} more"


if __name__ == "__main__":
    app = SchedulerApp()
    app.mainloop()
