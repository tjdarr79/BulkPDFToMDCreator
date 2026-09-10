# Bulk PDF to MD Creator

Desktop app to batch-convert every PDF in a folder into Markdown files.

## Windows: one-click install (recommended)

1. Double-click **`install.bat`**.
   - Checks for Python; if missing, installs it via `winget` (you'll be asked
     to re-run `install.bat` once after that finishes, so Windows picks up
     the new PATH entry).
   - Creates a `venv` and installs dependencies into it.
   - Adds a **"Bulk PDF to MD Creator"** shortcut to your Desktop, using the
     icon in `assets/icon.ico`.
2. Double-click the new Desktop shortcut any time to launch the app (no
   console window).

Re-running `install.bat` later is safe — it skips steps that are already done
and just re-creates the shortcut.

## Manual setup (any OS)

```bash
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Tkinter is required for the GUI. It ships with the standard Windows/macOS
Python installers. On Linux, install it via your package manager if missing,
e.g. `sudo apt install python3-tk`.

## Run (GUI)

```bash
python app.py
```

1. Click **Browse...** and select the folder containing your PDFs.
2. Click **Refresh** any time to re-scan that folder and update the PDF
   count shown at the bottom (e.g. after adding more files).
3. Set the output subfolder name (default: `markdown`).
4. Choose whether to include subfolders, whether to mirror the folder
   structure in the output, and whether to delete each original PDF once
   it's been converted (**on by default** — uncheck to keep the PDFs).
5. Click **Convert All PDFs**.

Converted `.md` files are written into a new subfolder inside the selected
folder (default name: `markdown`). That output subfolder is automatically
skipped on re-runs so it's never scanned as a source. A PDF is only deleted
after its `.md` file has been written successfully — a failed conversion
always leaves the original PDF in place.

## Run (CLI, for scripting/automation)

```bash
python cli.py /path/to/folder --output-name markdown
```

Options:
- `--no-recursive` — only convert top-level PDFs, skip subfolders.
- `--flatten` — put all `.md` files directly in the output folder instead of
  mirroring the source subfolder structure.
- `--delete-source` — delete each PDF after it converts successfully (off by
  default on the CLI; the GUI defaults this on).

Exit code is `0` if all files converted, `1` if any failed (see console log
for per-file errors).

## Notes

- Conversion uses `pymupdf4llm`, which extracts text, tables, and basic
  layout into Markdown. Scanned/image-only PDFs (no embedded text layer)
  will produce empty or near-empty output — OCR is not included.
- Failed files are logged individually and do not stop the batch.
- Deleting the original PDF is permanent (no recycle bin/trash) — leave the
  "Delete original PDF" box unchecked (GUI) or omit `--delete-source` (CLI)
  if you want to keep your source files.
