# ⚡ Command Manager

A lightweight desktop GUI for saving, managing, and running terminal commands — built with Python and Tkinter. No third-party dependencies required to run. Commands are persisted in a local `commands.json` file.

---

## Screenshots

```
┌─────────────────────────────────────────────────────────────────┐
│ ⚡ COMMAND MANAGER                                               │
├──────────────────┬──────────────────────────────────────────────┤
│  COMMANDS        │ ● TERMINAL          Clear  💾 Save  ⏹ Kill   │
│                  │                                              │
│  List Files      │ $ ls -la                                     │
│  System Info     │ total 48                                     │
│  Disk Usage      │ drwxr-xr-x  6 user  staff   192 Mar 11 ...  │
│  Current Dir     │                                              │
│  Date & Time     │ ✓ Exited with code 0                        │
│                  ├──────────────────────────────────────────────┤
│ $ ls -la         │ $  [type any command here]          ▶ Run   │
│ ＋Add  ✎Edit     │                                              │
│ ✕Remove ▶Run     │                                              │
└──────────────────┴──────────────────────────────────────────────┘
```

---

## Features

- **Command library** — save shell commands with a name and optional description
- **Add / Edit / Remove** — full CRUD via modal dialogs
- **Live terminal output** — stdout and stderr streamed in real time with colour coding
- **Ad-hoc commands** — type any shell command in the entry bar without saving it first
- **Kill process** — terminate a running command instantly
- **Save output** — export the full terminal session to a `.txt` or `.log` file with a timestamped default filename
- **Clear terminal** — wipe the output pane in one click
- **Persistent storage** — commands auto-save to `commands.json` alongside the script
- **Zero extra dependencies** — uses only Python standard library modules

---

## Requirements

| Requirement | Version |
|---|---|
| Python | 3.10 or newer |
| Tkinter | Included with Python (see notes below) |

> **Linux note:** Tkinter may need to be installed separately.
> ```bash
> # Debian / Ubuntu
> sudo apt install python3-tk
>
> # Fedora / RHEL
> sudo dnf install python3-tkinter
>
> # Arch
> sudo pacman -S tk
> ```

---

## Running from Source

```bash
# 1. Clone or download the files
git clone https://github.com/yourname/command-manager.git
cd command-manager

# 2. Run directly — no pip install needed
python3 command_manager.py
```

On first launch, `commands.json` is created automatically with five example commands.

---

## File Structure

```
command-manager/
├── command_manager.py   # Main application
├── build.py             # Cross-platform build script
├── commands.json        # Auto-generated — your saved commands
├── icon.icns            # Optional — macOS app icon
├── icon.ico             # Optional — Windows app icon
├── icon.png             # Optional — Linux app icon
└── README.md
```

---

## commands.json Format

Commands are stored as a JSON array. You can edit the file directly if needed.

```json
[
  {
    "name": "List Files",
    "command": "ls -la",
    "description": "List all files in current directory"
  },
  {
    "name": "Disk Usage",
    "command": "df -h",
    "description": "Show disk usage"
  }
]
```

| Field | Required | Description |
|---|---|---|
| `name` | ✅ | Label shown in the command list |
| `command` | ✅ | Shell command to execute |
| `description` | ✗ | Optional note shown below the list |

---

## Building a Standalone Executable

Use `build.py` to package the app into a native executable for your platform. The build script auto-detects macOS, Windows, or Linux.

### 1. Install PyInstaller

```bash
pip install pyinstaller
```

### 2. Run the build

```bash
# Default — creates a dist/CommandManager/ directory bundle
python build.py

# Single self-contained executable
python build.py --onefile

# Single file, remove build/ and .spec after packaging
python build.py --onefile --clean

# Keep the console window visible (useful on Windows for debugging)
python build.py --debug
```

### 3. Find your executable

| Platform | Default output |
|---|---|
| macOS | `dist/CommandManager.app` |
| Windows | `dist\CommandManager\CommandManager.exe` |
| Linux | `dist/CommandManager/CommandManager` |

With `--onefile`:

| Platform | Output |
|---|---|
| macOS | `dist/CommandManager` |
| Windows | `dist\CommandManager.exe` |
| Linux | `dist/CommandManager` |

### Optional Icons

Drop any of these files into the project root before building and the script picks them up automatically:

| File | Platform |
|---|---|
| `icon.icns` | macOS |
| `icon.ico` | Windows |
| `icon.png` | Linux |

---

## Usage Guide

### Managing Commands

| Action | How |
|---|---|
| Add a command | Click **＋ Add**, fill in Name and Command, click Save |
| Edit a command | Select it in the list, click **✎ Edit** |
| Remove a command | Select it in the list, click **✕ Remove**, confirm |
| Run a saved command | Select it and click **▶ Run**, or double-click it |

### Terminal

| Action | How |
|---|---|
| Run an ad-hoc command | Type in the `$` entry bar and press **Enter** or **▶ Run** |
| Kill a running process | Click **⏹ Kill** |
| Save terminal output | Click **💾 Save**, choose a filename and location |
| Clear the terminal | Click **Clear** |

---

## Platform Notes

### macOS
- Tkinter is bundled with the official Python installer from [python.org](https://python.org). The Homebrew version may require `brew install python-tk`.
- The `.app` bundle produced by `build.py` can be dragged to `/Applications`.

### Windows
- Tkinter ships with the standard Python installer from [python.org](https://python.org). No extra steps needed.
- Use `build.py --onefile` for a portable single `.exe` with no installer required.

### Linux
- Install `python3-tk` via your package manager (see Requirements above).
- The built binary is fully self-contained and can be distributed without Python installed on the target machine.

---

## License

MIT — free to use, modify, and distribute.
