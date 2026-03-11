#!/usr/bin/env python3
"""
Command Manager - GUI app to manage and run terminal commands, organised in folders.
Requires: tkinter (built-in), subprocess, json  — no third-party deps.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import subprocess
import threading
import json
import os
import sys
import io
import uuid
from datetime import datetime

# ── UTF-8 fix for Windows cp1252 terminals ────────────────────────────────────
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

COMMANDS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "commands.json")

# ─────────────────────────────────────────────────────────────────────────────
# Data model
#
#   commands.json  →  list of folder objects
#   [
#     {
#       "id":       "<uuid>",
#       "name":     "System",
#       "commands": [
#         { "id": "<uuid>", "name": "List Files", "command": "ls -la", "description": "..." },
#         ...
#       ]
#     },
#     ...
#   ]
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_DATA = [
    {
        "id": str(uuid.uuid4()), "name": "System",
        "commands": [
            {"id": str(uuid.uuid4()), "name": "List Files",  "command": "ls -la",  "description": "List all files"},
            {"id": str(uuid.uuid4()), "name": "System Info", "command": "uname -a", "description": "Show system info"},
            {"id": str(uuid.uuid4()), "name": "Disk Usage",  "command": "df -h",    "description": "Show disk usage"},
        ]
    },
    {
        "id": str(uuid.uuid4()), "name": "Navigation",
        "commands": [
            {"id": str(uuid.uuid4()), "name": "Current Dir", "command": "pwd",  "description": "Print working directory"},
            {"id": str(uuid.uuid4()), "name": "Date & Time", "command": "date", "description": "Show current date/time"},
        ]
    },
]


def _new_id():
    return str(uuid.uuid4())


def load_data():
    if os.path.exists(COMMANDS_FILE):
        try:
            with open(COMMANDS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # migrate old flat list → single "Default" folder
            if data and isinstance(data[0], dict) and "command" in data[0]:
                migrated = [{"id": _new_id(), "name": "Default",
                             "commands": [dict(c, id=_new_id()) for c in data]}]
                save_data(migrated)
                return migrated
            return data
        except (json.JSONDecodeError, IOError):
            pass
    save_data(DEFAULT_DATA)
    return [dict(f, commands=[dict(c) for c in f["commands"]]) for f in DEFAULT_DATA]


def save_data(folders):
    with open(COMMANDS_FILE, "w", encoding="utf-8") as f:
        json.dump(folders, f, indent=2)


# ─── Themes ──────────────────────────────────────────────────────────────────

THEMES = {
    "Cyber Night": {
        "bg_app": "#0d0d1a", "bg_header": "#070714", "bg_left": "#111128",
        "bg_tree": "#0d0d1a", "bg_right": "#0a0a0f", "bg_terminal": "#050510",
        "bg_entry": "#111128", "bg_divider": "#1a1a3a",
        "fg_title": "#00d4ff", "fg_label": "#606080", "fg_detail": "#505070",
        "fg_tree": "#c0c8e0", "fg_folder": "#00d4ff", "fg_cmd_item": "#a0b8d0",
        "fg_select_bg": "#1a2a3a", "fg_select_fg": "#00d4ff",
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
        "btn_folder": ("#304060", "#00d4ff"),
        "font_mono": "Courier New",
    },
    "Solarized Dark": {
        "bg_app": "#002b36", "bg_header": "#001e26", "bg_left": "#073642",
        "bg_tree": "#002b36", "bg_right": "#001e26", "bg_terminal": "#00141a",
        "bg_entry": "#073642", "bg_divider": "#0d4d5e",
        "fg_title": "#2aa198", "fg_label": "#586e75", "fg_detail": "#4a6068",
        "fg_tree": "#839496", "fg_folder": "#2aa198", "fg_cmd_item": "#657b83",
        "fg_select_bg": "#0d3a42", "fg_select_fg": "#2aa198",
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
        "btn_folder": ("#0d4d5e", "#2aa198"),
        "font_mono": "Courier New",
    },
    "Light Mint": {
        "bg_app": "#f0f4f0", "bg_header": "#d8ede0", "bg_left": "#e4f0e8",
        "bg_tree": "#f5faf6", "bg_right": "#f0f4f0", "bg_terminal": "#ffffff",
        "bg_entry": "#e8f4ec", "bg_divider": "#b8d8c0",
        "fg_title": "#1a7a4a", "fg_label": "#5a7a62", "fg_detail": "#6a8a72",
        "fg_tree": "#2a4a32", "fg_folder": "#1a7a4a", "fg_cmd_item": "#4a6a52",
        "fg_select_bg": "#c8e8d0", "fg_select_fg": "#1a5a3a",
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
        "btn_folder": ("#b8d8c0", "#1a7a4a"),
        "font_mono": "Courier New",
    },
    "Monokai": {
        "bg_app": "#272822", "bg_header": "#1a1a16", "bg_left": "#2d2e27",
        "bg_tree": "#272822", "bg_right": "#1e1f1a", "bg_terminal": "#1a1b16",
        "bg_entry": "#2d2e27", "bg_divider": "#3a3b34",
        "fg_title": "#66d9e8", "fg_label": "#75715e", "fg_detail": "#5a5a4e",
        "fg_tree": "#f8f8f2", "fg_folder": "#66d9e8", "fg_cmd_item": "#cfcfc2",
        "fg_select_bg": "#3a3b2e", "fg_select_fg": "#a6e22e",
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
        "btn_folder": ("#3a3b34", "#66d9e8"),
        "font_mono": "Courier New",
    },
    "Nord": {
        "bg_app": "#2e3440", "bg_header": "#242933", "bg_left": "#3b4252",
        "bg_tree": "#2e3440", "bg_right": "#242933", "bg_terminal": "#1e2330",
        "bg_entry": "#3b4252", "bg_divider": "#434c5e",
        "fg_title": "#88c0d0", "fg_label": "#616e88", "fg_detail": "#4c566a",
        "fg_tree": "#d8dee9", "fg_folder": "#88c0d0", "fg_cmd_item": "#adb8cc",
        "fg_select_bg": "#3b4a5e", "fg_select_fg": "#88c0d0",
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
        "btn_folder": ("#434c5e", "#88c0d0"),
        "font_mono": "Courier New",
    },
}

THEME_NAMES = list(THEMES.keys())


# ─── Dialogs ──────────────────────────────────────────────────────────────────

class CommandDialog(tk.Toplevel):
    """Add / Edit a command, with optional folder assignment."""

    def __init__(self, parent, theme, title,
                 name="", command="", description="",
                 folder_names=None, current_folder=None):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.result = None
        t = theme
        self.configure(bg=t["bg_left"])
        self.grab_set()

        pad = dict(padx=12, pady=6)
        fm = t["font_mono"]

        rows = [
            ("Name",        "name_var",  name,        t["fg_tree"]),
            ("Command",     "cmd_var",   command,     t["fg_cmd"]),
            ("Description", "desc_var",  description, t["fg_tree"]),
        ]
        for i, (lbl, attr, val, fg) in enumerate(rows):
            tk.Label(self, text=lbl, bg=t["bg_left"], fg=t["fg_label"],
                     font=(fm, 10)).grid(row=i, column=0, sticky="w", **pad)
            var = tk.StringVar(value=val)
            setattr(self, attr, var)
            tk.Entry(self, textvariable=var, width=38,
                     bg=t["bg_tree"], fg=fg,
                     insertbackground=t["fg_entry_insert"],
                     relief="flat", font=(fm, 11),
                     highlightthickness=1,
                     highlightbackground=t["hl_entry"],
                     highlightcolor=t["hl_focus"]).grid(row=i, column=1, **pad)

        # Folder picker
        if folder_names:
            tk.Label(self, text="Folder", bg=t["bg_left"], fg=t["fg_label"],
                     font=(fm, 10)).grid(row=3, column=0, sticky="w", **pad)
            self.folder_var = tk.StringVar(value=current_folder or folder_names[0])
            om = tk.OptionMenu(self, self.folder_var, *folder_names)
            om.configure(bg=t["bg_tree"], fg=t["fg_folder"],
                         activebackground=t["fg_select_bg"],
                         activeforeground=t["fg_select_fg"],
                         relief="flat", font=(fm, 10), highlightthickness=0)
            om.grid(row=3, column=1, sticky="w", **pad)
        else:
            self.folder_var = None

        btn_frame = tk.Frame(self, bg=t["bg_left"])
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)

        def on_ok():
            n = self.name_var.get().strip()
            c = self.cmd_var.get().strip()
            if not n or not c:
                messagebox.showwarning("Missing Fields", "Name and Command are required.", parent=self)
                return
            self.result = {
                "name": n, "command": c,
                "description": self.desc_var.get().strip(),
                "folder": self.folder_var.get() if self.folder_var else None,
            }
            self.destroy()

        acc_bg, acc_fg = t["btn_edit"]
        tk.Button(btn_frame, text="  Save  ", command=on_ok,
                  bg=acc_bg, fg=acc_fg, activebackground=acc_bg,
                  relief="flat", font=(fm, 10, "bold"), cursor="hand2", padx=8
                  ).pack(side="left", padx=6)

        g_bg, g_fg = t["btn_generic"]
        tk.Button(btn_frame, text=" Cancel ", command=self.destroy,
                  bg=g_bg, fg=g_fg, activebackground=g_bg,
                  relief="flat", font=(fm, 10), cursor="hand2", padx=8
                  ).pack(side="left", padx=6)

        self.bind("<Return>", lambda e: on_ok())
        self.bind("<Escape>", lambda e: self.destroy())
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width()  - self.winfo_width())  // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")


class MoveDialog(tk.Toplevel):
    """Choose a destination folder to move a command into."""

    def __init__(self, parent, theme, cmd_name, folder_names, current_folder):
        super().__init__(parent)
        self.title("Move Command")
        self.resizable(False, False)
        self.result = None
        t = theme
        self.configure(bg=t["bg_left"])
        self.grab_set()

        fm = t["font_mono"]
        pad = dict(padx=14, pady=6)

        tk.Label(self, text=f'Move  "{cmd_name}"  to folder:',
                 bg=t["bg_left"], fg=t["fg_label"], font=(fm, 10)
                 ).pack(**pad)

        self.folder_var = tk.StringVar(value=current_folder)
        for name in folder_names:
            rb = tk.Radiobutton(self, text=f"  {name}",
                                variable=self.folder_var, value=name,
                                bg=t["bg_left"], fg=t["fg_tree"],
                                selectcolor=t["bg_tree"],
                                activebackground=t["bg_left"],
                                font=(fm, 10), anchor="w")
            rb.pack(fill="x", padx=14, pady=2)

        btn_f = tk.Frame(self, bg=t["bg_left"])
        btn_f.pack(pady=10)

        def on_ok():
            self.result = self.folder_var.get()
            self.destroy()

        acc_bg, acc_fg = t["btn_edit"]
        tk.Button(btn_f, text="  Move  ", command=on_ok,
                  bg=acc_bg, fg=acc_fg, activebackground=acc_bg,
                  relief="flat", font=(fm, 10, "bold"), cursor="hand2", padx=8
                  ).pack(side="left", padx=6)

        g_bg, g_fg = t["btn_generic"]
        tk.Button(btn_f, text=" Cancel ", command=self.destroy,
                  bg=g_bg, fg=g_fg, activebackground=g_bg,
                  relief="flat", font=(fm, 10), cursor="hand2", padx=8
                  ).pack(side="left", padx=6)

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
        self.geometry("1220x740")
        self.minsize(900, 540)

        self.folders          = load_data()          # list of folder dicts
        self.current_process  = None
        self.running          = False
        self.cwd              = os.path.expanduser("~")
        self.theme_name       = tk.StringVar(value=THEME_NAMES[0])
        self.theme            = THEMES[THEME_NAMES[0]]

        self._build_ui()
        self._style_tree()
        self._apply_theme()
        self._refresh_tree()

    # ─── Helpers ──────────────────────────────────────────────────────────

    def _t(self, key):
        return self.theme[key]

    def _folder_names(self):
        return [f["name"] for f in self.folders]

    def _folder_by_name(self, name):
        for f in self.folders:
            if f["name"] == name:
                return f
        return None

    def _folder_by_id(self, fid):
        for f in self.folders:
            if f["id"] == fid:
                return f
        return None

    # Returns (folder_dict, command_dict) for the currently selected tree item,
    # or (folder_dict, None) if a folder row is selected.
    def _selection(self):
        sel = self.tree.selection()
        if not sel:
            return None, None
        iid = sel[0]
        tag = self.tree.item(iid, "tags")
        if "folder" in tag:
            fid = self.tree.item(iid, "values")[0]
            return self._folder_by_id(fid), None
        else:
            # command node — parent is folder
            parent_iid = self.tree.parent(iid)
            fid = self.tree.item(parent_iid, "values")[0]
            cid = self.tree.item(iid, "values")[0]
            folder = self._folder_by_id(fid)
            if folder:
                for c in folder["commands"]:
                    if c["id"] == cid:
                        return folder, c
        return None, None

    # ─── Theme ────────────────────────────────────────────────────────────

    def _switch_theme(self, name):
        self.theme = THEMES[name]
        self._style_tree()
        self._apply_theme()

    def _style_tree(self):
        t = self.theme
        fm = t["font_mono"]
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("CMD.Treeview",
                        background=t["bg_tree"],
                        foreground=t["fg_tree"],
                        fieldbackground=t["bg_tree"],
                        borderwidth=0,
                        font=(fm, 10),
                        rowheight=26)
        style.configure("CMD.Treeview.Heading",
                        background=t["bg_left"],
                        foreground=t["fg_label"],
                        font=(fm, 9, "bold"),
                        borderwidth=0)
        style.map("CMD.Treeview",
                  background=[("selected", t["fg_select_bg"])],
                  foreground=[("selected", t["fg_select_fg"])])
        style.configure("CMD.Treeview",
                        indent=18)

    def _apply_theme(self):
        t  = self.theme
        fm = t["font_mono"]

        self.configure(bg=t["bg_app"])

        # header
        self.w_header.configure(bg=t["bg_header"])
        self.w_title_lbl.configure(bg=t["bg_header"], fg=t["fg_title"], font=(fm, 14, "bold"))
        self.w_cwd_frame.configure(bg=t["bg_header"])
        self.w_cwd_lbl.configure(bg=t["bg_header"],  fg=t["fg_label"],  font=(fm, 8))
        self.w_cwd_val.configure(bg=t["bg_header"],   fg=t["fg_prompt"], font=(fm, 8))
        self.w_cwd_btn.configure(bg=t["fg_title"], fg=t["bg_app"],
                                 activebackground=t["fg_title"], font=(fm, 8, "bold"))
        self.w_theme_frame.configure(bg=t["bg_header"])
        self.w_theme_lbl.configure(bg=t["bg_header"], fg=t["fg_label"], font=(fm, 8))
        self.w_theme_menu.configure(bg=t["bg_left"], fg=t["fg_tree"],
                                    activebackground=t["fg_select_bg"],
                                    activeforeground=t["fg_select_fg"],
                                    highlightthickness=0, font=(fm, 8))

        # body / left
        self.w_body.configure(bg=t["bg_app"])
        self.w_left.configure(bg=t["bg_left"])
        self.w_tree_label.configure(bg=t["bg_left"], fg=t["fg_label"], font=(fm, 9, "bold"))
        self.w_tree_frame.configure(bg=t["bg_left"])
        self.w_tree_scroll.configure(bg=t["bg_left"], troughcolor=t["bg_app"])

        # folder toolbar
        self.w_folder_bar.configure(bg=t["bg_left"])
        for btn, key in [
            (self.w_btn_folder_add,    "btn_folder"),
            (self.w_btn_folder_rename, "btn_folder"),
            (self.w_btn_folder_delete, "btn_remove"),
        ]:
            bg, fg = t[key]
            btn.configure(bg=bg, fg=fg, activebackground=bg,
                          activeforeground=fg, font=(fm, 8, "bold"))

        # command toolbar
        self.w_cmd_bar.configure(bg=t["bg_left"])
        for btn, key in [
            (self.w_btn_add,    "btn_add"),
            (self.w_btn_edit,   "btn_edit"),
            (self.w_btn_remove, "btn_remove"),
            (self.w_btn_move,   "btn_folder"),
            (self.w_btn_run,    "btn_run"),
        ]:
            bg, fg = t[key]
            btn.configure(bg=bg, fg=fg, activebackground=bg,
                          activeforeground=fg, font=(fm, 8, "bold"))

        # detail label
        self.w_detail_lbl.configure(bg=t["bg_left"], fg=t["fg_detail"], font=(fm, 8))

        # divider
        self.w_divider.configure(bg=t["bg_divider"])

        # right / terminal
        self.w_right.configure(bg=t["bg_right"])
        self.w_term_header.configure(bg=t["bg_header"])
        self.w_term_lbl.configure(bg=t["bg_header"], fg=t["fg_success"], font=(fm, 9, "bold"))
        self.w_status_lbl.configure(bg=t["bg_header"], fg=t["fg_status"], font=(fm, 8))
        for btn, key in [
            (self.w_btn_kill,  "btn_kill"),
            (self.w_btn_save,  "btn_save"),
            (self.w_btn_clear, "btn_clear"),
        ]:
            bg, fg = t[key]
            btn.configure(bg=bg, fg=fg, activebackground=bg,
                          activeforeground=fg, font=(fm, 9, "bold"))

        # cwd bar
        self.w_cwd_bar.configure(bg=t["bg_right"])
        self.w_cwd_prefix.configure(bg=t["bg_right"], fg=t["fg_label"], font=(fm, 8))
        self.w_cwd_path_lbl.configure(bg=t["bg_right"], fg=t["fg_prompt"], font=(fm, 8))

        # entry bar
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

        # terminal
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

        # re-style tree rows
        self._style_tree()
        try:
            self.tree.tag_configure("folder",  foreground=t["fg_folder"],
                                    font=(fm, 10, "bold"))
            self.tree.tag_configure("command", foreground=t["fg_cmd_item"],
                                    font=(fm, 10))
        except Exception:
            pass

    # ─── UI Build ─────────────────────────────────────────────────────────

    def _make_btn(self, parent, text, cmd, color_key, pady=None):
        bg, fg = self._t(color_key)
        kw = dict(text=text, command=cmd, bg=bg, fg=fg,
                  activebackground=bg, activeforeground=fg,
                  relief="flat", font=(self._t("font_mono"), 8, "bold"),
                  cursor="hand2", padx=5)
        if pady is not None:
            kw["pady"] = pady
        return tk.Button(parent, **kw)

    def _build_ui(self):
        t  = self.theme
        fm = t["font_mono"]

        # ── Header ──────────────────────────────────────────────────────
        self.w_header = tk.Frame(self, bg=t["bg_header"], height=52)
        self.w_header.pack(fill="x")
        self.w_header.pack_propagate(False)

        self.w_title_lbl = tk.Label(self.w_header, text="COMMAND MANAGER",
                                    bg=t["bg_header"], fg=t["fg_title"],
                                    font=(fm, 14, "bold"))
        self.w_title_lbl.pack(side="left", padx=18, pady=14)

        # Theme dropdown
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

        # ── Body ────────────────────────────────────────────────────────
        self.w_body = tk.Frame(self, bg=t["bg_app"])
        self.w_body.pack(fill="both", expand=True)

        # ── Left pane ───────────────────────────────────────────────────
        self.w_left = tk.Frame(self.w_body, bg=t["bg_left"], width=300)
        self.w_left.pack(side="left", fill="y")
        self.w_left.pack_propagate(False)

        self.w_tree_label = tk.Label(self.w_left, text="FOLDERS & COMMANDS",
                                     bg=t["bg_left"], fg=t["fg_label"],
                                     font=(fm, 9, "bold"))
        self.w_tree_label.pack(anchor="w", padx=14, pady=(12, 4))

        # Tree widget
        self.w_tree_frame = tk.Frame(self.w_left, bg=t["bg_left"])
        self.w_tree_frame.pack(fill="both", expand=True, padx=6, pady=2)

        self.w_tree_scroll = tk.Scrollbar(self.w_tree_frame, orient="vertical",
                                          bg=t["bg_left"], troughcolor=t["bg_app"],
                                          relief="flat", width=8)
        self.w_tree_scroll.pack(side="right", fill="y")

        self.tree = ttk.Treeview(self.w_tree_frame,
                                 style="CMD.Treeview",
                                 yscrollcommand=self.w_tree_scroll.set,
                                 show="tree",
                                 selectmode="browse")
        self.tree.pack(side="left", fill="both", expand=True)
        self.w_tree_scroll.config(command=self.tree.yview)

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.tree.bind("<Double-Button-1>",  self._on_tree_double_click)

        # Detail label
        self.detail_var = tk.StringVar(value="")
        self.w_detail_lbl = tk.Label(self.w_left, textvariable=self.detail_var,
                                     bg=t["bg_left"], fg=t["fg_detail"],
                                     font=(fm, 8), wraplength=270,
                                     justify="left", anchor="w")
        self.w_detail_lbl.pack(fill="x", padx=14, pady=(2, 4))

        # Folder toolbar
        self.w_folder_bar = tk.Frame(self.w_left, bg=t["bg_left"])
        self.w_folder_bar.pack(fill="x", padx=6, pady=(2, 0))

        folder_lbl = tk.Label(self.w_folder_bar, text="FOLDER:",
                              bg=t["bg_left"], fg=t["fg_label"],
                              font=(fm, 7, "bold"))
        folder_lbl.pack(side="left", padx=(4, 6))

        self.w_btn_folder_add    = self._make_btn(self.w_folder_bar, "+ New",    self._add_folder,    "btn_folder")
        self.w_btn_folder_rename = self._make_btn(self.w_folder_bar, "* Rename", self._rename_folder, "btn_folder")
        self.w_btn_folder_delete = self._make_btn(self.w_folder_bar, "x Delete", self._delete_folder, "btn_remove")
        self.w_btn_folder_add.pack(side="left",    padx=2, pady=3)
        self.w_btn_folder_rename.pack(side="left", padx=2, pady=3)
        self.w_btn_folder_delete.pack(side="left", padx=2, pady=3)

        # Command toolbar
        self.w_cmd_bar = tk.Frame(self.w_left, bg=t["bg_left"])
        self.w_cmd_bar.pack(fill="x", padx=6, pady=(0, 8))

        cmd_lbl = tk.Label(self.w_cmd_bar, text="CMD:",
                           bg=t["bg_left"], fg=t["fg_label"],
                           font=(fm, 7, "bold"))
        cmd_lbl.pack(side="left", padx=(4, 6))

        self.w_btn_add    = self._make_btn(self.w_cmd_bar, "+ Add",  self._add_command,    "btn_add")
        self.w_btn_edit   = self._make_btn(self.w_cmd_bar, "* Edit", self._edit_command,   "btn_edit")
        self.w_btn_remove = self._make_btn(self.w_cmd_bar, "x Del",  self._remove_command, "btn_remove")
        self.w_btn_move   = self._make_btn(self.w_cmd_bar, "> Move", self._move_command,   "btn_folder")
        self.w_btn_run    = self._make_btn(self.w_cmd_bar, ">> Run", self._run_selected,   "btn_run")
        for b in [self.w_btn_add, self.w_btn_edit, self.w_btn_remove,
                  self.w_btn_move, self.w_btn_run]:
            b.pack(side="left", padx=2, pady=3)

        # ── Divider ─────────────────────────────────────────────────────
        self.w_divider = tk.Frame(self.w_body, bg=t["bg_divider"], width=1)
        self.w_divider.pack(side="left", fill="y")

        # ── Right pane ──────────────────────────────────────────────────
        self.w_right = tk.Frame(self.w_body, bg=t["bg_right"])
        self.w_right.pack(side="left", fill="both", expand=True)

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

        self.w_btn_kill  = tk.Button(self.w_term_header, text="Kill",
                                     command=self._kill_process,
                                     **self._tbtn(t, "btn_kill"))
        self.w_btn_save  = tk.Button(self.w_term_header, text="Save",
                                     command=self._save_output,
                                     **self._tbtn(t, "btn_save"))
        self.w_btn_clear = tk.Button(self.w_term_header, text="Clear",
                                     command=self._clear_terminal,
                                     **self._tbtn(t, "btn_clear"))
        self.w_btn_kill.pack(side="right",  padx=4, pady=4)
        self.w_btn_save.pack(side="right",  padx=4, pady=4)
        self.w_btn_clear.pack(side="right", padx=4, pady=4)

        # CWD display
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
        self._setup_entry_bindings(self.cmd_entry)

        bg, fg = t["btn_run"]
        self.w_btn_run_entry = tk.Button(self.w_entry_frame, text="> Run",
                                         command=self._run_entry,
                                         bg=bg, fg=fg, activebackground=bg,
                                         relief="flat", font=(fm, 9, "bold"),
                                         cursor="hand2", padx=6, pady=2)
        self.w_btn_run_entry.pack(side="left", padx=(6, 0))

        # Terminal text
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
        self._setup_terminal_bindings(self.terminal)

        self._write_terminal("Command Manager ready.\n", "info")
        self._write_terminal("Click a command to load it, double-click to run.\n\n", "info")

    def _tbtn(self, t, key, pady=2):
        bg, fg = t[key]
        return dict(bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
                    relief="flat", font=(t["font_mono"], 9, "bold"),
                    cursor="hand2", padx=6, pady=pady)

    # ─── Copy / Paste helpers ─────────────────────────────────────────────

    def _setup_entry_bindings(self, entry):
        """Attach keyboard shortcuts and right-click context menu to an Entry widget."""
        # On Windows tkinter doesn't always wire these automatically
        entry.bind("<Control-a>",         lambda e: self._entry_select_all(entry))
        entry.bind("<Control-A>",         lambda e: self._entry_select_all(entry))
        entry.bind("<Control-c>",         lambda e: self._entry_copy(entry))
        entry.bind("<Control-C>",         lambda e: self._entry_copy(entry))
        entry.bind("<Control-x>",         lambda e: self._entry_cut(entry))
        entry.bind("<Control-X>",         lambda e: self._entry_cut(entry))
        entry.bind("<Control-v>",         lambda e: self._entry_paste(entry))
        entry.bind("<Control-V>",         lambda e: self._entry_paste(entry))
        entry.bind("<Control-z>",         lambda e: self._entry_undo(entry))
        entry.bind("<Control-Z>",         lambda e: self._entry_undo(entry))
        # macOS uses Command (Meta)
        entry.bind("<Command-a>",         lambda e: self._entry_select_all(entry))
        entry.bind("<Command-c>",         lambda e: self._entry_copy(entry))
        entry.bind("<Command-x>",         lambda e: self._entry_cut(entry))
        entry.bind("<Command-v>",         lambda e: self._entry_paste(entry))
        entry.bind("<Command-z>",         lambda e: self._entry_undo(entry))
        # Right-click context menu
        entry.bind("<Button-3>",          lambda e: self._show_entry_menu(e, entry))
        entry.bind("<Control-Button-1>",  lambda e: self._show_entry_menu(e, entry))  # macOS Ctrl+click

    def _setup_terminal_bindings(self, text_widget):
        """Attach right-click context menu and copy shortcut to the read-only terminal."""
        text_widget.bind("<Button-3>",         lambda e: self._show_terminal_menu(e, text_widget))
        text_widget.bind("<Control-Button-1>", lambda e: self._show_terminal_menu(e, text_widget))
        # Allow Ctrl+C / Cmd+C to copy selected text from the terminal
        text_widget.bind("<Control-c>",  lambda e: self._terminal_copy(text_widget))
        text_widget.bind("<Control-C>",  lambda e: self._terminal_copy(text_widget))
        text_widget.bind("<Command-c>",  lambda e: self._terminal_copy(text_widget))
        text_widget.bind("<Control-a>",  lambda e: self._terminal_select_all(text_widget))
        text_widget.bind("<Control-A>",  lambda e: self._terminal_select_all(text_widget))
        text_widget.bind("<Command-a>",  lambda e: self._terminal_select_all(text_widget))

    # Entry actions
    def _entry_select_all(self, entry):
        entry.select_range(0, "end")
        entry.icursor("end")
        return "break"

    def _entry_copy(self, entry):
        try:
            text = entry.selection_get()
            self.clipboard_clear()
            self.clipboard_append(text)
        except tk.TclError:
            pass
        return "break"

    def _entry_cut(self, entry):
        try:
            text = entry.selection_get()
            self.clipboard_clear()
            self.clipboard_append(text)
            entry.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            pass
        return "break"

    def _entry_paste(self, entry):
        try:
            text = self.clipboard_get()
            # Replace selection if any, otherwise insert at cursor
            try:
                entry.delete(tk.SEL_FIRST, tk.SEL_LAST)
            except tk.TclError:
                pass
            entry.insert(tk.INSERT, text)
        except tk.TclError:
            pass
        return "break"

    def _entry_undo(self, entry):
        try:
            entry.event_generate("<<Undo>>")
        except tk.TclError:
            pass
        return "break"

    def _copy_to_entry(self, entry):
        """Copy terminal selection into the command entry bar."""
        try:
            text = self.terminal.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
            if text:
                entry.delete(0, "end")
                entry.insert(0, text)
                entry.icursor("end")
                entry.focus_set()
        except tk.TclError:
            pass

    # Terminal actions
    def _terminal_copy(self, text_widget):
        try:
            text = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(text)
        except tk.TclError:
            pass
        return "break"

    def _terminal_select_all(self, text_widget):
        text_widget.tag_add(tk.SEL, "1.0", "end")
        return "break"

    # Context menus
    def _show_entry_menu(self, event, entry):
        t  = self.theme
        fm = t["font_mono"]
        menu = tk.Menu(self, tearoff=0,
                       bg=t["bg_left"], fg=t["fg_tree"],
                       activebackground=t["fg_select_bg"],
                       activeforeground=t["fg_select_fg"],
                       font=(fm, 9))

        has_sel = False
        try:
            entry.selection_get()
            has_sel = True
        except tk.TclError:
            pass

        has_clip = False
        try:
            has_clip = bool(self.clipboard_get())
        except tk.TclError:
            pass

        menu.add_command(label="Cut",        command=lambda: self._entry_cut(entry),
                         state="normal" if has_sel else "disabled")
        menu.add_command(label="Copy",       command=lambda: self._entry_copy(entry),
                         state="normal" if has_sel else "disabled")
        menu.add_command(label="Paste",      command=lambda: self._entry_paste(entry),
                         state="normal" if has_clip else "disabled")
        menu.add_separator()
        menu.add_command(label="Select All", command=lambda: self._entry_select_all(entry))
        menu.add_separator()
        menu.add_command(label="Clear",      command=lambda: entry.delete(0, "end"))

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _show_terminal_menu(self, event, text_widget):
        t  = self.theme
        fm = t["font_mono"]
        menu = tk.Menu(self, tearoff=0,
                       bg=t["bg_left"], fg=t["fg_tree"],
                       activebackground=t["fg_select_bg"],
                       activeforeground=t["fg_select_fg"],
                       font=(fm, 9))

        has_sel = False
        try:
            text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            has_sel = True
        except tk.TclError:
            pass

        menu.add_command(label="Copy",              command=lambda: self._terminal_copy(text_widget),
                         state="normal" if has_sel else "disabled")
        menu.add_command(label="Copy to Entry Bar", command=lambda: self._copy_to_entry(self.cmd_entry),
                         state="normal" if has_sel else "disabled")
        menu.add_separator()
        menu.add_command(label="Select All",        command=lambda: self._terminal_select_all(text_widget))
        menu.add_separator()
        menu.add_command(label="Clear Terminal",    command=self._clear_terminal)
        menu.add_command(label="Save Output...",    command=self._save_output)

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    # ─── Tree ─────────────────────────────────────────────────────────────

    def _refresh_tree(self, expand_folder_name=None, select_cmd_id=None):
        t  = self.theme
        fm = t["font_mono"]

        # Remember which folders are open
        open_ids = {iid for iid in self.tree.get_children()
                    if self.tree.item(iid, "open")}
        open_names = set()
        for iid in open_ids:
            vals = self.tree.item(iid, "values")
            if vals:
                f = self._folder_by_id(vals[0])
                if f:
                    open_names.add(f["name"])

        self.tree.delete(*self.tree.get_children())

        target_iid = None
        for folder in self.folders:
            fid  = folder["id"]
            fn   = folder["name"]
            cnt  = len(folder["commands"])
            fiid = self.tree.insert("", "end",
                                    text=f"  {fn}  ({cnt})",
                                    values=(fid,),
                                    tags=("folder",),
                                    open=True)
            for cmd in folder["commands"]:
                ciid = self.tree.insert(fiid, "end",
                                        text=f"    {cmd['name']}",
                                        values=(cmd["id"],),
                                        tags=("command",))
                if cmd["id"] == select_cmd_id:
                    target_iid = ciid

            # restore open/close state
            if fn not in open_names and expand_folder_name != fn:
                self.tree.item(fiid, open=False)
            if expand_folder_name == fn:
                self.tree.item(fiid, open=True)

        self.tree.tag_configure("folder",  foreground=t["fg_folder"],
                                font=(fm, 10, "bold"))
        self.tree.tag_configure("command", foreground=t["fg_cmd_item"],
                                font=(fm, 10))

        if target_iid:
            self.tree.selection_set(target_iid)
            self.tree.see(target_iid)

    def _on_tree_select(self, event=None):
        folder, cmd = self._selection()
        if cmd:
            desc = cmd.get("description", "")
            self.detail_var.set(f"$ {cmd['command']}" + (f"\n{desc}" if desc else ""))
            self.cmd_entry.delete(0, "end")
            self.cmd_entry.insert(0, cmd["command"])
            self.cmd_entry.icursor("end")
        elif folder:
            self.detail_var.set(f"Folder: {folder['name']}  ({len(folder['commands'])} commands)")
        else:
            self.detail_var.set("")

    def _on_tree_double_click(self, event=None):
        _, cmd = self._selection()
        if cmd:
            self._execute(cmd["command"], cmd["name"])

    # ─── Folder CRUD ──────────────────────────────────────────────────────

    def _add_folder(self):
        name = simpledialog.askstring("New Folder", "Folder name:", parent=self)
        if not name:
            return
        name = name.strip()
        if not name:
            return
        if self._folder_by_name(name):
            messagebox.showwarning("Duplicate", f"A folder named '{name}' already exists.")
            return
        self.folders.append({"id": _new_id(), "name": name, "commands": []})
        save_data(self.folders)
        self._refresh_tree(expand_folder_name=name)

    def _rename_folder(self):
        folder, _ = self._selection()
        if not folder:
            messagebox.showinfo("No Folder Selected",
                                "Click a folder (or a command inside one) first.")
            return
        new_name = simpledialog.askstring("Rename Folder", "New name:",
                                          initialvalue=folder["name"], parent=self)
        if not new_name:
            return
        new_name = new_name.strip()
        if not new_name:
            return
        existing = self._folder_by_name(new_name)
        if existing and existing["id"] != folder["id"]:
            messagebox.showwarning("Duplicate", f"A folder named '{new_name}' already exists.")
            return
        folder["name"] = new_name
        save_data(self.folders)
        self._refresh_tree(expand_folder_name=new_name)

    def _delete_folder(self):
        folder, _ = self._selection()
        if not folder:
            messagebox.showinfo("No Folder Selected",
                                "Click a folder (or a command inside one) first.")
            return
        if len(self.folders) == 1:
            messagebox.showwarning("Cannot Delete",
                                   "You must have at least one folder.")
            return
        n = len(folder["commands"])
        msg = f"Delete folder '{folder['name']}'"
        msg += f" and all {n} command(s) inside it?" if n else "?"
        if not messagebox.askyesno("Confirm Delete", msg):
            return
        self.folders = [f for f in self.folders if f["id"] != folder["id"]]
        save_data(self.folders)
        self._refresh_tree()
        self.detail_var.set("")

    # ─── Command CRUD ─────────────────────────────────────────────────────

    def _add_command(self):
        folder_names = self._folder_names()
        # pre-select the currently highlighted folder
        folder, _ = self._selection()
        current_folder = folder["name"] if folder else folder_names[0]

        dlg = CommandDialog(self, self.theme, "Add Command",
                            folder_names=folder_names,
                            current_folder=current_folder)
        self.wait_window(dlg)
        if not dlg.result:
            return
        r = dlg.result
        target = self._folder_by_name(r["folder"]) or self.folders[0]
        target["commands"].append({
            "id": _new_id(), "name": r["name"],
            "command": r["command"], "description": r["description"],
        })
        save_data(self.folders)
        self._refresh_tree(expand_folder_name=target["name"])

    def _edit_command(self):
        folder, cmd = self._selection()
        if not cmd:
            messagebox.showinfo("No Command Selected", "Please select a command to edit.")
            return
        dlg = CommandDialog(self, self.theme, "Edit Command",
                            name=cmd["name"], command=cmd["command"],
                            description=cmd.get("description", ""),
                            folder_names=self._folder_names(),
                            current_folder=folder["name"])
        self.wait_window(dlg)
        if not dlg.result:
            return
        r = dlg.result
        cmd["name"]        = r["name"]
        cmd["command"]     = r["command"]
        cmd["description"] = r["description"]

        # handle folder change inside edit dialog
        new_folder_name = r.get("folder")
        if new_folder_name and new_folder_name != folder["name"]:
            folder["commands"].remove(cmd)
            dest = self._folder_by_name(new_folder_name)
            if dest:
                dest["commands"].append(cmd)
            save_data(self.folders)
            self._refresh_tree(expand_folder_name=new_folder_name,
                               select_cmd_id=cmd["id"])
        else:
            save_data(self.folders)
            self._refresh_tree(expand_folder_name=folder["name"],
                               select_cmd_id=cmd["id"])

    def _remove_command(self):
        folder, cmd = self._selection()
        if not cmd:
            messagebox.showinfo("No Command Selected", "Please select a command to remove.")
            return
        if messagebox.askyesno("Confirm Remove", f"Remove '{cmd['name']}'?"):
            folder["commands"].remove(cmd)
            save_data(self.folders)
            self._refresh_tree(expand_folder_name=folder["name"])
            self.detail_var.set("")

    def _move_command(self):
        folder, cmd = self._selection()
        if not cmd:
            messagebox.showinfo("No Command Selected", "Please select a command to move.")
            return
        folder_names = self._folder_names()
        if len(folder_names) < 2:
            messagebox.showinfo("Only One Folder",
                                "Add more folders before moving commands.")
            return
        dlg = MoveDialog(self, self.theme, cmd["name"],
                         folder_names, folder["name"])
        self.wait_window(dlg)
        if not dlg.result or dlg.result == folder["name"]:
            return
        dest = self._folder_by_name(dlg.result)
        if dest:
            folder["commands"].remove(cmd)
            dest["commands"].append(cmd)
            save_data(self.folders)
            self._refresh_tree(expand_folder_name=dest["name"],
                               select_cmd_id=cmd["id"])

    # ─── CWD ──────────────────────────────────────────────────────────────

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

    # ─── Execution ────────────────────────────────────────────────────────

    def _run_selected(self):
        _, cmd = self._selection()
        if not cmd:
            messagebox.showinfo("No Command Selected", "Please select a command to run.")
            return
        self._execute(cmd["command"], cmd["name"])

    def _run_entry(self):
        text = self.cmd_entry.get().strip()
        if text:
            self._execute(text, text)

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
                text=True, bufsize=1, cwd=self.cwd,
            )
            for line in self.current_process.stdout:
                self._write_terminal(line, "stdout")
            for line in self.current_process.stderr:
                self._write_terminal(line, "stderr")
            rc = self.current_process.wait()
            self._write_terminal(f"\n[exit {rc}]\n", "success" if rc == 0 else "error")
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
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = filedialog.asksaveasfilename(
            title="Save Terminal Output",
            initialfile=f"terminal_output_{ts}.txt",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"),
                       ("Log files",  "*.log"),
                       ("All files",  "*.*")],
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
