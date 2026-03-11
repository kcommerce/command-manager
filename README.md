# Command Manager

A lightweight desktop GUI for organising and running terminal commands — built with Python and Tkinter. Commands are grouped into folders, persisted in a local `commands.json` file, and the app requires no third-party dependencies to run.

---


## Layout

```
┌──────────────────────────────────────────────────────────────────────────┐
│ COMMAND MANAGER          cwd: ~/projects  [Browse]    Theme: [Cyber Night]│
├────────────────────────┬─────────────────────────────────────────────────┤
│ FOLDERS & COMMANDS     │ TERMINAL              Clear   Save   Kill        │
│                        │                                                  │
│ > System  (3)          │ dir: ~/projects                                  │
│     List Files         │                                                  │
│     System Info        │ [10:42:01] $ ls -la                              │
│     Disk Usage         │     in: ~/projects                               │
│ > Navigation  (2)      │ total 48                                         │
│     Current Dir        │ drwxr-xr-x  6 user staff  192 Mar 11 ...        │
│     Date & Time        │                                                  │
│                        │ [exit 0]                                         │
│ Folder: System (3 cmds)├─────────────────────────────────────────────────┤
│                        │ $  [ls -la                              ] > Run  │
│ FOLDER: +New *Rename xDel                                                 │
│ CMD:    +Add *Edit xDel >Move >>Run                                       │
└────────────────────────┴─────────────────────────────────────────────────┘
```

---

## Features

- **Folder organisation** — group commands into named folders; add, rename, and delete folders freely
- **Collapsible tree** — folders expand and collapse; command count shown per folder
- **Move commands** — reassign any command to a different folder via a dedicated Move dialog
- **Click to load** — selecting a command populates the entry bar so you can tweak it before running
- **Double-click to run** — execute a command immediately without touching the keyboard
- **Live terminal output** — stdout and stderr streamed in real time with colour coding
- **Ad-hoc commands** — type any shell command in the `$` entry bar without saving it first
- **Working directory** — change the `cwd` for all executed commands via the header Browse button
- **Kill process** — terminate a running command instantly
- **Save output** — export the full terminal session to a `.txt` or `.log` file
- **Clear terminal** — wipe the output pane in one click
- **5 built-in themes** — switch palette live from the header dropdown
- **Persistent storage** — all data auto-saves to `commands.json` alongside the script
- **Auto-migration** — old flat `commands.json` files are automatically promoted into a "Default" folder
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

On first launch, `commands.json` is created automatically with two example folders and five commands.

---

## File Structure

```
command-manager/
├── command_manager.py   # Main application
├── build.py             # Cross-platform build script
├── commands.json        # Auto-generated — your saved folders and commands
├── icon.icns            # Optional — macOS app icon
├── icon.ico             # Optional — Windows app icon
├── icon.png             # Optional — Linux app icon
└── README.md
```

---

## commands.json Format

Commands are stored in a JSON array of folder objects. You can edit the file directly if needed.

```json
[
  {
    "id": "a1b2c3d4-...",
    "name": "System",
    "commands": [
      {
        "id": "e5f6a7b8-...",
        "name": "List Files",
        "command": "ls -la",
        "description": "List all files in current directory"
      },
      {
        "id": "c9d0e1f2-...",
        "name": "Disk Usage",
        "command": "df -h",
        "description": "Show disk usage"
      }
    ]
  }
]
```

### Folder fields

| Field | Required | Description |
|---|---|---|
| `id` | Auto | UUID assigned automatically — do not edit |
| `name` | Yes | Folder label shown in the tree |
| `commands` | Yes | Array of command objects (can be empty) |

### Command fields

| Field | Required | Description |
|---|---|---|
| `id` | Auto | UUID assigned automatically — do not edit |
| `name` | Yes | Label shown in the tree |
| `command` | Yes | Shell command to execute |
| `description` | No | Optional note shown in the detail area |

---

## Themes

Switch theme any time from the dropdown in the header. The change is instant and affects every widget including dialogs.

| Theme | Style |
|---|---|
| **Cyber Night** | Deep navy with cyan and green neon accents (default) |
| **Solarized Dark** | Classic Solarized dark palette |
| **Light Mint** | Light background with green and blue accents |
| **Monokai** | Warm olive dark with pink and green highlights |
| **Nord** | Arctic blue-grey tones |

---

## Usage Guide

### Managing Folders

| Action | How |
|---|---|
| Create a folder | Click **+ New** in the FOLDER toolbar, enter a name |
| Rename a folder | Select any item in the folder, click **\* Rename** |
| Delete a folder | Select any item in the folder, click **x Delete**, confirm |

> Deleting a folder removes all commands inside it. You must have at least one folder at all times.

### Managing Commands

| Action | How |
|---|---|
| Add a command | Click **+ Add** — choose the destination folder from the dropdown in the dialog |
| Edit a command | Select a command, click **\* Edit** — you can also change its folder here |
| Remove a command | Select a command, click **x Del**, confirm |
| Move to another folder | Select a command, click **> Move**, pick the destination folder |
| Load into entry bar | Single-click any command — its text appears in the `$` bar ready to edit |
| Run a saved command | Select it and click **>> Run**, or double-click it in the tree |

### Terminal

| Action | How |
|---|---|
| Change working directory | Click the path or **Browse** in the header |
| Run an ad-hoc command | Type in the `$` entry bar and press **Enter** or **> Run** |
| Kill a running process | Click **Kill** in the terminal header |
| Save terminal output | Click **Save**, choose a filename and location |
| Clear the terminal | Click **Clear** |

---

## Building a Standalone Executable

Use `build.py` to package the app into a native executable. The script auto-detects macOS, Windows, or Linux.

### 1. Install PyInstaller

```bash
pip install pyinstaller
```

### 2. Run the build

```bash
# Directory bundle (default)
python build.py

# Single self-contained executable
python build.py --onefile

# Single file, remove build/ and .spec after packaging
python build.py --onefile --clean

# Keep the console window visible (Windows debugging)
python build.py --debug
```

### 3. Find your executable

| Platform | Default output | With --onefile |
|---|---|---|
| macOS | `dist/CommandManager.app` | `dist/CommandManager` |
| Windows | `dist\CommandManager\CommandManager.exe` | `dist\CommandManager.exe` |
| Linux | `dist/CommandManager/CommandManager` | `dist/CommandManager` |

### Optional Icons

Place any of these files in the project root before building — the script picks them up automatically:

| File | Platform |
|---|---|
| `icon.icns` | macOS |
| `icon.ico` | Windows |
| `icon.png` | Linux |

---

## GitHub Actions CI/CD

The included `.github/workflows/build.yml` builds all three platform executables in parallel and publishes them as a GitHub Release whenever you push a version tag.

```bash
git tag v1.0.0
git push origin v1.0.0   # triggers the pipeline
```

See `GITHUB_ACTIONS_SETUP.md` for the full setup walkthrough.

---

## Platform Notes

### macOS
- Tkinter is bundled with the official Python installer from [python.org](https://python.org). The Homebrew version may require `brew install python-tk`.
- The `.app` bundle produced by `build.py` can be dragged to `/Applications`.

### Windows
- Tkinter ships with the standard Python installer. No extra steps needed.
- Use `build.py --onefile` for a portable single `.exe` with no installer required.
- The build pipeline sets `PYTHONUTF8=1` to avoid `cp1252` encoding errors on Windows runners.

### Linux
- Install `python3-tk` via your package manager (see Requirements above).
- The built binary is fully self-contained and can be distributed without Python installed on the target machine.

---

## License

MIT — free to use, modify, and distribute.
