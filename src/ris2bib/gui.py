"""
Soft, drag-and-drop capable GUI for RIS ↔ BibTeX conversion.
"""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Iterable, List, Sequence
import os

from .bib import convert_bib_files, rekey_bib_files
from .core import convert_files

try:  # Optional drag-and-drop (tkinterdnd2)
    from tkinterdnd2 import DND_FILES, TkinterDnD  # type: ignore
except Exception:  # pragma: no cover
    TkinterDnD = None
    DND_FILES = None


BG = "#f5f7fb"
CARD = "#ffffff"
ACCENT = "#5b8def"
TEXT = "#1f2a44"
MUTED = "#6b7280"
DROP_BG = "#e8ecf8"
DND_WARNING = "Drag-and-drop unavailable. Install tkinterdnd2 or use the file picker."


def detect_format(path: Path) -> str:
    """Return 'ris', 'bib', or 'unknown' based on extension/content."""
    ext = path.suffix.lower()
    if ext == ".ris":
        return "ris"
    if ext == ".bib":
        return "bib"
    try:
        sample = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return "unknown"
    snippet = sample[:2000].lower()
    if "ty  -" in snippet:
        return "ris"
    if "@" in snippet:
        return "bib"
    return "unknown"


def parse_drop_event(data: str, tk_root: tk.Tk) -> List[Path]:
    paths: List[Path] = []
    try:
        items = tk_root.splitlist(data)
    except Exception:
        items = data.split()
    for item in items:
        cleaned = item.strip("{}")
        if cleaned:
            paths.append(Path(cleaned))
    return paths


