#!/usr/bin/env python3
"""
Command Manager - A GUI application to manage and run terminal commands.
Requires: tkinter (built-in), subprocess, json
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import subprocess
import threading
import json
import os
import shlex
import sys
from datetime import datetime

COMMANDS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "commands.json")

DEFAULT_COMMANDS = [
    {"name": "List Files", "command": "ls -la", "description": "List all files in current directory"},
    {"name": "System Info", "command": "uname -a", "description": "Show system information"},
    {"name": "Disk Usage", "command": "df -h", "description": "Show disk usage"},
    {"name": "Current Dir", "command": "pwd", "description": "Print working directory"},
    {"name": "Date & Time", "command": "date", "description": "Show current date and time"},
]


# ─── Data Layer ─────────────────────────────────────────────────────────────

def load_commands():
    if os.path.exists(COMMANDS_FILE):
        try:
            with open(COMMANDS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    save_commands(DEFAULT_COMMANDS)
    return DEFAULT_COMMANDS


def save_commands(commands):
    with open(COMMANDS_FILE, "w") as f:
        json.dump(commands, f, indent=2)


# ─── Dialog ─────────────────────────────────────────────────────────────────

class CommandDialog(tk.Toplevel):
    """Modal dialog for adding/editing a command."""

    def __init__(self, parent, title, name="", command="", description=""):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.result = None

        self.configure(bg="#1a1a2e")
        self.grab_set()

        pad = dict(padx=12, pady=6)

        tk.Label(self, text="Name", bg="#1a1a2e", fg="#a0a8c0",
                 font=("Courier New", 10)).grid(row=0, column=0, sticky="w", **pad)
        self.name_var = tk.StringVar(value=name)
        tk.Entry(self, textvariable=self.name_var, width=36,
                 bg="#0d0d1a", fg="#e0e8ff", insertbackground="#00d4ff",
                 relief="flat", font=("Courier New", 11),
                 highlightthickness=1, highlightbackground="#2a2a4a",
                 highlightcolor="#00d4ff").grid(row=0, column=1, **pad)

        tk.Label(self, text="Command", bg="#1a1a2e", fg="#a0a8c0",
                 font=("Courier New", 10)).grid(row=1, column=0, sticky="w", **pad)
        self.cmd_var = tk.StringVar(value=command)
        tk.Entry(self, textvariable=self.cmd_var, width=36,
                 bg="#0d0d1a", fg="#00ff9f", insertbackground="#00d4ff",
                 relief="flat", font=("Courier New", 11),
                 highlightthickness=1, highlightbackground="#2a2a4a",
                 highlightcolor="#00d4ff").grid(row=1, column=1, **pad)

        tk.Label(self, text="Description", bg="#1a1a2e", fg="#a0a8c0",
                 font=("Courier New", 10)).grid(row=2, column=0, sticky="w", **pad)
        self.desc_var = tk.StringVar(value=description)
        tk.Entry(self, textvariable=self.desc_var, width=36,
                 bg="#0d0d1a", fg="#e0e8ff", insertbackground="#00d4ff",
                 relief="flat", font=("Courier New", 11),
                 highlightthickness=1, highlightbackground="#2a2a4a",
                 highlightcolor="#00d4ff").grid(row=2, column=1, **pad)

        btn_frame = tk.Frame(self, bg="#1a1a2e")
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)

        def on_ok():
            n = self.name_var.get().strip()
            c = self.cmd_var.get().strip()
            if not n or not c:
                messagebox.showwarning("Missing Fields", "Name and Command are required.", parent=self)
                return
            self.result = {"name": n, "command": c, "description": self.desc_var.get().strip()}
            self.destroy()

        tk.Button(btn_frame, text="  Save  ", command=on_ok,
                  bg="#00d4ff", fg="#0d0d1a", activebackground="#00b8e0",
                  relief="flat", font=("Courier New", 10, "bold"),
                  cursor="hand2", padx=8).pack(side="left", padx=6)

        tk.Button(btn_frame, text=" Cancel ", command=self.destroy,
                  bg="#2a2a4a", fg="#a0a8c0", activebackground="#3a3a5a",
                  relief="flat", font=("Courier New", 10),
                  cursor="hand2", padx=8).pack(side="left", padx=6)

        self.bind("<Return>", lambda e: on_ok())
        self.bind("<Escape>", lambda e: self.destroy())
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")


# ─── Main Application ────────────────────────────────────────────────────────

class CommandManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("⚡ Command Manager")
        self.geometry("1100x700")
        self.minsize(800, 500)
        self.configure(bg="#0d0d1a")

        # State
        self.commands = load_commands()
        self.current_process = None
        self.running = False

        self._build_ui()
        self._refresh_list()

    # ── UI Construction ───────────────────────────────────────────────────

    def _build_ui(self):
        # ── Header ──
        header = tk.Frame(self, bg="#070714", height=52)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="⚡ COMMAND MANAGER",
                 bg="#070714", fg="#00d4ff",
                 font=("Courier New", 14, "bold")).pack(side="left", padx=18, pady=14)

        tk.Label(header, text=f"commands saved in: {COMMANDS_FILE}",
                 bg="#070714", fg="#404060",
                 font=("Courier New", 8)).pack(side="right", padx=18)

        # ── Body ──
        body = tk.Frame(self, bg="#0d0d1a")
        body.pack(fill="both", expand=True, padx=0, pady=0)

        # Left pane
        left = tk.Frame(body, bg="#111128", width=280)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Label(left, text="COMMANDS", bg="#111128", fg="#606080",
                 font=("Courier New", 9, "bold")).pack(anchor="w", padx=14, pady=(14, 4))

        # Listbox with scrollbar
        list_frame = tk.Frame(left, bg="#111128")
        list_frame.pack(fill="both", expand=True, padx=8, pady=4)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical", bg="#1a1a3a",
                                 troughcolor="#0d0d1a", relief="flat", width=8)
        scrollbar.pack(side="right", fill="y")

        self.listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            bg="#0d0d1a", fg="#c0c8e0",
            selectbackground="#00d4ff", selectforeground="#0d0d1a",
            font=("Courier New", 11),
            relief="flat",
            borderwidth=0,
            activestyle="none",
            highlightthickness=0,
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)
        self.listbox.bind("<Double-Button-1>", lambda e: self._run_selected())

        # Command detail label
        self.detail_var = tk.StringVar(value="")
        tk.Label(left, textvariable=self.detail_var, bg="#111128", fg="#505070",
                 font=("Courier New", 8), wraplength=250, justify="left",
                 anchor="w").pack(fill="x", padx=14, pady=(0, 6))

        # Buttons
        btn_row1 = tk.Frame(left, bg="#111128")
        btn_row1.pack(fill="x", padx=8, pady=2)

        self._btn(btn_row1, "＋ Add", self._add_command, "#00ff9f", "#0d1a0d").pack(side="left", fill="x", expand=True, padx=2)
        self._btn(btn_row1, "✎ Edit", self._edit_command, "#00d4ff", "#0d1a1a").pack(side="left", fill="x", expand=True, padx=2)

        btn_row2 = tk.Frame(left, bg="#111128")
        btn_row2.pack(fill="x", padx=8, pady=(2, 8))

        self._btn(btn_row2, "✕ Remove", self._remove_command, "#ff4f7b", "#1a0d10").pack(side="left", fill="x", expand=True, padx=2)
        self._btn(btn_row2, "▶ Run", self._run_selected, "#ffd700", "#1a1800").pack(side="left", fill="x", expand=True, padx=2)

        # Divider
        tk.Frame(body, bg="#1a1a3a", width=1).pack(side="left", fill="y")

        # Right pane — terminal
        right = tk.Frame(body, bg="#0a0a0f")
        right.pack(side="left", fill="both", expand=True)

        term_header = tk.Frame(right, bg="#070714", height=36)
        term_header.pack(fill="x")
        term_header.pack_propagate(False)

        tk.Label(term_header, text="● TERMINAL", bg="#070714", fg="#00ff9f",
                 font=("Courier New", 9, "bold")).pack(side="left", padx=14, pady=8)

        self.status_var = tk.StringVar(value="ready")
        tk.Label(term_header, textvariable=self.status_var, bg="#070714", fg="#606080",
                 font=("Courier New", 8)).pack(side="right", padx=14)

        self._btn(term_header, "⏹ Kill", self._kill_process, "#ff4f7b", "#1a0d10",
                  height=1).pack(side="right", padx=4, pady=4)
        self._btn(term_header, "💾 Save", self._save_output, "#a78bfa", "#100d1a",
                  height=1).pack(side="right", padx=4, pady=4)
        self._btn(term_header, "Clear", self._clear_terminal, "#404060", "#0d0d1a",
                  height=1).pack(side="right", padx=4, pady=4)

        # Custom command entry
        entry_frame = tk.Frame(right, bg="#0a0a0f")
        entry_frame.pack(fill="x", padx=10, pady=(8, 4))

        tk.Label(entry_frame, text="$", bg="#0a0a0f", fg="#00ff9f",
                 font=("Courier New", 12, "bold")).pack(side="left", padx=(4, 6))

        self.cmd_entry = tk.Entry(
            entry_frame,
            bg="#111128", fg="#00ff9f",
            insertbackground="#00d4ff",
            relief="flat",
            font=("Courier New", 11),
            highlightthickness=1,
            highlightbackground="#2a2a4a",
            highlightcolor="#00d4ff",
        )
        self.cmd_entry.pack(side="left", fill="x", expand=True, ipady=5)
        self.cmd_entry.bind("<Return>", lambda e: self._run_entry())

        self._btn(entry_frame, "▶ Run", self._run_entry, "#ffd700", "#1a1800",
                  height=1).pack(side="left", padx=(6, 0))

        # Terminal output
        term_frame = tk.Frame(right, bg="#0a0a0f")
        term_frame.pack(fill="both", expand=True, padx=10, pady=(4, 10))

        t_scroll = tk.Scrollbar(term_frame, orient="vertical", bg="#1a1a3a",
                                troughcolor="#0d0d1a", relief="flat", width=8)
        t_scroll.pack(side="right", fill="y")

        self.terminal = tk.Text(
            term_frame,
            yscrollcommand=t_scroll.set,
            bg="#050510", fg="#c0c8e0",
            font=("Courier New", 10),
            relief="flat",
            borderwidth=0,
            state="disabled",
            wrap="word",
            highlightthickness=0,
            cursor="arrow",
        )
        self.terminal.pack(side="left", fill="both", expand=True)
        t_scroll.config(command=self.terminal.yview)

        # Text tags for coloring
        self.terminal.tag_config("prompt", foreground="#00d4ff")
        self.terminal.tag_config("cmd", foreground="#00ff9f")
        self.terminal.tag_config("stdout", foreground="#c0c8e0")
        self.terminal.tag_config("stderr", foreground="#ff6b8a")
        self.terminal.tag_config("info", foreground="#606080")
        self.terminal.tag_config("success", foreground="#00ff9f")
        self.terminal.tag_config("error", foreground="#ff4f7b")
        self.terminal.tag_config("timestamp", foreground="#404060")

        self._write_terminal(f"Command Manager ready. Double-click or select a command and press ▶ Run.\n", "info")
        self._write_terminal(f"You can also type any shell command in the entry bar above.\n\n", "info")

    def _btn(self, parent, text, cmd, bg="#2a2a4a", fg="#c0c8e0", height=None):
        kw = dict(text=text, command=cmd, bg=bg, fg=fg,
                  activebackground=bg, activeforeground=fg,
                  relief="flat", font=("Courier New", 9, "bold"),
                  cursor="hand2", padx=6)
        if height:
            kw["pady"] = 2
        return tk.Button(parent, **kw)

    # ── List Management ───────────────────────────────────────────────────

    def _refresh_list(self, select_index=None):
        self.listbox.delete(0, "end")
        for c in self.commands:
            self.listbox.insert("end", f"  {c['name']}")
        if select_index is not None and 0 <= select_index < len(self.commands):
            self.listbox.selection_set(select_index)
            self.listbox.activate(select_index)
            self._on_select()

    def _selected_index(self):
        sel = self.listbox.curselection()
        return sel[0] if sel else None

    def _on_select(self, event=None):
        idx = self._selected_index()
        if idx is not None:
            c = self.commands[idx]
            desc = c.get("description", "")
            self.detail_var.set(f"$ {c['command']}" + (f"\n{desc}" if desc else ""))
        else:
            self.detail_var.set("")

    # ── CRUD ──────────────────────────────────────────────────────────────

    def _add_command(self):
        dlg = CommandDialog(self, "Add Command")
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
        dlg = CommandDialog(self, "Edit Command", c["name"], c["command"], c.get("description", ""))
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

        self.running = True
        self.status_var.set(f"running: {label}")

        thread = threading.Thread(target=self._run_thread, args=(command,), daemon=True)
        thread.start()

    def _run_thread(self, command):
        try:
            self.current_process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )

            # Stream stdout
            for line in self.current_process.stdout:
                self._write_terminal(line, "stdout")

            # Stream stderr
            for line in self.current_process.stderr:
                self._write_terminal(line, "stderr")

            retcode = self.current_process.wait()

            if retcode == 0:
                self._write_terminal(f"\n✓ Exited with code {retcode}\n", "success")
            else:
                self._write_terminal(f"\n✗ Exited with code {retcode}\n", "error")

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
                self._write_terminal("\n⏹ Process killed.\n", "error")
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
        default_name = f"terminal_output_{ts}.txt"
        path = filedialog.asksaveasfilename(
            title="Save Terminal Output",
            initialfile=default_name,
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("Log files", "*.log"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            self._write_terminal(f"\n💾 Output saved to: {path}\n", "success")
        except IOError as e:
            messagebox.showerror("Save Failed", f"Could not save file:\n{e}")

    def _clear_terminal(self):
        self.terminal.config(state="normal")
        self.terminal.delete("1.0", "end")
        self.terminal.config(state="disabled")
        self._write_terminal("Terminal cleared.\n\n", "info")


# ─── Entry Point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = CommandManagerApp()
    app.mainloop()
