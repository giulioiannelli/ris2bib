"""
Simple cross-platform Tkinter GUI for RIS → BibTeX conversion.
"""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import List

from .core import convert_files


class Ris2BibApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("RIS to BibTeX")
        self.geometry("900x600")

        self.selected_files: List[str] = []
        self.status_var = tk.StringVar(value="Select one or more .ris files to convert.")
        self.files_var = tk.StringVar(value="No files selected.")

        self._build_ui()

    def _build_ui(self) -> None:
        padding = {"padx": 10, "pady": 8}

        header = ttk.Label(self, text="RIS → BibTeX Converter", font=("Arial", 16, "bold"))
        header.grid(row=0, column=0, sticky="w", **padding)

        file_frame = ttk.Frame(self)
        file_frame.grid(row=1, column=0, sticky="ew", **padding)
        file_frame.columnconfigure(1, weight=1)

        ttk.Label(file_frame, text="Selected files:").grid(row=0, column=0, sticky="nw", padx=(0, 8))
        files_label = ttk.Label(file_frame, textvariable=self.files_var, justify="left", relief="groove")
        files_label.grid(row=0, column=1, sticky="ew")

        button_frame = ttk.Frame(self)
        button_frame.grid(row=2, column=0, sticky="w", **padding)

        ttk.Button(button_frame, text="Choose RIS files…", command=self._choose_files).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(button_frame, text="Convert", command=self._convert).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(button_frame, text="Save output…", command=self._save_output).grid(row=0, column=2)

        output_frame = ttk.Frame(self)
        output_frame.grid(row=3, column=0, sticky="nsew", **padding)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)

        ttk.Label(output_frame, text="BibTeX output:").grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.output_text = tk.Text(output_frame, wrap="word", font=("Consolas", 11))
        self.output_text.grid(row=1, column=0, sticky="nsew")

        scroll = ttk.Scrollbar(output_frame, orient="vertical", command=self.output_text.yview)
        scroll.grid(row=1, column=1, sticky="ns")
        self.output_text.configure(yscrollcommand=scroll.set)

        status_bar = ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.grid(row=4, column=0, sticky="ew", **padding)

        self.rowconfigure(3, weight=1)
        self.columnconfigure(0, weight=1)

    def _choose_files(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Select RIS files",
            filetypes=[("RIS files", "*.ris"), ("All files", "*.*")],
        )
        if paths:
            self.selected_files = list(paths)
            preview = "\n".join(self.selected_files)
            self.files_var.set(preview)
            self.status_var.set(f"{len(self.selected_files)} file(s) selected.")

    def _convert(self) -> None:
        if not self.selected_files:
            messagebox.showwarning("No files", "Please select one or more .ris files first.")
            return

        warnings: List[str] = []

        def warn(message: str) -> None:
            warnings.append(message)

        try:
            bib_text = convert_files(self.selected_files, on_warning=warn)
        except ValueError as exc:
            messagebox.showerror("Conversion failed", str(exc))
            self.status_var.set("Conversion failed.")
            return

        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, bib_text)

        status = "Conversion complete."
        if warnings:
            status += f" {len(warnings)} warning(s)."
            messagebox.showwarning("Conversion warnings", "\n".join(warnings))
        self.status_var.set(status)

    def _save_output(self) -> None:
        content = self.output_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showinfo("No output", "Run a conversion first, then save the BibTeX output.")
            return

        path = filedialog.asksaveasfilename(
            title="Save BibTeX output",
            defaultextension=".bib",
            filetypes=[("BibTeX files", "*.bib"), ("All files", "*.*")],
        )
        if not path:
            return

        Path(path).write_text(content + "\n", encoding="utf-8")
        self.status_var.set(f"Saved BibTeX to {path}")


def main() -> None:
    app = Ris2BibApp()
    app.mainloop()


if __name__ == "__main__":
    main()
