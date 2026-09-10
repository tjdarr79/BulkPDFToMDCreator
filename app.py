"""Bulk PDF -> Markdown Creator: desktop GUI.

Select a folder; every PDF in it (and optionally its subfolders) is
converted to a .md file placed in a new "markdown" subfolder.
"""
from __future__ import annotations

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from pdf_to_md import ConversionResult, convert_folder, find_pdfs

APP_TITLE = "Bulk PDF to MD Creator"
ASSETS_DIR = Path(__file__).resolve().parent / "assets"


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("640x480")
        self.minsize(560, 400)
        self._set_window_icon()

        self.source_folder = tk.StringVar()
        self.output_subfolder = tk.StringVar(value="markdown")
        self.recursive = tk.BooleanVar(value=True)
        self.preserve_structure = tk.BooleanVar(value=True)
        self.delete_source = tk.BooleanVar(value=True)
        self.status_text = tk.StringVar(value="Select a folder to begin.")

        self._queue: queue.Queue = queue.Queue()
        self._worker: threading.Thread | None = None

        self._build_ui()
        self.after(100, self._poll_queue)

    def _build_ui(self) -> None:
        pad = {"padx": 10, "pady": 6}

        folder_frame = ttk.Frame(self)
        folder_frame.pack(fill="x", **pad)

        ttk.Label(folder_frame, text="Source folder:").pack(side="left")
        entry = ttk.Entry(folder_frame, textvariable=self.source_folder)
        entry.pack(side="left", fill="x", expand=True, padx=(6, 6))
        ttk.Button(folder_frame, text="Browse...", command=self._browse_folder).pack(side="left")
        ttk.Button(folder_frame, text="Refresh", command=self._refresh).pack(side="left", padx=(6, 0))

        options_frame = ttk.Frame(self)
        options_frame.pack(fill="x", **pad)

        ttk.Label(options_frame, text="Output subfolder name:").pack(side="left")
        ttk.Entry(options_frame, textvariable=self.output_subfolder, width=20).pack(
            side="left", padx=(6, 20)
        )
        ttk.Checkbutton(
            options_frame, text="Include subfolders", variable=self.recursive
        ).pack(side="left", padx=(0, 20))
        ttk.Checkbutton(
            options_frame,
            text="Preserve folder structure in output",
            variable=self.preserve_structure,
        ).pack(side="left", padx=(0, 20))
        ttk.Checkbutton(
            options_frame,
            text="Delete original PDF after conversion",
            variable=self.delete_source,
        ).pack(side="left")

        action_frame = ttk.Frame(self)
        action_frame.pack(fill="x", **pad)
        self.convert_button = ttk.Button(
            action_frame, text="Convert All PDFs", command=self._start_conversion
        )
        self.convert_button.pack(side="left")
        self.progress = ttk.Progressbar(action_frame, mode="determinate")
        self.progress.pack(side="left", fill="x", expand=True, padx=(10, 0))

        ttk.Label(self, textvariable=self.status_text).pack(fill="x", padx=10)

        log_frame = ttk.Frame(self)
        log_frame.pack(fill="both", expand=True, **pad)
        self.log = tk.Text(log_frame, height=15, state="disabled", wrap="word")
        scrollbar = ttk.Scrollbar(log_frame, command=self.log.yview)
        self.log.configure(yscrollcommand=scrollbar.set)
        self.log.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _set_window_icon(self) -> None:
        ico_path = ASSETS_DIR / "icon.ico"
        png_path = ASSETS_DIR / "icon.png"
        if ico_path.exists():
            try:
                self.iconbitmap(str(ico_path))
                return
            except tk.TclError:
                pass  # .ico icons aren't supported by Tk on this platform (e.g. Linux)
        if png_path.exists():
            try:
                self.iconphoto(True, tk.PhotoImage(file=str(png_path)))
            except tk.TclError:
                pass

    def _browse_folder(self) -> None:
        folder = filedialog.askdirectory(title="Select folder containing PDFs")
        if folder:
            self.source_folder.set(folder)
            self._refresh_pdf_count(folder)

    def _refresh(self) -> None:
        folder = self.source_folder.get().strip()
        if not folder or not Path(folder).is_dir():
            messagebox.showerror(APP_TITLE, "Please select a valid folder first.")
            return
        self._refresh_pdf_count(folder)

    def _refresh_pdf_count(self, folder: str) -> None:
        try:
            count = len(find_pdfs(Path(folder), self.recursive.get()))
            self.status_text.set(f"{count} PDF(s) found in selected folder.")
        except Exception:
            pass

    def _log(self, message: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", message + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _start_conversion(self) -> None:
        if self._worker and self._worker.is_alive():
            return

        folder = self.source_folder.get().strip()
        if not folder or not Path(folder).is_dir():
            messagebox.showerror(APP_TITLE, "Please select a valid folder first.")
            return

        subfolder_name = self.output_subfolder.get().strip() or "markdown"

        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")
        self.progress.configure(value=0, maximum=100)
        self.convert_button.configure(state="disabled")
        self.status_text.set("Converting...")

        self._worker = threading.Thread(
            target=self._run_conversion,
            args=(
                folder,
                subfolder_name,
                self.recursive.get(),
                self.preserve_structure.get(),
                self.delete_source.get(),
            ),
            daemon=True,
        )
        self._worker.start()

    def _run_conversion(
        self,
        folder: str,
        subfolder_name: str,
        recursive: bool,
        preserve_structure: bool,
        delete_source: bool,
    ) -> None:
        def on_progress(done: int, total: int, result: ConversionResult) -> None:
            self._queue.put(("progress", done, total, result))

        try:
            output_root, results = convert_folder(
                folder,
                output_subfolder_name=subfolder_name,
                recursive=recursive,
                preserve_structure=preserve_structure,
                delete_source=delete_source,
                progress_callback=on_progress,
            )
            self._queue.put(("done", output_root, results))
        except Exception as exc:  # noqa: BLE001
            self._queue.put(("error", str(exc)))

    def _poll_queue(self) -> None:
        try:
            while True:
                item = self._queue.get_nowait()
                kind = item[0]
                if kind == "progress":
                    _, done, total, result = item
                    self.progress.configure(maximum=max(total, 1), value=done)
                    if result.ok:
                        msg = f"[OK] {result.source.name} -> {result.output.name}"
                        if result.deleted_source:
                            msg += " (original PDF deleted)"
                        elif result.delete_error:
                            msg += f" (could not delete original: {result.delete_error})"
                        self._log(msg)
                    else:
                        self._log(f"[FAIL] {result.source.name}: {result.error}")
                    self.status_text.set(f"Converting... ({done}/{total})")
                elif kind == "done":
                    _, output_root, results = item
                    ok_count = sum(1 for r in results if r.ok)
                    fail_count = len(results) - ok_count
                    self.status_text.set(
                        f"Done: {ok_count} converted, {fail_count} failed. "
                        f"Output: {output_root}"
                    )
                    self.convert_button.configure(state="normal")
                    if not results:
                        messagebox.showinfo(APP_TITLE, "No PDF files found in the selected folder.")
                elif kind == "error":
                    self.status_text.set("Error.")
                    self.convert_button.configure(state="normal")
                    messagebox.showerror(APP_TITLE, item[1])
        except queue.Empty:
            pass
        self.after(100, self._poll_queue)


if __name__ == "__main__":
    App().mainloop()
