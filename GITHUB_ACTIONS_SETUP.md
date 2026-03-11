# GitHub Actions CI/CD Setup Guide

Build and release **Command Manager** for macOS, Windows, and Linux automatically using GitHub Actions.

---

## How It Works

Every time you push a version tag (e.g. `v1.0.0`), the pipeline:

1. Spins up **three parallel runners** — macOS, Windows, Ubuntu
2. Installs Python 3.12 and PyInstaller on each
3. Runs `build.py --onefile --clean` to produce a single native executable
4. Uploads all three binaries to a **GitHub Release** automatically

You can also trigger a build manually from the GitHub Actions UI at any time.

```
git push origin v1.0.0
        │
        ├─► Runner: macos-latest   → CommandManager-macOS
        ├─► Runner: windows-latest → CommandManager-Windows.exe
        └─► Runner: ubuntu-latest  → CommandManager-Linux
                │
                └─► GitHub Release v1.0.0 (all 3 files attached)
```

---

## Step-by-Step Setup

### Step 1 — Create a GitHub Repository

Go to [github.com/new](https://github.com/new) and create a new repository,
or use an existing one.

### Step 2 — Add Your Project Files

Your repository should contain these files at the root:

```
your-repo/
├── .github/
│   └── workflows/
│       └── build.yml          ← the workflow file
├── command_manager.py
├── build.py
├── icon.icns                  ← optional
├── icon.ico                   ← optional
├── icon.png                   ← optional
└── README.md
```

### Step 3 — Push the Workflow File

```bash
# If starting fresh
git init
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Add all files
git add .
git commit -m "Initial commit"
git push origin main
```

### Step 4 — Trigger a Build by Pushing a Tag

```bash
# Tag the current commit with a version number
git tag v1.0.0

# Push the tag — this triggers the pipeline
git push origin v1.0.0
```

That's it. GitHub Actions takes over from here.

### Step 5 — Watch the Build

1. Go to your repository on GitHub
2. Click the **Actions** tab
3. You'll see **"Build Command Manager"** running across all three platforms
4. Each job takes roughly 2–4 minutes

### Step 6 — Download the Release

Once all jobs succeed:

1. Click the **Releases** section on your repo's main page (right sidebar)
2. Find the release tagged `v1.0.0`
3. Download the binary for your platform:
   - `CommandManager-macOS`
   - `CommandManager-Windows.exe`
   - `CommandManager-Linux`

---

## Manual Trigger (No Tag Required)

To build without creating a release tag:

1. Go to **Actions** → **Build Command Manager**
2. Click **"Run workflow"** (top right)
3. Select branch and click **Run workflow**

Artifacts are available for download under the workflow run for 90 days.

---

## Workflow File Reference

```
.github/workflows/build.yml
```

| Setting | Value | Notes |
|---|---|---|
| Trigger | `push` to `v*` tags | e.g. `v1.0.0`, `v2.1.3` |
| Trigger | `workflow_dispatch` | Manual trigger from UI |
| macOS runner | `macos-latest` | Currently macOS 14 Sonoma |
| Windows runner | `windows-latest` | Currently Windows Server 2022 |
| Linux runner | `ubuntu-latest` | Currently Ubuntu 22.04 |
| Python version | `3.12` | Set in `setup-python` step |
| Build mode | `--onefile` | Single self-contained binary |

---

## Versioning Convention

Use standard semantic versioning for tags:

```bash
git tag v1.0.0   # first stable release
git tag v1.1.0   # new features
git tag v1.1.1   # bug fix
git tag v2.0.0   # breaking change
```

Push a tag to trigger a release:

```bash
git tag v1.2.0 && git push origin v1.2.0
```

Delete a tag if you made a mistake:

```bash
git tag -d v1.2.0                  # delete locally
git push origin --delete v1.2.0    # delete on GitHub
```

---

## Troubleshooting

**Build fails on macOS with Tkinter import error**

Tkinter is included with the `macos-latest` runner's Python. If you see an error, pin a specific Python version:

```yaml
python-version: "3.12.3"
```

**Build fails on Linux with `_tkinter` not found**

The workflow already installs `python3-tk` on Linux. If you've modified the workflow and removed that step, add it back:

```yaml
- name: Install Tkinter (Linux only)
  if: runner.os == 'Linux'
  run: sudo apt-get update && sudo apt-get install -y python3-tk
```

**Release step fails with 403 permission error**

Make sure the workflow has write permissions. The `build.yml` already includes:

```yaml
permissions:
  contents: write
```

If you still get 403, go to **Settings → Actions → General → Workflow permissions** and set it to **"Read and write permissions"**.

**Windows executable triggers antivirus warning**

This is common with PyInstaller-built executables. You can optionally add a code-signing step, or instruct users to click **"More info → Run anyway"** in Windows SmartScreen.

---

## Required Files Checklist

Before pushing your tag, confirm these files exist in your repo root:

- [ ] `command_manager.py`
- [ ] `build.py`
- [ ] `.github/workflows/build.yml`
- [ ] `icon.ico` *(optional but recommended)*
- [ ] `icon.icns` *(optional but recommended)*
- [ ] `icon.png` *(optional but recommended)*