class Ris2BibApp(TkinterDnD.Tk if TkinterDnD else tk.Tk):  # type: ignore[misc]
    def __init__(self) -> None:
        super().__init__()
        self.title("ris2bib — RIS ↔ BibTeX")
        self.configure(bg=BG)

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=CARD, relief="flat")
        style.configure("TLabel", background=BG, foreground=TEXT)
        style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), background=BG, foreground=TEXT)
        style.configure("Muted.TLabel", background=BG, foreground=MUTED)
        style.configure("Accent.TButton", background=ACCENT, foreground="white")
        style.map("Accent.TButton", background=[("active", "#4a7bd6")])
        style.configure(
            "Mode.TRadiobutton",
            background=BG,
            foreground=TEXT,
            indicatoron=False,
            padding=(12, 8),
            relief="flat",
        )
        style.map(
            "Mode.TRadiobutton",
            background=[("selected", ACCENT), ("active", "#4a7bd6")],
            foreground=[("selected", "white"), ("active", "white")],
        )

        self.mode_var = tk.StringVar(value="ris_to_bib")
        self.selected_files: List[Path] = []
        self.status_var = tk.StringVar(value="Drop files or choose manually.")
        self.output_label_var = tk.StringVar(value="Output (BibTeX)")
        self.drop_enabled = TkinterDnD is not None

        self._build_ui()
        self._update_mode()
        self.after(50, self._set_initial_size)
        if self.drop_enabled:
            try:
                self.drop_target_register(DND_FILES)  # type: ignore[arg-type]
                self.dnd_bind("<<Drop>>", self._on_drop)  # type: ignore[attr-defined]
            except Exception:
                self.drop_enabled = False
                self.status_var.set("Drag-and-drop unavailable; use Choose Files.")

    def _build_ui(self) -> None:
        main = ttk.Frame(self, padding=18, style="TFrame")
        main.grid(row=0, column=0, sticky="nsew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        header = ttk.Frame(main, style="TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        header.columnconfigure(1, weight=1)

        ttk.Label(header, text="ris2bib", style="Header.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header, text="Convert RIS ↔ BibTeX with a friendly GUI.", style="Muted.TLabel").grid(
            row=1, column=0, sticky="w"
        )

        mode_shell = ttk.Frame(main, style="TFrame")
        mode_shell.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        mode_shell.columnconfigure(0, weight=1)

        mode_frame = ttk.Frame(mode_shell, style="Card.TFrame", padding=8)
        mode_frame.grid(row=0, column=0, sticky="e")
        ttk.Label(mode_frame, text="Conversion mode", background=CARD, foreground=TEXT).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 6)
        )
        ttk.Radiobutton(
            mode_frame,
            text="RIS → BibTeX",
            value="ris_to_bib",
            variable=self.mode_var,
            command=self._update_mode,
            style="Mode.TRadiobutton",
        ).grid(row=1, column=0, padx=(0, 6))
        ttk.Radiobutton(
            mode_frame,
            text="BibTeX → RIS",
            value="bib_to_ris",
            variable=self.mode_var,
            command=self._update_mode,
            style="Mode.TRadiobutton",
        ).grid(row=1, column=1, padx=(6, 0))

        card = ttk.Frame(main, padding=16, style="Card.TFrame")
        card.grid(row=2, column=0, sticky="nsew")
        card.columnconfigure(0, weight=1)
        card.rowconfigure(3, weight=1)

        drop_text = "Drag & drop files here" if self.drop_enabled else "Choose files below"
        self.drop_zone = tk.Label(
            card,
            text=drop_text,
            bg=DROP_BG,
            fg=TEXT,
            relief="groove",
            bd=1,
            padx=12,
            pady=18,
            font=("Segoe UI", 11, "bold"),
        )
        self.drop_zone.grid(row=0, column=0, sticky="ew")
        if self.drop_enabled:
            try:
                self.drop_zone.drop_target_register(DND_FILES)  # type: ignore[attr-defined]
                self.drop_zone.dnd_bind("<<Drop>>", self._on_drop)  # type: ignore[attr-defined]
            except Exception:
                pass
        else:
            ttk.Label(
                card,
                text=DND_WARNING,
                background=CARD,
                foreground=MUTED,
                wraplength=400,
                padding=(0, 6),
            ).grid(row=0, column=0, sticky="w", pady=(6, 0))

        list_frame = ttk.Frame(card, style="Card.TFrame")
        list_frame.grid(row=1, column=0, sticky="ew", pady=(12, 6))
        list_frame.columnconfigure(0, weight=1)
        ttk.Label(list_frame, text="Selected files", background=CARD, foreground=TEXT).grid(
            row=0, column=0, sticky="w"
        )
        self.files_text = tk.Text(
            list_frame,
            height=4,
            wrap="word",
            relief="flat",
            bg=CARD,
            fg=TEXT,
            font=("Segoe UI", 10),
        )
        self.files_text.grid(row=1, column=0, sticky="ew")
        self.files_text.configure(state="disabled")

        buttons = ttk.Frame(card, style="Card.TFrame")
        buttons.grid(row=2, column=0, sticky="ew", pady=(6, 12))
        buttons.columnconfigure(3, weight=1)
        ttk.Button(buttons, text="Choose files…", command=self._choose_files).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(buttons, text="Clear", command=self._clear_files).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(buttons, text="Convert", style="Accent.TButton", command=self._convert).grid(row=0, column=2)
        ttk.Button(buttons, text="Save output…", command=self._save_output).grid(row=0, column=4, padx=(8, 0))

        out_frame = ttk.Frame(card, style="Card.TFrame")
        out_frame.grid(row=3, column=0, sticky="nsew")
        out_frame.columnconfigure(0, weight=1)
        out_frame.rowconfigure(1, weight=1)

        ttk.Label(out_frame, textvariable=self.output_label_var, background=CARD, foreground=TEXT).grid(
            row=0, column=0, sticky="w", pady=(0, 4)
        )
        self.output_text = tk.Text(out_frame, wrap="word", font=("Cascadia Code", 11), bg="#0d1117", fg="#d0d7de")
        self.output_text.configure(height=12)
        self.output_text.grid(row=1, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(out_frame, orient="vertical", command=self.output_text.yview)
        scroll.grid(row=1, column=1, sticky="ns")
        self.output_text.configure(yscrollcommand=scroll.set)

        status_bar = ttk.Label(self, textvariable=self.status_var, relief="flat", background=BG, foreground=MUTED)
        status_bar.grid(row=2, column=0, sticky="ew", padx=18, pady=(8, 12))

        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

    def _set_initial_size(self) -> None:
        """Ensure the window fits the content without clipping on small screens."""
        self.update_idletasks()
        req_w = self.winfo_reqwidth()
        req_h = self.winfo_reqheight()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        width = min(req_w + 40, screen_w - 80)
        height = min(req_h + 40, screen_h - 120)
        self.minsize(min(width, screen_w), min(height, screen_h))
        self.geometry(f"{width}x{height}")

    # --- File handling ---------------------------------------------------

    def _add_files(self, paths: Iterable[Path]) -> None:
        added = 0
        for p in paths:
            if p.exists() and p not in self.selected_files:
                self.selected_files.append(p)
                added += 1
        if added:
            self._refresh_file_list()
            self.status_var.set(f"{len(self.selected_files)} file(s) selected.")

    def _on_drop(self, event) -> None:  # type: ignore[override]
        paths = parse_drop_event(event.data, self)
        self._add_files(paths)

    def _refresh_file_list(self) -> None:
        self.files_text.configure(state="normal")
        self.files_text.delete("1.0", tk.END)
        if self.selected_files:
            display = "\n".join(str(p) for p in self.selected_files)
            self.files_text.insert(tk.END, display)
        else:
            self.files_text.insert(tk.END, "No files selected.")
        self.files_text.configure(state="disabled")

    def _choose_files(self) -> None:
        filetypes = [("RIS/BibTeX", "*.ris *.bib"), ("RIS", "*.ris"), ("BibTeX", "*.bib"), ("All files", "*.*")]
        paths = filedialog.askopenfilenames(title="Select RIS or BibTeX files", filetypes=filetypes)
        if paths:
            self._add_files([Path(p) for p in paths])

    def _clear_files(self) -> None:
        self.selected_files = []
        self._refresh_file_list()
        self.status_var.set("Selection cleared.")

    # --- Conversion ------------------------------------------------------

    def _convert(self) -> None:
        if not self.selected_files:
            messagebox.showwarning("No files", "Please select one or more files first.")
            return

        warnings: List[str] = []

        def warn(message: str) -> None:
            warnings.append(message)

        ris_inputs: List[Path] = []
        bib_inputs: List[Path] = []
        unknown: List[Path] = []

        for path in self.selected_files:
            fmt = detect_format(path)
            if fmt == "ris":
                ris_inputs.append(path)
            elif fmt == "bib":
                bib_inputs.append(path)
            else:
                unknown.append(path)

        output_chunks: List[str] = []
        mode = self.mode_var.get()

        try:
            if mode == "ris_to_bib":
                if ris_inputs:
                    output_chunks.append(convert_files([*ris_inputs], on_warning=warn))
                if bib_inputs:
                    output_chunks.append(rekey_bib_files([*bib_inputs], on_warning=warn))
                self.output_label_var.set("Output (BibTeX)")
            else:  # bib_to_ris
                if bib_inputs:
                    output_chunks.append(convert_bib_files([*bib_inputs], on_warning=warn))
                if ris_inputs:
                    # Pass-through existing RIS so they stay in the output.
                    for p in ris_inputs:
                        try:
                            output_chunks.append(p.read_text(encoding="utf-8"))
                        except Exception as exc:  # pragma: no cover
                            warn(f"Failed to read {p}: {exc}")
                self.output_label_var.set("Output (RIS)")
        except ValueError as exc:
            messagebox.showerror("Conversion failed", str(exc))
            self.status_var.set("Conversion failed.")
            return

        if unknown:
            warn(f"Skipped unknown format: {', '.join(str(p) for p in unknown)}")

        if not output_chunks:
            messagebox.showwarning("No output", "No convertible entries found.")
            self.status_var.set("No output produced.")
            return

        final_text = "\n\n".join(chunk.strip() for chunk in output_chunks if chunk.strip()) + "\n"
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, final_text)

        status = "Conversion complete."
        if warnings:
            status += f" {len(warnings)} warning(s)."
            messagebox.showwarning("Conversion warnings", "\n".join(warnings))
        self.status_var.set(status)

    # --- Save ------------------------------------------------------------

    def _save_output(self) -> None:
        content = self.output_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showinfo("No output", "Run a conversion first, then save the output.")
            return

        if self.mode_var.get() == "ris_to_bib":
            defext = ".bib"
            ftypes = [("BibTeX files", "*.bib"), ("All files", "*.*")]
        else:
            defext = ".ris"
            ftypes = [("RIS files", "*.ris"), ("All files", "*.*")]

        path = self._custom_save_dialog(defext, ftypes)
        if not path:
            return

        Path(path).write_text(content + "\n", encoding="utf-8")
        self.status_var.set(f"Saved to {path}")

    # --- Misc ------------------------------------------------------------

    def _update_mode(self) -> None:
        mode = self.mode_var.get()
        if mode == "ris_to_bib":
            self.output_label_var.set("Output (BibTeX)")
            self.status_var.set("RIS → BibTeX mode.")
        else:
            self.output_label_var.set("Output (RIS)")
            self.status_var.set("BibTeX → RIS mode.")

    # --- Custom save dialog with hidden toggle ---------------------------

    def _custom_save_dialog(self, defext: str, ftypes: Sequence[tuple[str, str]]) -> str | None:
        """Custom save dialog that can hide dotfiles."""
        result: str | None = None
        top = tk.Toplevel(self)
        top.title("Save output")
        top.transient(self)
        top.grab_set()

        current_dir = Path.home().resolve()
        show_hidden = tk.BooleanVar(value=False)
        filename_var = tk.StringVar()

        frame = ttk.Frame(top, padding=12)
        frame.grid(row=0, column=0, sticky="nsew")
        top.columnconfigure(0, weight=1)
        top.rowconfigure(0, weight=1)

        path_var = tk.StringVar(value=str(current_dir))
        ttk.Label(frame, textvariable=path_var).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 6))

        listbox = tk.Listbox(frame, height=12)
        listbox.grid(row=1, column=0, columnspan=3, sticky="nsew")
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=listbox.yview)
        scrollbar.grid(row=1, column=3, sticky="ns")
        listbox.configure(yscrollcommand=scrollbar.set)

        def refresh_list() -> None:
            listbox.delete(0, tk.END)
            entries = []
            try:
                for name in os.listdir(current_dir):
                    if not show_hidden.get() and name.startswith("."):
                        continue
                    entries.append(name)
            except PermissionError:
                messagebox.showwarning("Access denied", f"Cannot access {current_dir}")
                return
            entries.sort(key=str.lower)
            listbox.insert(tk.END, "..")
            for name in entries:
                listbox.insert(tk.END, name)

        def enter_dir(dir_name: str) -> None:
            nonlocal current_dir
            if dir_name == "..":
                current_dir = current_dir.parent
            else:
                candidate = current_dir / dir_name
                if candidate.is_dir():
                    current_dir = candidate.resolve()
            path_var.set(str(current_dir))
            refresh_list()

        def on_select(event=None) -> None:
            selection = listbox.curselection()
            if not selection:
                return
            name = listbox.get(selection[0])
            if name == "..":
                filename_var.set("")
                return
            path = current_dir / name
            if path.is_dir():
                enter_dir(name)
            else:
                filename_var.set(name)

        listbox.bind("<Double-Button-1>", lambda e: on_select())
        listbox.bind("<<ListboxSelect>>", lambda e: on_select())

        refresh_list()

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(8, 4))
        btn_frame.columnconfigure(2, weight=1)

        ttk.Button(btn_frame, text="Up", command=lambda: enter_dir("..")).grid(row=0, column=0, padx=(0, 6))
        ttk.Checkbutton(
            btn_frame,
            text="Show hidden",
            variable=show_hidden,
            command=refresh_list,
        ).grid(row=0, column=1, padx=(0, 6))

        ttk.Label(frame, text="File name:").grid(row=3, column=0, sticky="w", pady=(4, 0))
        entry = ttk.Entry(frame, textvariable=filename_var, width=40)
        entry.grid(row=3, column=1, columnspan=3, sticky="ew", pady=(4, 0))

        def on_save() -> None:
            name = filename_var.get().strip()
            if not name:
                messagebox.showwarning("No file name", "Please enter a file name.")
                return
            final_name = name
            if defext and not final_name.endswith(defext):
                final_name += defext
            full_path = current_dir / final_name
            nonlocal result
            result = str(full_path)
            top.destroy()

        def on_cancel() -> None:
            nonlocal result
            result = None
            top.destroy()

        action_frame = ttk.Frame(frame)
        action_frame.grid(row=4, column=0, columnspan=4, sticky="e", pady=(10, 0))
        ttk.Button(action_frame, text="Cancel", command=on_cancel).grid(row=0, column=0, padx=(0, 6))
        ttk.Button(action_frame, text="Save", command=on_save, style="Accent.TButton").grid(row=0, column=1)

        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(1, weight=1)

        entry.focus_set()
        top.wait_window(top)
        return result


def main() -> None:
    app = Ris2BibApp()
    app.mainloop()


if __name__ == "__main__":
    main()
