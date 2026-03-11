#!/usr/bin/env python3
"""
build.py — Cross-platform build script for Command Manager
Produces a standalone executable for macOS, Windows, or Linux.

Usage:
    python build.py              # auto-detects current platform
    python build.py --onefile    # single-file bundle (larger, no folder)
    python build.py --debug      # keep console window (Windows)
    python build.py --clean      # remove build artefacts after packaging
    python build.py --help       # show this help

Requirements:
    pip install pyinstaller
"""

import sys
import os
import shutil
import argparse
import subprocess
import platform
import io

# Force UTF-8 output on Windows (cp1252 cannot encode unicode symbols)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ─── Configuration ────────────────────────────────────────────────────────────

APP_NAME        = "CommandManager"
SCRIPT          = "command_manager.py"      # main entry-point
ICON_WIN        = "icon.ico"                # optional – place next to build.py
ICON_MAC        = "icon.icns"               # optional – place next to build.py
ICON_LINUX      = "icon.png"                # optional – place next to build.py
DIST_DIR        = "dist"
BUILD_DIR       = "build"
SPEC_FILE       = f"{APP_NAME}.spec"

# ─── Helpers ──────────────────────────────────────────────────────────────────

def banner(msg: str) -> None:
    width = 60
    print("\n" + "─" * width)
    print(f"  {msg}")
    print("─" * width)


def run(cmd: list[str]) -> None:
    print("$", " ".join(cmd))
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"\n✗ Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)


def check_pyinstaller() -> None:
    banner("Checking PyInstaller")
    try:
        import PyInstaller  # noqa: F401
        import importlib.metadata
        ver = importlib.metadata.version("pyinstaller")
        print(f"✓ PyInstaller {ver} found")
    except ImportError:
        print("PyInstaller not found — installing…")
        run([sys.executable, "-m", "pip", "install", "pyinstaller"])


def check_source() -> None:
    if not os.path.isfile(SCRIPT):
        print(f"\n✗ Source file '{SCRIPT}' not found.")
        print(f"  Make sure build.py and {SCRIPT} are in the same directory.")
        sys.exit(1)
    print(f"✓ Source file found: {SCRIPT}")


def resolve_icon(system: str) -> str | None:
    mapping = {
        "Darwin":  ICON_MAC,
        "Windows": ICON_WIN,
        "Linux":   ICON_LINUX,
    }
    icon_file = mapping.get(system)
    if icon_file and os.path.isfile(icon_file):
        print(f"✓ Icon found: {icon_file}")
        return icon_file
    print(f"  (no icon file found — building without one)")
    return None


def clean_artefacts() -> None:
    banner("Cleaning build artefacts")
    for path in [BUILD_DIR, SPEC_FILE]:
        if os.path.isdir(path):
            shutil.rmtree(path)
            print(f"  removed directory: {path}")
        elif os.path.isfile(path):
            os.remove(path)
            print(f"  removed file:      {path}")
    print("✓ Clean complete")


# ─── Build ────────────────────────────────────────────────────────────────────

def build(onefile: bool, debug: bool, system: str) -> None:
    banner(f"Building for {system}")

    icon = resolve_icon(system)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", APP_NAME,
        "--distpath", DIST_DIR,
        "--workpath", BUILD_DIR,
        "--noconfirm",
    ]

    # Single-file vs directory bundle
    if onefile:
        cmd.append("--onefile")
        print("  Mode: single-file bundle")
    else:
        cmd.append("--onedir")
        print("  Mode: one-directory bundle")

    # Hide console on Windows unless debug mode
    if system == "Windows" and not debug:
        cmd.append("--noconsole")

    # macOS: build a proper .app bundle
    if system == "Darwin":
        cmd.append("--windowed")

    # Icon
    if icon:
        cmd += ["--icon", icon]

    # Hidden imports that tkinter sometimes needs
    cmd += [
        "--hidden-import", "tkinter",
        "--hidden-import", "tkinter.filedialog",
        "--hidden-import", "tkinter.messagebox",
        "--hidden-import", "tkinter.simpledialog",
    ]

    # Entry-point script
    cmd.append(SCRIPT)

    run(cmd)


# ─── Post-build info ─────────────────────────────────────────────────────────

def report(onefile: bool, system: str) -> None:
    banner("Build complete ✓")

    if onefile:
        ext = ".exe" if system == "Windows" else ""
        exe = os.path.join(DIST_DIR, APP_NAME + ext)
        print(f"  Executable : {exe}")
    else:
        app_dir = os.path.join(DIST_DIR, APP_NAME)
        if system == "Darwin":
            app_dir = os.path.join(DIST_DIR, APP_NAME + ".app")
        print(f"  Bundle dir : {app_dir}")

    print(f"\n  To run:")
    if system == "Windows":
        if onefile:
            print(f"    dist\\{APP_NAME}.exe")
        else:
            print(f"    dist\\{APP_NAME}\\{APP_NAME}.exe")
    elif system == "Darwin":
        if onefile:
            print(f"    open dist/{APP_NAME}")
        else:
            print(f"    open dist/{APP_NAME}.app")
    else:
        if onefile:
            print(f"    ./dist/{APP_NAME}")
        else:
            print(f"    ./dist/{APP_NAME}/{APP_NAME}")

    print()


# ─── Entry point ─────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build Command Manager into a standalone executable.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--onefile", action="store_true",
        help="Pack everything into a single executable file"
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Keep the console window visible (Windows only)"
    )
    parser.add_argument(
        "--clean", action="store_true",
        help="Remove build/ and .spec file after packaging"
    )
    args = parser.parse_args()

    system = platform.system()   # 'Darwin' | 'Windows' | 'Linux'

    print(f"\n[**] Command Manager -- Build Script")
    print(f"   Platform : {system} {platform.machine()}")
    print(f"   Python   : {sys.version.split()[0]}")
    print(f"   Mode     : {'single-file' if args.onefile else 'directory bundle'}")

    check_pyinstaller()
    check_source()
    build(onefile=args.onefile, debug=args.debug, system=system)

    if args.clean:
        clean_artefacts()

    report(onefile=args.onefile, system=system)


if __name__ == "__main__":
    main()
