# Bulk PDF to MD Creator

Desktop app to batch-convert every PDF in a folder into Markdown files.

## Setup

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
2. Set the output subfolder name (default: `markdown`).
3. Choose whether to include subfolders and whether to mirror the folder
   structure in the output.
4. Click **Convert All PDFs**.

Converted `.md` files are written into a new subfolder inside the selected
folder (default name: `markdown`). That output subfolder is automatically
skipped on re-runs so it's never scanned as a source.

## Run (CLI, for scripting/automation)

```bash
python cli.py /path/to/folder --output-name markdown
```

Options:
- `--no-recursive` — only convert top-level PDFs, skip subfolders.
- `--flatten` — put all `.md` files directly in the output folder instead of
  mirroring the source subfolder structure.

Exit code is `0` if all files converted, `1` if any failed (see console log
for per-file errors).

## Notes

- Conversion uses `pymupdf4llm`, which extracts text, tables, and basic
  layout into Markdown. Scanned/image-only PDFs (no embedded text layer)
  will produce empty or near-empty output — OCR is not included.
- Failed files are logged individually and do not stop the batch.
