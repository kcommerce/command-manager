#!/usr/bin/env python3
"""
Command Manager - A GUI application to manage and run terminal commands.
Requires: tkinter (built-in), subprocess, json
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import subprocess
import threading
import json
import os
import sys
import io
from datetime import datetime

# Force UTF-8 output on Windows (cp1252 cannot encode unicode symbols)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

COMMANDS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "commands.json")

DEFAULT_COMMANDS = [
    {"name": "List Files",  "command": "ls -la",  "description": "List all files in current directory"},
    {"name": "System Info", "command": "uname -a", "description": "Show system information"},
    {"name": "Disk Usage",  "command": "df -h",    "description": "Show disk usage"},
    {"name": "Current Dir", "command": "pwd",       "description": "Print working directory"},
    {"name": "Date & Time", "command": "date",      "description": "Show current date and time"},
]

# ─── Themes ──────────────────────────────────────────────────────────────────

THEMES = {
    "Cyber Night": {
        "bg_app": "#0d0d1a", "bg_header": "#070714", "bg_left": "#111128",
        "bg_listbox": "#0d0d1a", "bg_right": "#0a0a0f", "bg_terminal": "#050510",
        "bg_entry": "#111128", "bg_divider": "#1a1a3a",
        "fg_title": "#00d4ff", "fg_label": "#606080", "fg_detail": "#505070",
        "fg_list": "#c0c8e0", "fg_select_bg": "#00d4ff", "fg_select_fg": "#0d0d1a",
        "fg_terminal": "#c0c8e0", "fg_status": "#606080",
        "fg_prompt": "#00d4ff", "fg_cmd": "#00ff9f", "fg_stdout": "#c0c8e0",
        "fg_stderr": "#ff6b8a", "fg_info": "#606080", "fg_success": "#00ff9f",
        "fg_error": "#ff4f7b", "fg_timestamp": "#404060",
        "fg_entry_text": "#00ff9f", "fg_entry_insert": "#00d4ff",
        "hl_entry": "#2a2a4a", "hl_focus": "#00d4ff",
        "btn_add":    ("#00ff9f", "#0d1a0d"), "btn_edit":   ("#00d4ff", "#0d1a1a"),
        "btn_remove": ("#ff4f7b", "#1a0d10"), "btn_run":    ("#ffd700", "#1a1800"),
        "btn_kill":   ("#ff4f7b", "#1a0d10"), "btn_save":   ("#a78bfa", "#100d1a"),
        "btn_clear":  ("#404060", "#0d0d1a"), "btn_generic":("#2a2a4a", "#c0c8e0"),
        "font_mono": "Courier New",
    },
    "Solarized Dark": {
        "bg_app": "#002b36", "bg_header": "#001e26", "bg_left": "#073642",
        "bg_listbox": "#002b36", "bg_right": "#001e26", "bg_terminal": "#00141a",
        "bg_entry": "#073642", "bg_divider": "#0d4d5e",
        "fg_title": "#2aa198", "fg_label": "#586e75", "fg_detail": "#4a6068",
        "fg_list": "#839496", "fg_select_bg": "#2aa198", "fg_select_fg": "#002b36",
        "fg_terminal": "#839496", "fg_status": "#586e75",
        "fg_prompt": "#268bd2", "fg_cmd": "#859900", "fg_stdout": "#839496",
        "fg_stderr": "#dc322f", "fg_info": "#586e75", "fg_success": "#859900",
        "fg_error": "#dc322f", "fg_timestamp": "#3a5560",
        "fg_entry_text": "#859900", "fg_entry_insert": "#2aa198",
        "hl_entry": "#0d4d5e", "hl_focus": "#2aa198",
        "btn_add":    ("#859900", "#001a00"), "btn_edit":   ("#2aa198", "#001a18"),
        "btn_remove": ("#dc322f", "#1a0000"), "btn_run":    ("#b58900", "#1a1200"),
        "btn_kill":   ("#dc322f", "#1a0000"), "btn_save":   ("#6c71c4", "#0a0a1a"),
        "btn_clear":  ("#586e75", "#001e26"), "btn_generic":("#0d4d5e", "#839496"),
        "font_mono": "Courier New",
    },
    "Light Mint": {
        "bg_app": "#f0f4f0", "bg_header": "#d8ede0", "bg_left": "#e4f0e8",
        "bg_listbox": "#f5faf6", "bg_right": "#f0f4f0", "bg_terminal": "#ffffff",
        "bg_entry": "#e8f4ec", "bg_divider": "#b8d8c0",
        "fg_title": "#1a7a4a", "fg_label": "#5a7a62", "fg_detail": "#6a8a72",
        "fg_list": "#2a4a32", "fg_select_bg": "#1a7a4a", "fg_select_fg": "#ffffff",
        "fg_terminal": "#2a3a2e", "fg_status": "#5a7a62",
        "fg_prompt": "#1a7a4a", "fg_cmd": "#0a5a8a", "fg_stdout": "#2a3a2e",
        "fg_stderr": "#c0392b", "fg_info": "#7a9a82", "fg_success": "#1a7a4a",
        "fg_error": "#c0392b", "fg_timestamp": "#9ab8a0",
        "fg_entry_text": "#0a5a8a", "fg_entry_insert": "#1a7a4a",
        "hl_entry": "#b8d8c0", "hl_focus": "#1a7a4a",
        "btn_add":    ("#1a7a4a", "#e0f4e8"), "btn_edit":   ("#0a5a8a", "#e0eef8"),
        "btn_remove": ("#c0392b", "#fde8e8"), "btn_run":    ("#8a6a00", "#faf0d0"),
        "btn_kill":   ("#c0392b", "#fde8e8"), "btn_save":   ("#6a3aaa", "#f0e8f8"),
        "btn_clear":  ("#5a7a62", "#e4f0e8"), "btn_generic":("#b8d8c0", "#2a4a32"),
        "font_mono": "Courier New",
    },
    "Monokai": {
        "bg_app": "#272822", "bg_header": "#1a1a16", "bg_left": "#2d2e27",
        "bg_listbox": "#272822", "bg_right": "#1e1f1a", "bg_terminal": "#1a1b16",
        "bg_entry": "#2d2e27", "bg_divider": "#3a3b34",
        "fg_title": "#66d9e8", "fg_label": "#75715e", "fg_detail": "#5a5a4e",
        "fg_list": "#f8f8f2", "fg_select_bg": "#66d9e8", "fg_select_fg": "#272822",
        "fg_terminal": "#f8f8f2", "fg_status": "#75715e",
        "fg_prompt": "#66d9e8", "fg_cmd": "#a6e22e", "fg_stdout": "#f8f8f2",
        "fg_stderr": "#f92672", "fg_info": "#75715e", "fg_success": "#a6e22e",
        "fg_error": "#f92672", "fg_timestamp": "#49483e",
        "fg_entry_text": "#a6e22e", "fg_entry_insert": "#66d9e8",
        "hl_entry": "#3a3b34", "hl_focus": "#66d9e8",
        "btn_add":    ("#a6e22e", "#1a2600"), "btn_edit":   ("#66d9e8", "#001a1e"),
        "btn_remove": ("#f92672", "#1e0010"), "btn_run":    ("#e6db74", "#1e1a00"),
        "btn_kill":   ("#f92672", "#1e0010"), "btn_save":   ("#ae81ff", "#120010"),
        "btn_clear":  ("#49483e", "#1a1a16"), "btn_generic":("#3a3b34", "#f8f8f2"),
        "font_mono": "Courier New",
    },
    "Nord": {
        "bg_app": "#2e3440", "bg_header": "#242933", "bg_left": "#3b4252",
        "bg_listbox": "#2e3440", "bg_right": "#242933", "bg_terminal": "#1e2330",
        "bg_entry": "#3b4252", "bg_divider": "#434c5e",
        "fg_title": "#88c0d0", "fg_label": "#616e88", "fg_detail": "#4c566a",
        "fg_list": "#d8dee9", "fg_select_bg": "#88c0d0", "fg_select_fg": "#2e3440",
        "fg_terminal": "#d8dee9", "fg_status": "#616e88",
        "fg_prompt": "#88c0d0", "fg_cmd": "#a3be8c", "fg_stdout": "#d8dee9",
        "fg_stderr": "#bf616a", "fg_info": "#616e88", "fg_success": "#a3be8c",
        "fg_error": "#bf616a", "fg_timestamp": "#3b4252",
        "fg_entry_text": "#a3be8c", "fg_entry_insert": "#88c0d0",
        "hl_entry": "#434c5e", "hl_focus": "#88c0d0",
        "btn_add":    ("#a3be8c", "#1e2a1a"), "btn_edit":   ("#88c0d0", "#1a2a30"),
        "btn_remove": ("#bf616a", "#2a1618"), "btn_run":    ("#ebcb8b", "#2a2414"),
        "btn_kill":   ("#bf616a", "#2a1618"), "btn_save":   ("#b48ead", "#221a24"),
        "btn_clear":  ("#4c566a", "#242933"), "btn_generic":("#434c5e", "#d8dee9"),
        "font_mono": "Courier New",
    },
}

THEME_NAMES = list(THEMES.keys())


# ─── Data Layer ──────────────────────────────────────────────────────────────

def load_commands():
    if os.path.exists(COMMANDS_FILE):
        try:
            with open(COMMANDS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    save_commands(DEFAULT_COMMANDS)
    return list(DEFAULT_COMMANDS)


def save_commands(commands):
    with open(COMMANDS_FILE, "w") as f:
        json.dump(commands, f, indent=2)


# ─── Add/Edit Dialog ─────────────────────────────────────────────────────────

class CommandDialog(tk.Toplevel):
    """Modal dialog for adding/editing a command — theme-aware."""

    def __init__(self, parent, theme, title, name="", command="", description=""):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.result = None
        t = theme
        self.configure(bg=t["bg_left"])
        self.grab_set()

        pad = dict(padx=12, pady=6)
        font = (t["font_mono"], 10)
        font_e = (t["font_mono"], 11)

        rows = [
            ("Name",        "name_var",  name,        t["fg_list"]),
            ("Command",     "cmd_var",   command,     t["fg_cmd"]),
            ("Description", "desc_var",  description, t["fg_list"]),
        ]
        for i, (lbl_text, attr, val, fg) in enumerate(rows):
            tk.Label(self, text=lbl_text, bg=t["bg_left"], fg=t["fg_label"],
                     font=font).grid(row=i, column=0, sticky="w", **pad)
            var = tk.StringVar(value=val)
            setattr(self, attr, var)
            tk.Entry(self, textvariable=var, width=38,
                     bg=t["bg_listbox"], fg=fg,
                     insertbackground=t["fg_entry_insert"],
                     relief="flat", font=font_e,
                     highlightthickness=1,
                     highlightbackground=t["hl_entry"],
                     highlightcolor=t["hl_focus"]).grid(row=i, column=1, **pad)

        btn_frame = tk.Frame(self, bg=t["bg_left"])
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)

        def on_ok():
            n = self.name_var.get().strip()
            c = self.cmd_var.get().strip()
            if not n or not c:
                messagebox.showwarning("Missing Fields", "Name and Command are required.", parent=self)
                return
            self.result = {"name": n, "command": c, "description": self.desc_var.get().strip()}
            self.destroy()

        acc_bg, acc_fg = t["btn_edit"]
        tk.Button(btn_frame, text="  Save  ", command=on_ok,
                  bg=acc_bg, fg=acc_fg, activebackground=acc_bg,
                  relief="flat", font=(t["font_mono"], 10, "bold"),
                  cursor="hand2", padx=8).pack(side="left", padx=6)

        g_bg, g_fg = t["btn_generic"]
        tk.Button(btn_frame, text=" Cancel ", command=self.destroy,
                  bg=g_bg, fg=g_fg, activebackground=g_bg,
                  relief="flat", font=(t["font_mono"], 10),
                  cursor="hand2", padx=8).pack(side="left", padx=6)

        self.bind("<Return>", lambda e: on_ok())
        self.bind("<Escape>", lambda e: self.destroy())
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width()  - self.winfo_width())  // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")


# ─── Main Application ─────────────────────────────────────────────────────────

class CommandManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Command Manager")
        self.geometry("1160x720")
        self.minsize(860, 520)

        self.commands       = load_commands()
        self.current_process = None
        self.running        = False
        self.cwd            = os.path.expanduser("~")
        self.theme_name     = tk.StringVar(value=THEME_NAMES[0])
        self.theme          = THEMES[THEME_NAMES[0]]

        self._build_ui()
        self._apply_theme()
        self._refresh_list()

    # ── Theme ─────────────────────────────────────────────────────────────

    def _t(self, key):
        return self.theme[key]

    def _switch_theme(self, name):
        self.theme = THEMES[name]
        self._apply_theme()

    def _apply_theme(self):
        t = self.theme
        self.configure(bg=t["bg_app"])
        fm = t["font_mono"]

        self.w_header.configure(bg=t["bg_header"])
        self.w_title_lbl.configure(bg=t["bg_header"], fg=t["fg_title"], font=(fm, 14, "bold"))
        self.w_cwd_frame.configure(bg=t["bg_header"])
        self.w_cwd_lbl.configure(bg=t["bg_header"], fg=t["fg_label"], font=(fm, 8))
        self.w_cwd_val.configure(bg=t["bg_header"], fg=t["fg_prompt"], font=(fm, 8))
        self.w_cwd_btn.configure(bg=t["fg_title"], fg=t["bg_app"],
                                 activebackground=t["fg_title"], font=(fm, 8, "bold"))
        self.w_theme_frame.configure(bg=t["bg_header"])
        self.w_theme_lbl.configure(bg=t["bg_header"], fg=t["fg_label"], font=(fm, 8))
        self.w_theme_menu.configure(bg=t["bg_left"], fg=t["fg_list"],
                                    activebackground=t["fg_select_bg"],
                                    activeforeground=t["fg_select_fg"],
                                    highlightthickness=0, font=(fm, 8))
        # Left
        self.w_body.configure(bg=t["bg_app"])
        self.w_left.configure(bg=t["bg_left"])
        self.w_cmd_lbl.configure(bg=t["bg_left"], fg=t["fg_label"], font=(fm, 9, "bold"))
        self.w_list_frame.configure(bg=t["bg_left"])
        self.w_scrollbar.configure(bg=t["bg_left"], troughcolor=t["bg_app"])
        self.w_listbox.configure(bg=t["bg_listbox"], fg=t["fg_list"],
                                 selectbackground=t["fg_select_bg"],
                                 selectforeground=t["fg_select_fg"],
                                 font=(fm, 11))
        self.w_detail_lbl.configure(bg=t["bg_left"], fg=t["fg_detail"], font=(fm, 8))
        self.w_btn_row1.configure(bg=t["bg_left"])
        self.w_btn_row2.configure(bg=t["bg_left"])
        for btn, key in [
            (self.w_btn_add, "btn_add"), (self.w_btn_edit, "btn_edit"),
            (self.w_btn_remove, "btn_remove"), (self.w_btn_run_left, "btn_run"),
        ]:
            bg, fg = t[key]
            btn.configure(bg=bg, fg=fg, activebackground=bg, activeforeground=fg, font=(fm, 9, "bold"))
        # Divider
        self.w_divider.configure(bg=t["bg_divider"])
        # Right
        self.w_right.configure(bg=t["bg_right"])
        self.w_term_header.configure(bg=t["bg_header"])
        self.w_term_lbl.configure(bg=t["bg_header"], fg=t["fg_success"], font=(fm, 9, "bold"))
        self.w_status_lbl.configure(bg=t["bg_header"], fg=t["fg_status"], font=(fm, 8))
        for btn, key in [
            (self.w_btn_kill, "btn_kill"), (self.w_btn_save, "btn_save"),
            (self.w_btn_clear, "btn_clear"),
        ]:
            bg, fg = t[key]
            btn.configure(bg=bg, fg=fg, activebackground=bg, activeforeground=fg, font=(fm, 9, "bold"))
        self.w_cwd_bar.configure(bg=t["bg_right"])
        self.w_cwd_prefix.configure(bg=t["bg_right"], fg=t["fg_label"], font=(fm, 8))
        self.w_cwd_path_lbl.configure(bg=t["bg_right"], fg=t["fg_prompt"], font=(fm, 8))
        self.w_entry_frame.configure(bg=t["bg_right"])
        self.w_dollar_lbl.configure(bg=t["bg_right"], fg=t["fg_cmd"], font=(fm, 12, "bold"))
        self.cmd_entry.configure(bg=t["bg_entry"], fg=t["fg_entry_text"],
                                 insertbackground=t["fg_entry_insert"],
                                 font=(fm, 11),
                                 highlightbackground=t["hl_entry"],
                                 highlightcolor=t["hl_focus"])
        bg, fg = t["btn_run"]
        self.w_btn_run_entry.configure(bg=bg, fg=fg, activebackground=bg,
                                       activeforeground=fg, font=(fm, 9, "bold"))
        self.w_term_frame.configure(bg=t["bg_right"])
        self.w_t_scroll.configure(bg=t["bg_left"], troughcolor=t["bg_app"])
        self.terminal.configure(bg=t["bg_terminal"], fg=t["fg_terminal"], font=(fm, 10))
        self.terminal.tag_config("prompt",    foreground=t["fg_prompt"])
        self.terminal.tag_config("cmd",       foreground=t["fg_cmd"])
        self.terminal.tag_config("stdout",    foreground=t["fg_stdout"])
        self.terminal.tag_config("stderr",    foreground=t["fg_stderr"])
        self.terminal.tag_config("info",      foreground=t["fg_info"])
        self.terminal.tag_config("success",   foreground=t["fg_success"])
        self.terminal.tag_config("error",     foreground=t["fg_error"])
        self.terminal.tag_config("timestamp", foreground=t["fg_timestamp"])

    # ── UI Construction ───────────────────────────────────────────────────

    def _build_ui(self):
        t = self.theme
        fm = t["font_mono"]

        # Header
        self.w_header = tk.Frame(self, bg=t["bg_header"], height=52)
        self.w_header.pack(fill="x")
        self.w_header.pack_propagate(False)

        self.w_title_lbl = tk.Label(self.w_header, text="COMMAND MANAGER",
                                    bg=t["bg_header"], fg=t["fg_title"],
                                    font=(fm, 14, "bold"))
        self.w_title_lbl.pack(side="left", padx=18, pady=14)

        # Theme selector
        self.w_theme_frame = tk.Frame(self.w_header, bg=t["bg_header"])
        self.w_theme_frame.pack(side="right", padx=12)
        self.w_theme_lbl = tk.Label(self.w_theme_frame, text="Theme:",
                                    bg=t["bg_header"], fg=t["fg_label"], font=(fm, 8))
        self.w_theme_lbl.pack(side="left", padx=(0, 4))
        self.w_theme_menu = tk.OptionMenu(self.w_theme_frame, self.theme_name,
                                          *THEME_NAMES, command=self._switch_theme)
        self.w_theme_menu.configure(relief="flat", borderwidth=0,
                                    padx=6, pady=2, cursor="hand2")
        self.w_theme_menu.pack(side="left")

        # CWD picker
        self.w_cwd_frame = tk.Frame(self.w_header, bg=t["bg_header"])
        self.w_cwd_frame.pack(side="right", padx=12)
        self.w_cwd_lbl = tk.Label(self.w_cwd_frame, text="cwd:",
                                  bg=t["bg_header"], fg=t["fg_label"], font=(fm, 8))
        self.w_cwd_lbl.pack(side="left")
        self.cwd_display_var = tk.StringVar(value=self._short_path(self.cwd))
        self.w_cwd_val = tk.Label(self.w_cwd_frame, textvariable=self.cwd_display_var,
                                  bg=t["bg_header"], fg=t["fg_prompt"], font=(fm, 8),
                                  cursor="hand2")
        self.w_cwd_val.pack(side="left", padx=4)
        self.w_cwd_val.bind("<Button-1>", lambda e: self._change_cwd())
        self.w_cwd_btn = tk.Button(self.w_cwd_frame, text="Browse",
                                   command=self._change_cwd,
                                   bg=t["fg_title"], fg=t["bg_app"],
                                   activebackground=t["fg_title"],
                                   relief="flat", cursor="hand2",
                                   font=(fm, 8, "bold"), padx=6, pady=1)
        self.w_cwd_btn.pack(side="left", padx=(2, 0))

        # Body
        self.w_body = tk.Frame(self, bg=t["bg_app"])
        self.w_body.pack(fill="both", expand=True)

        # Left pane
        self.w_left = tk.Frame(self.w_body, bg=t["bg_left"], width=280)
        self.w_left.pack(side="left", fill="y")
        self.w_left.pack_propagate(False)

        self.w_cmd_lbl = tk.Label(self.w_left, text="COMMANDS",
                                  bg=t["bg_left"], fg=t["fg_label"],
                                  font=(fm, 9, "bold"))
        self.w_cmd_lbl.pack(anchor="w", padx=14, pady=(14, 4))

        self.w_list_frame = tk.Frame(self.w_left, bg=t["bg_left"])
        self.w_list_frame.pack(fill="both", expand=True, padx=8, pady=4)

        self.w_scrollbar = tk.Scrollbar(self.w_list_frame, orient="vertical",
                                        bg=t["bg_left"], troughcolor=t["bg_app"],
                                        relief="flat", width=8)
        self.w_scrollbar.pack(side="right", fill="y")

        self.w_listbox = tk.Listbox(
            self.w_list_frame,
            yscrollcommand=self.w_scrollbar.set,
            bg=t["bg_listbox"], fg=t["fg_list"],
            selectbackground=t["fg_select_bg"],
            selectforeground=t["fg_select_fg"],
            font=(fm, 11), relief="flat", borderwidth=0,
            activestyle="none", highlightthickness=0,
        )
        self.w_listbox.pack(side="left", fill="both", expand=True)
        self.w_scrollbar.config(command=self.w_listbox.yview)
        self.w_listbox.bind("<<ListboxSelect>>", self._on_select)
        self.w_listbox.bind("<Double-Button-1>", lambda e: self._run_selected())

        self.detail_var = tk.StringVar(value="")
        self.w_detail_lbl = tk.Label(self.w_left, textvariable=self.detail_var,
                                     bg=t["bg_left"], fg=t["fg_detail"],
                                     font=(fm, 8), wraplength=250,
                                     justify="left", anchor="w")
        self.w_detail_lbl.pack(fill="x", padx=14, pady=(0, 6))

        self.w_btn_row1 = tk.Frame(self.w_left, bg=t["bg_left"])
        self.w_btn_row1.pack(fill="x", padx=8, pady=2)

        add_bg, add_fg   = t["btn_add"]
        edit_bg, edit_fg = t["btn_edit"]
        self.w_btn_add  = tk.Button(self.w_btn_row1, text="+ Add",
                                    command=self._add_command,
                                    bg=add_bg, fg=add_fg, activebackground=add_bg,
                                    relief="flat", font=(fm, 9, "bold"), cursor="hand2", padx=6)
        self.w_btn_edit = tk.Button(self.w_btn_row1, text="* Edit",
                                    command=self._edit_command,
                                    bg=edit_bg, fg=edit_fg, activebackground=edit_bg,
                                    relief="flat", font=(fm, 9, "bold"), cursor="hand2", padx=6)
        self.w_btn_add.pack(side="left", fill="x", expand=True, padx=2)
        self.w_btn_edit.pack(side="left", fill="x", expand=True, padx=2)

        self.w_btn_row2 = tk.Frame(self.w_left, bg=t["bg_left"])
        self.w_btn_row2.pack(fill="x", padx=8, pady=(2, 8))

        rem_bg, rem_fg = t["btn_remove"]
        run_bg, run_fg = t["btn_run"]
        self.w_btn_remove = tk.Button(self.w_btn_row2, text="x Remove",
                                      command=self._remove_command,
                                      bg=rem_bg, fg=rem_fg, activebackground=rem_bg,
                                      relief="flat", font=(fm, 9, "bold"), cursor="hand2", padx=6)
        self.w_btn_run_left = tk.Button(self.w_btn_row2, text="> Run",
                                        command=self._run_selected,
                                        bg=run_bg, fg=run_fg, activebackground=run_bg,
                                        relief="flat", font=(fm, 9, "bold"), cursor="hand2", padx=6)
        self.w_btn_remove.pack(side="left", fill="x", expand=True, padx=2)
        self.w_btn_run_left.pack(side="left", fill="x", expand=True, padx=2)

        # Divider
        self.w_divider = tk.Frame(self.w_body, bg=t["bg_divider"], width=1)
        self.w_divider.pack(side="left", fill="y")

        # Right pane
        self.w_right = tk.Frame(self.w_body, bg=t["bg_right"])
        self.w_right.pack(side="left", fill="both", expand=True)

        # Terminal top bar
        self.w_term_header = tk.Frame(self.w_right, bg=t["bg_header"], height=36)
        self.w_term_header.pack(fill="x")
        self.w_term_header.pack_propagate(False)

        self.w_term_lbl = tk.Label(self.w_term_header, text="TERMINAL",
                                   bg=t["bg_header"], fg=t["fg_success"],
                                   font=(fm, 9, "bold"))
        self.w_term_lbl.pack(side="left", padx=14, pady=8)

        self.status_var = tk.StringVar(value="ready")
        self.w_status_lbl = tk.Label(self.w_term_header, textvariable=self.status_var,
                                     bg=t["bg_header"], fg=t["fg_status"], font=(fm, 8))
        self.w_status_lbl.pack(side="right", padx=14)

        kill_bg, kill_fg   = t["btn_kill"]
        save_bg, save_fg   = t["btn_save"]
        clear_bg, clear_fg = t["btn_clear"]
        self.w_btn_kill  = tk.Button(self.w_term_header, text="Kill",
                                     command=self._kill_process,
                                     bg=kill_bg, fg=kill_fg, activebackground=kill_bg,
                                     relief="flat", font=(fm, 9, "bold"), cursor="hand2",
                                     padx=6, pady=2)
        self.w_btn_save  = tk.Button(self.w_term_header, text="Save",
                                     command=self._save_output,
                                     bg=save_bg, fg=save_fg, activebackground=save_bg,
                                     relief="flat", font=(fm, 9, "bold"), cursor="hand2",
                                     padx=6, pady=2)
        self.w_btn_clear = tk.Button(self.w_term_header, text="Clear",
                                     command=self._clear_terminal,
                                     bg=clear_bg, fg=clear_fg, activebackground=clear_bg,
                                     relief="flat", font=(fm, 9, "bold"), cursor="hand2",
                                     padx=6, pady=2)
        self.w_btn_kill.pack(side="right",  padx=4, pady=4)
        self.w_btn_save.pack(side="right",  padx=4, pady=4)
        self.w_btn_clear.pack(side="right", padx=4, pady=4)

        # CWD status bar (below terminal header)
        self.w_cwd_bar = tk.Frame(self.w_right, bg=t["bg_right"])
        self.w_cwd_bar.pack(fill="x", padx=10, pady=(6, 0))

        self.w_cwd_prefix = tk.Label(self.w_cwd_bar, text="dir:",
                                     bg=t["bg_right"], fg=t["fg_label"], font=(fm, 8))
        self.w_cwd_prefix.pack(side="left")

        self.cwd_path_var = tk.StringVar(value=self.cwd)
        self.w_cwd_path_lbl = tk.Label(self.w_cwd_bar, textvariable=self.cwd_path_var,
                                       bg=t["bg_right"], fg=t["fg_prompt"], font=(fm, 8))
        self.w_cwd_path_lbl.pack(side="left", padx=4)

        # Command entry bar
        self.w_entry_frame = tk.Frame(self.w_right, bg=t["bg_right"])
        self.w_entry_frame.pack(fill="x", padx=10, pady=(4, 4))

        self.w_dollar_lbl = tk.Label(self.w_entry_frame, text="$",
                                     bg=t["bg_right"], fg=t["fg_cmd"],
                                     font=(fm, 12, "bold"))
        self.w_dollar_lbl.pack(side="left", padx=(4, 6))

        self.cmd_entry = tk.Entry(
            self.w_entry_frame,
            bg=t["bg_entry"], fg=t["fg_entry_text"],
            insertbackground=t["fg_entry_insert"],
            relief="flat", font=(fm, 11),
            highlightthickness=1,
            highlightbackground=t["hl_entry"],
            highlightcolor=t["hl_focus"],
        )
        self.cmd_entry.pack(side="left", fill="x", expand=True, ipady=5)
        self.cmd_entry.bind("<Return>", lambda e: self._run_entry())

        self.w_btn_run_entry = tk.Button(self.w_entry_frame, text="> Run",
                                         command=self._run_entry,
                                         bg=run_bg, fg=run_fg, activebackground=run_bg,
                                         relief="flat", font=(fm, 9, "bold"),
                                         cursor="hand2", padx=6, pady=2)
        self.w_btn_run_entry.pack(side="left", padx=(6, 0))

        # Terminal text area
        self.w_term_frame = tk.Frame(self.w_right, bg=t["bg_right"])
        self.w_term_frame.pack(fill="both", expand=True, padx=10, pady=(4, 10))

        self.w_t_scroll = tk.Scrollbar(self.w_term_frame, orient="vertical",
                                       bg=t["bg_left"], troughcolor=t["bg_app"],
                                       relief="flat", width=8)
        self.w_t_scroll.pack(side="right", fill="y")

        self.terminal = tk.Text(
            self.w_term_frame,
            yscrollcommand=self.w_t_scroll.set,
            bg=t["bg_terminal"], fg=t["fg_terminal"],
            font=(fm, 10), relief="flat", borderwidth=0,
            state="disabled", wrap="word",
            highlightthickness=0, cursor="arrow",
        )
        self.terminal.pack(side="left", fill="both", expand=True)
        self.w_t_scroll.config(command=self.terminal.yview)

        self._write_terminal("Command Manager ready.\n", "info")
        self._write_terminal("Click a command to load it in the entry bar, or double-click to run.\n\n", "info")

    # ── CWD ───────────────────────────────────────────────────────────────

    def _short_path(self, path):
        home = os.path.expanduser("~")
        if path.startswith(home):
            return "~" + path[len(home):]
        return path

    def _change_cwd(self):
        chosen = filedialog.askdirectory(title="Select Working Directory",
                                         initialdir=self.cwd)
        if chosen:
            self.cwd = chosen
            self.cwd_display_var.set(self._short_path(chosen))
            self.cwd_path_var.set(chosen)
            self._write_terminal(f"\n[cwd] {chosen}\n", "info")

    # ── List ──────────────────────────────────────────────────────────────

    def _refresh_list(self, select_index=None):
        self.w_listbox.delete(0, "end")
        for c in self.commands:
            self.w_listbox.insert("end", f"  {c['name']}")
        if select_index is not None and 0 <= select_index < len(self.commands):
            self.w_listbox.selection_set(select_index)
            self.w_listbox.activate(select_index)
            self._on_select()

    def _selected_index(self):
        sel = self.w_listbox.curselection()
        return sel[0] if sel else None

    def _on_select(self, event=None):
        idx = self._selected_index()
        if idx is not None:
            c = self.commands[idx]
            desc = c.get("description", "")
            self.detail_var.set(f"$ {c['command']}" + (f"\n{desc}" if desc else ""))
            # Load command into entry bar so user can adjust before running
            self.cmd_entry.delete(0, "end")
            self.cmd_entry.insert(0, c["command"])
            self.cmd_entry.icursor("end")
        else:
            self.detail_var.set("")

    # ── CRUD ──────────────────────────────────────────────────────────────

    def _add_command(self):
        dlg = CommandDialog(self, self.theme, "Add Command")
        self.wait_window(dlg)
        if dlg.result:
            self.commands.append(dlg.result)
            save_commands(self.commands)
            self._refresh_list(len(self.commands) - 1)

    def _edit_command(self):
        idx = self._selected_index()
        if idx is None:
            messagebox.showinfo("No Selection", "Please select a command to edit.")
            return
        c = self.commands[idx]
        dlg = CommandDialog(self, self.theme, "Edit Command",
                            c["name"], c["command"], c.get("description", ""))
        self.wait_window(dlg)
        if dlg.result:
            self.commands[idx] = dlg.result
            save_commands(self.commands)
            self._refresh_list(idx)

    def _remove_command(self):
        idx = self._selected_index()
        if idx is None:
            messagebox.showinfo("No Selection", "Please select a command to remove.")
            return
        name = self.commands[idx]["name"]
        if messagebox.askyesno("Confirm Remove", f"Remove '{name}'?"):
            self.commands.pop(idx)
            save_commands(self.commands)
            new_idx = min(idx, len(self.commands) - 1) if self.commands else None
            self._refresh_list(new_idx)
            self.detail_var.set("")

    # ── Execution ─────────────────────────────────────────────────────────

    def _run_selected(self):
        idx = self._selected_index()
        if idx is None:
            messagebox.showinfo("No Selection", "Please select a command to run.")
            return
        self._execute(self.commands[idx]["command"], self.commands[idx]["name"])

    def _run_entry(self):
        cmd = self.cmd_entry.get().strip()
        if not cmd:
            return
        self._execute(cmd, cmd)

    def _execute(self, command, label):
        if self.running:
            messagebox.showwarning("Busy", "A command is already running. Kill it first.")
            return
        ts = datetime.now().strftime("%H:%M:%S")
        self._write_terminal(f"\n[{ts}] ", "timestamp")
        self._write_terminal(f"$ {command}\n", "cmd")
        self._write_terminal(f"    in: {self.cwd}\n", "info")
        self.running = True
        self.status_var.set(f"running: {label}")
        threading.Thread(target=self._run_thread, args=(command,), daemon=True).start()

    def _run_thread(self, command):
        try:
            self.current_process = subprocess.Popen(
                command, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, bufsize=1,
                cwd=self.cwd,
            )
            for line in self.current_process.stdout:
                self._write_terminal(line, "stdout")
            for line in self.current_process.stderr:
                self._write_terminal(line, "stderr")
            retcode = self.current_process.wait()
            tag = "success" if retcode == 0 else "error"
            self._write_terminal(f"\n[exit {retcode}]\n", tag)
        except Exception as e:
            self._write_terminal(f"\nError: {e}\n", "error")
        finally:
            self.current_process = None
            self.running = False
            self.after(0, lambda: self.status_var.set("ready"))

    def _kill_process(self):
        if self.current_process:
            try:
                self.current_process.kill()
                self._write_terminal("\n[killed]\n", "error")
            except Exception as e:
                self._write_terminal(f"\nFailed to kill: {e}\n", "error")
        else:
            self._write_terminal("\nNo running process.\n", "info")

    def _write_terminal(self, text, tag="stdout"):
        def _do():
            self.terminal.config(state="normal")
            self.terminal.insert("end", text, tag)
            self.terminal.see("end")
            self.terminal.config(state="disabled")
        self.after(0, _do)

    def _save_output(self):
        content = self.terminal.get("1.0", "end").strip()
        if not content:
            messagebox.showinfo("Nothing to Save", "The terminal output is empty.")
            return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = filedialog.asksaveasfilename(
            title="Save Terminal Output",
            initialfile=f"terminal_output_{ts}.txt",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Log files", "*.log"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            self._write_terminal(f"\n[saved] {path}\n", "success")
        except IOError as e:
            messagebox.showerror("Save Failed", f"Could not save file:\n{e}")

    def _clear_terminal(self):
        self.terminal.config(state="normal")
        self.terminal.delete("1.0", "end")
        self.terminal.config(state="disabled")
        self._write_terminal("Terminal cleared.\n\n", "info")


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = CommandManagerApp()
    app.mainloop()
