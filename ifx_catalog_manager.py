"""
IFX Catalog Manager - CustomTkinter application for managing IFX fastener catalogs.
"""

import re
import shutil
import customtkinter as ctk
from pathlib import Path
from tkinter import messagebox, filedialog
from PIL import Image

# Default sections - extracted from catalog files
DEFAULT_SECTIONS = ["#screws", "#washers", "#nuts", "#inserts", "#pins"]

# Catalog index filename (try both variants)
CATALOG_INDEX_FILES = ["ifx_catalog.txt", "ifx_catalogs.txt"]

# INSTANCE row types that indicate text (not numeric)
TEXT_TYPES = {"STRING", "name", "type", "size"}
# Variable names that are always text, regardless of INSTANCE row
TEXT_VAR_NAMES = {"SYMBOL", "STRING", "BUW_NAME", "BUW_TYPE", "BUW_SIZE"}


def validate_numeric_value(var_name: str, raw: str, numeric_vars: set[str]) -> tuple[str, str | None]:
    """
    Validate a numeric field. Does not correct - user must use . for decimals.
    numeric_vars: set of variable names that expect numeric values (from .dat INSTANCE row).
    Returns (value, error_message). error_message is None if valid.
    """
    if var_name not in numeric_vars:
        return raw, None
    if not raw.strip():
        return raw, None  # Empty is allowed
    try:
        float(raw.strip())
        return raw, None
    except ValueError:
        return raw, f"'{var_name}' must be a valid number"


def get_sections_from_catalog(catalog_path: Path) -> list[str]:
    """Extract #section headings from a catalog file."""
    sections = []
    if catalog_path.exists():
        with open(catalog_path, "r", encoding="utf-8-sig", errors="ignore") as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith("#") and stripped not in sections:
                    sections.append(stripped)
    return sections if sections else DEFAULT_SECTIONS


def parse_catalog_index(file_path: Path) -> tuple[list[str], list[tuple[str, str]]]:
    """
    Parse ifx_catalogs.txt style file.
    Returns: (list of display items in order, list of (item, section) for items)
    """
    display_items = []
    item_sections = []  # (item, section) for each non-heading item
    
    if not file_path.exists():
        return display_items, item_sections
    
    current_section = None
    with open(file_path, "r", encoding="utf-8-sig", errors="ignore") as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("#"):
                current_section = stripped
                display_items.append(stripped)
            else:
                display_items.append(stripped)
                if current_section:
                    item_sections.append((stripped, current_section))
    
    return display_items, item_sections


def get_catalog_file_path(catalogs_dir: Path, catalog_name: str) -> Path:
    """Get path to a catalog's .txt file."""
    return catalogs_dir / f"{catalog_name}.txt"


SECTION_TO_TEMPLATE_FOLDER = {
    "#screws": "screws",
    "#washers": "washers",
    "#nuts": "nuts",
    "#inserts": "inserts",
    "#pins": "pins",
}


def get_template_folder_for_section(section: str) -> str | None:
    """Map section to template subfolder name."""
    for key, folder in SECTION_TO_TEMPLATE_FOLDER.items():
        if key in section:
            return folder
    return None


def parse_dat_variables(dat_path: Path) -> tuple[list[str], str, set[str]]:
    """
    Parse .dat file to extract variable names from SYMBOL row, UNIT, and which are numeric from INSTANCE row.
    Returns (list of variable names, current unit "MM" or "INCH", set of numeric variable names).
    """
    variables = []
    unit = "MM"
    numeric_vars = set()
    if not dat_path.exists():
        return variables, unit, numeric_vars
    lines = []
    with open(dat_path, "r", encoding="utf-8-sig", errors="ignore") as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.upper().startswith("UNIT\t") or stripped.upper().startswith("UNIT "):
            parts = stripped.split(None, 1)
            if len(parts) >= 2:
                unit = parts[1].strip().upper()
                if unit not in ("MM", "INCH"):
                    unit = "MM"
        elif stripped.upper().startswith("SYMBOL"):
            variables = [v.strip() for v in line.split("\t") if v.strip()]
            # Next line is INSTANCE with types - use to determine numeric vars dynamically
            if i + 1 < len(lines):
                instance_parts = [p.strip() for p in lines[i + 1].split("\t") if p.strip()]
                if instance_parts and instance_parts[0].upper() == "INSTANCE":
                    for j, var in enumerate(variables):
                        if var in TEXT_VAR_NAMES:
                            continue  # SYMBOL, STRING, BUW_* are always text
                        if j + 1 < len(instance_parts):
                            inst_type = instance_parts[j + 1].lower()
                            # STRING, name, type, size = text; DN, LG, K, etc. = numeric
                            if inst_type not in {t.lower() for t in TEXT_TYPES}:
                                numeric_vars.add(var)
            break
    return variables, unit, numeric_vars


def get_detail_gif_path(template_dir: Path, base_name: str) -> Path | None:
    """Return path to {base}_detail.gif in template dir if it exists."""
    p = template_dir / f"{base_name}_detail.gif"
    return p if p.exists() else None


def list_templates_with_gifs(templates_dir: Path, type_folder: str) -> list[tuple[str, Path, Path | None]]:
    """
    Walk through type_folder (screws, washers, etc.) and all subfolders to find templates.
    A template folder contains {foldername}.dat (e.g. screw_01/screw_01.dat).
    Returns list of (display_name, template_folder_path, gif_path or None).
    """
    type_path = templates_dir / type_folder
    if not type_path.exists():
        return []
    result = []
    for subdir in sorted(type_path.rglob("*")):
        if not subdir.is_dir():
            continue
        base = subdir.name
        dat_file = subdir / f"{base}.dat"
        if not dat_file.exists():
            continue
        gif_path = None
        for f in subdir.iterdir():
            if f.is_file() and f.suffix.lower() == ".gif" and not f.stem.endswith("_detail"):
                gif_path = f
                break
        result.append((base, subdir, gif_path))
    return result


class IFXCatalogManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("IFX Catalog Manager")
        self.geometry("700x550")
        self.resizable(False, False)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Data paths
        self.base_folder = Path(r"C:\dev\IFX Customizer")
        self.catalogs_dir = self.base_folder / "ifx" / "parts" / "ifx_catalogs"
        self.fastener_data_dir = self.base_folder / "ifx" / "parts" / "ifx_fastener_data"
        self.templates_dir = self.base_folder / "ifx_fastener_templates"
        self.catalog_index_path = None
        self.display_items = []
        self.item_sections = {}  # item -> section
        self.sections = DEFAULT_SECTIONS

        self._build_ui()
        self._load_catalog_index()

    def _build_ui(self):
        # Folder selection frame (hidden when on dat editor)
        self.folder_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.folder_frame.pack(fill="x", padx=20, pady=(10, 4))

        ctk.CTkLabel(self.folder_frame, text="IFX Data Folder:", width=120).pack(
            side="left", padx=(0, 10)
        )
        self.folder_var = ctk.StringVar(value=str(self.base_folder))
        self.folder_entry = ctk.CTkEntry(
            self.folder_frame, textvariable=self.folder_var, width=400
        )
        self.folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(
            self.folder_frame, text="Browse", width=80, command=self._browse_folder
        ).pack(side="left")

        # Catalog list frame (hidden when on dat editor)
        self.list_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="x", padx=20, pady=4)

        ctk.CTkLabel(self.list_frame, text="Catalog (ifx_catalog.txt):").pack(anchor="w")
        self.combo_var = ctk.StringVar()
        self.catalog_combo = ctk.CTkComboBox(
            self.list_frame,
            values=[],
            variable=self.combo_var,
            width=400,
            state="readonly",
            command=self._on_selection_changed,
        )
        self.catalog_combo.pack(fill="x", pady=(2, 4))

        # Selection info
        self.selection_info = ctk.CTkLabel(
            self.list_frame, text="", text_color="gray", anchor="w"
        )
        self.selection_info.pack(fill="x")

        # Action area - varies by selection type
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.pack(fill="both", expand=True, padx=20, pady=8)

    def _find_catalog_index(self) -> Path | None:
        """Find the catalog index file in catalogs directory."""
        for name in CATALOG_INDEX_FILES:
            path = self.catalogs_dir / name
            if path.exists():
                return path
        return None

    def _browse_folder(self):
        folder = filedialog.askdirectory(
            initialdir=str(self.base_folder), title="Select IFX data folder"
        )
        if folder:
            self.base_folder = Path(folder)
            self.folder_var.set(folder)
            # Try common locations for ifx_catalogs (ifx11 is used by some IFX installs)
            for subpath in [
                Path("ifx") / "parts" / "ifx_catalogs",
                Path("ifx11") / "parts" / "ifx_catalogs",
                Path("ifx_catalogs"),
            ]:
                cand = self.base_folder / subpath
                if cand.exists():
                    self.catalogs_dir = cand
                    self.fastener_data_dir = self.catalogs_dir.parent / "ifx_fastener_data"
                    self.templates_dir = self.base_folder / "ifx_fastener_templates"
                    break
            else:
                self.catalogs_dir = self.base_folder / "ifx" / "parts" / "ifx_catalogs"
                self.fastener_data_dir = self.base_folder / "ifx" / "parts" / "ifx_fastener_data"
                self.templates_dir = self.base_folder / "ifx_fastener_templates"
            self._load_catalog_index()

    def _load_catalog_index(self):
        self.catalog_index_path = self._find_catalog_index()
        if not self.catalog_index_path:
            self.display_items = []
            self.item_sections = {}
            self.catalog_combo.configure(values=["(No ifx_catalog.txt found)"])
            self.combo_var.set("")
            return

        self.display_items, pairs = parse_catalog_index(self.catalog_index_path)
        self.item_sections = dict(pairs)

        # Update combo
        self.catalog_combo.configure(values=self.display_items)
        if self.display_items:
            self.combo_var.set(self.display_items[0])
        self._on_selection_changed(None)

    def _on_selection_changed(self, _):
        sel = self.combo_var.get()
        self._clear_action_frame()
        # Show folder/catalog UI when on main screens
        self.folder_frame.pack(fill="x", padx=20, pady=(10, 4), before=self.action_frame)
        self.list_frame.pack(fill="x", padx=20, pady=4, before=self.action_frame)
        self.geometry("700x550")
        if not sel or sel.startswith("("):
            return

        if sel.startswith("#"):
            self.selection_info.configure(text=f"Selected: Section heading {sel}")
            self._build_add_catalog_ui(sel)
        else:
            section = self.item_sections.get(sel, "?")
            self.selection_info.configure(
                text=f"Selected: Catalog '{sel}' (under {section})"
            )
            self._build_add_to_catalog_ui(sel)

    def _clear_action_frame(self):
        for w in self.action_frame.winfo_children():
            w.destroy()
        self.geometry("700x550")

    def _build_add_catalog_ui(self, section: str):
        """Build UI for adding a new catalog when a section heading is selected."""
        ctk.CTkLabel(
            self.action_frame,
            text="Add new catalog to this section",
            font=ctk.CTkFont(weight="bold"),
        ).pack(anchor="w", pady=(0, 10))

        row1 = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Catalog name:", width=120).pack(side="left", padx=(0, 10))
        self.new_name_entry = ctk.CTkEntry(row1, width=250, placeholder_text="e.g. my_catalog")
        self.new_name_entry.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            self.action_frame,
            text="Add new catalog",
            command=lambda: self._add_new_catalog(section),
        ).pack(anchor="w", pady=(15, 0))

    def _build_add_to_catalog_ui(self, catalog_name: str):
        """Build UI for adding an item to an existing catalog."""
        ctk.CTkLabel(
            self.action_frame,
            text=f"Add fastener/item to catalog '{catalog_name}'",
            font=ctk.CTkFont(weight="bold"),
        ).pack(anchor="w", pady=(0, 10))

        # Get sections from this catalog file
        catalog_path = get_catalog_file_path(self.catalogs_dir, catalog_name)
        if catalog_path.exists():
            self.sections = get_sections_from_catalog(catalog_path)
        else:
            self.sections = DEFAULT_SECTIONS

        row1 = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Item name:", width=120).pack(side="left", padx=(0, 10))
        self.add_item_entry = ctk.CTkEntry(row1, width=250, placeholder_text="e.g. HexBolt")
        self.add_item_entry.pack(side="left", padx=(0, 10))

        row2 = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        ctk.CTkLabel(row2, text="Add under section:", width=120).pack(
            side="left", padx=(0, 10)
        )
        self.add_section_combo = ctk.CTkComboBox(
            row2, values=self.sections, width=150, state="readonly"
        )
        self.add_section_combo.pack(side="left", padx=(0, 10))
        if self.sections:
            self.add_section_combo.set(self.sections[0])

        ctk.CTkButton(
            self.action_frame,
            text="Add to catalog",
            command=lambda: self._add_to_catalog(catalog_name),
        ).pack(anchor="w", pady=(15, 0))

    def _build_template_selection_ui(self, item_name: str, section: str, catalog_name: str):
        """After adding to catalog: show template picker, then copy files on button click."""
        self._clear_action_frame()
        self.pending_fastener = {"item_name": item_name, "section": section, "catalog_name": catalog_name}

        type_folder = get_template_folder_for_section(section)
        if not type_folder or not self.templates_dir.exists():
            messagebox.showwarning(
                "No templates",
                f"No templates found for {section}. Add ifx_fastener_templates folder.",
            )
            self._on_selection_changed(None)
            return

        templates = list_templates_with_gifs(self.templates_dir, type_folder)
        if not templates:
            messagebox.showwarning(
                "No templates",
                f"No templates found in {self.templates_dir / type_folder}",
            )
            self._on_selection_changed(None)
            return

        self.template_options = [(base, path, gif_path) for base, path, gif_path in templates]
        self.selected_template_path = self.template_options[0][1]  # default first

        ctk.CTkLabel(
            self.action_frame,
            text=f"Select template for '{item_name}'",
            font=ctk.CTkFont(weight="bold"),
        ).pack(anchor="w", pady=(0, 10))

        scroll_frame = ctk.CTkScrollableFrame(self.action_frame, width=560, height=200)
        scroll_frame.pack(fill="both", expand=True, pady=(5, 10))

        self._template_image_refs = []  # keep refs to avoid gc
        self._template_cells = {}  # path -> cell for highlighting
        thumb_size = (64, 64)
        for i, (base, path, gif_path) in enumerate(self.template_options):
            row, col = i // 6, i % 6
            cell = ctk.CTkFrame(
                scroll_frame,
                fg_color=("gray90", "gray25"),
                corner_radius=6,
                border_width=2,
                border_color=("gray75", "gray35"),
                width=80,
                height=90,
            )
            cell.grid(row=row, column=col, padx=5, pady=5, sticky="nw")
            self._template_cells[path] = cell

            if gif_path and gif_path.exists():
                try:
                    pil_img = Image.open(str(gif_path)).convert("RGBA")
                    ctk_img = ctk.CTkImage(light_image=pil_img, size=thumb_size)
                    self._template_image_refs.append((pil_img, ctk_img))
                    btn = ctk.CTkButton(
                        cell, image=ctk_img, text="", width=70, height=70,
                        fg_color="transparent", hover_color=("gray80", "gray30"),
                        border_width=0, cursor="hand2", command=lambda p=path: self._on_template_thumb_click(p),
                    )
                except Exception:
                    btn = ctk.CTkButton(
                        cell, text=base[:8], width=70, height=70,
                        fg_color="transparent", hover_color=("gray80", "gray30"),
                        cursor="hand2", command=lambda p=path: self._on_template_thumb_click(p),
                    )
            else:
                btn = ctk.CTkButton(
                    cell, text=base[:8], width=70, height=70,
                    fg_color="transparent", hover_color=("gray80", "gray30"),
                    cursor="hand2", command=lambda p=path: self._on_template_thumb_click(p),
                )

            btn.pack(pady=(4, 2))
            ctk.CTkLabel(cell, text=base, font=ctk.CTkFont(size=11)).pack()

        self._highlight_selected_template()

        ctk.CTkButton(
            self.action_frame,
            text="Create from template",
            command=self._show_dat_editor,
        ).pack(anchor="w", pady=(0, 10))

    def _show_dat_editor(self):
        """Show the .dat variable editor before creating the fastener."""
        if not hasattr(self, "pending_fastener") or not hasattr(self, "selected_template_path"):
            return
        pf = self.pending_fastener
        template_path = self.selected_template_path
        if not template_path.exists():
            messagebox.showerror("Error", "Template not found.")
            return

        template_base = template_path.name
        dat_path = template_path / f"{template_base}.dat"
        variables, unit, numeric_vars = parse_dat_variables(dat_path)
        if not variables:
            messagebox.showwarning("No variables", f"Could not parse variables from {dat_path.name}. Proceeding without form.")
            self._create_from_template()
            return

        self._dat_editor_vars = variables
        self._dat_numeric_vars = numeric_vars
        detail_gif = get_detail_gif_path(template_path, template_base)

        self._clear_action_frame()

        # Hide folder/catalog, expand window for values form only
        self.folder_frame.pack_forget()
        self.list_frame.pack_forget()
        self.geometry("700x720")

        # Form content - no scroll, window tall enough to fit all
        inner = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        inner.pack(fill="both", expand=True)

        ctk.CTkLabel(
            inner,
            text=f"Enter values for '{pf['item_name']}'",
            font=ctk.CTkFont(weight="bold"),
        ).pack(anchor="w", pady=(0, 2))

        # Detail GIF at top - natural size to avoid clipping
        if detail_gif and detail_gif.exists():
            try:
                pil_img = Image.open(str(detail_gif)).convert("RGBA")
                w, h = pil_img.size
                ctk_img = ctk.CTkImage(light_image=pil_img, size=(w, h))
                self._detail_image_ref = (pil_img, ctk_img)
                ctk.CTkLabel(inner, text="", image=ctk_img).pack(anchor="w", pady=(0, 4))
            except Exception:
                self._detail_image_ref = None
        else:
            self._detail_image_ref = None

        # Units only - on its own row
        top_row = ctk.CTkFrame(inner, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 2))
        ctk.CTkLabel(top_row, text="Units:").pack(side="left", padx=(0, 6))
        self._unit_var = ctk.StringVar(value=unit)
        ctk.CTkComboBox(
            top_row, values=["MM", "INCH"], variable=self._unit_var, width=80, state="readonly"
        ).pack(side="left")

        # Form: INFO is hidden (auto-set to fastener name), other vars visible
        form_frame = ctk.CTkFrame(inner, fg_color="transparent")
        form_frame.pack(fill="x", pady=(0, 2))

        self._dat_entries = {}

        form_vars = [v for v in variables if v != "INFO"]
        left_vars = [v for v in form_vars if v not in ("BUW_NAME", "BUW_TYPE", "BUW_SIZE")]
        right_vars = [v for v in form_vars if v in ("BUW_NAME", "BUW_TYPE", "BUW_SIZE")]
        num_rows = max(len(left_vars), len(right_vars), 1)

        for i in range(num_rows):
            if i < len(left_vars):
                v = left_vars[i]
                ctk.CTkLabel(form_frame, text=f"{v}:").grid(
                    row=i, column=0, sticky="w", padx=(0, 6), pady=1
                )
                entry = ctk.CTkEntry(form_frame, width=160)
                entry.grid(row=i, column=1, sticky="w", padx=(0, 20), pady=1)
                self._dat_entries[v] = entry
            if i < len(right_vars):
                v = right_vars[i]
                ctk.CTkLabel(form_frame, text=f"{v}:").grid(
                    row=i, column=2, sticky="w", padx=(0, 6), pady=1
                )
                entry = ctk.CTkEntry(form_frame, width=160)
                entry.grid(row=i, column=3, sticky="w", pady=1)
                self._dat_entries[v] = entry

        ctk.CTkButton(
            inner,
            text="Create",
            command=self._create_from_template,
        ).pack(anchor="e", pady=(4, 0))

    def _on_template_thumb_click(self, template_path: Path):
        """Update selection when user clicks a template thumbnail."""
        self.selected_template_path = template_path
        self._highlight_selected_template()

    def _highlight_selected_template(self):
        """Highlight the currently selected template cell."""
        if not hasattr(self, "_template_cells"):
            return
        for path, cell in self._template_cells.items():
            if path == getattr(self, "selected_template_path", None):
                cell.configure(border_width=3, border_color=("#1f6aa5", "#3b8ed0"))
            else:
                cell.configure(border_width=2, border_color=("gray75", "gray35"))

    def _create_from_template(self):
        """Copy template .prt, .dat, .gifs to ifx_fastener_data with user's name."""
        if not hasattr(self, "pending_fastener"):
            return
        pf = self.pending_fastener
        item_name = pf["item_name"]
        catalog_name = pf["catalog_name"]
        section = pf["section"]

        template_path = getattr(self, "selected_template_path", None)
        if not template_path or not template_path.exists():
            messagebox.showerror("Error", "Template not found.")
            return

        template_base = template_path.name  # e.g. screw_01
        dest = self.fastener_data_dir
        dest.mkdir(parents=True, exist_ok=True)

        copied = []
        dat_content_to_write = None

        # If we have dat editor entries, build dat content with user values
        if hasattr(self, "_dat_entries") and hasattr(self, "_dat_editor_vars"):
            variables = self._dat_editor_vars
            values = []
            for var in variables:
                if var == "INFO":
                    raw = pf["item_name"]
                else:
                    entry = self._dat_entries.get(var)
                    raw = entry.get().strip() if entry else ""
                _, err = validate_numeric_value(var, raw, getattr(self, "_dat_numeric_vars", set()))
                if err:
                    messagebox.showwarning("Invalid value", err)
                    return
                values.append(raw)

            info_str = pf["item_name"]
            symbol_entry = self._dat_entries.get("SYMBOL")
            symbol_str = symbol_entry.get().strip() if symbol_entry else ""
            if info_str and symbol_str and info_str.lower() == symbol_str.lower():
                messagebox.showwarning("Invalid value", f"SYMBOL cannot be same name as Item Name ({info_str})")
                return

            src_dat = template_path / f"{template_base}.dat"
            if src_dat.exists():
                content = src_dat.read_text(encoding="utf-8", errors="ignore")
                content = content.replace(template_base, item_name)

                # Update or add UNIT line
                unit_val = getattr(self, "_unit_var", ctk.StringVar(value="MM")).get()
                before_unit = content
                content = re.sub(r"(?m)^UNIT\s+\S+", f"UNIT\t{unit_val}", content)
                if content == before_unit and "UNIT" not in content:
                    # No UNIT line exists, add after first TYPE line
                    content = re.sub(
                        r"(?m)^(SCREWTYPE|WASHERTYPE|NUTTYPE|INSERTTYPE|PINTYPE)\s+\S+",
                        lambda m: m.group(0) + f"\nUNIT\t{unit_val}",
                        content,
                        count=1,
                    )

                # Update INFO line (always fastener name)
                content = re.sub(r"(?m)^INFO\s+.*", f"INFO\t{pf['item_name']}", content)

                # Append new data row at end (tab-separated, in variable order)
                new_row = "\t".join(values)
                content = content.rstrip()
                if content and not content.endswith("\n"):
                    content += "\n"
                content += new_row + "\n"
                dat_content_to_write = content

        unit_val = getattr(self._unit_var, "get", lambda: "MM")() if hasattr(self, "_unit_var") else "MM"
        prt_src = template_path / f"{template_base}_inch.prt" if unit_val == "INCH" else template_path / f"{template_base}.prt"
        if unit_val == "INCH" and not prt_src.exists():
            prt_src = template_path / f"{template_base}.prt"  # Fallback if _inch not found

        for ext in [".prt", ".dat"]:
            src = prt_src if ext == ".prt" else template_path / f"{template_base}{ext}"
            if src.exists():
                dst = dest / f"{item_name}{ext}"
                try:
                    if ext == ".dat" and dat_content_to_write is not None:
                        dst.write_text(dat_content_to_write, encoding="utf-8")
                    elif ext == ".dat":
                        content = src.read_text(encoding="utf-8", errors="ignore")
                        content = content.replace(template_base, item_name)
                        dst.write_text(content, encoding="utf-8")
                    else:
                        shutil.copy2(src, dst)
                    copied.append(f"{item_name}{ext}")
                except OSError as e:
                    messagebox.showwarning("Copy failed", f"Could not copy {ext}: {e}")

        for f in template_path.iterdir():
            if f.suffix.lower() == ".gif":
                dst = dest / f"{item_name}{f.suffix}"
                try:
                    shutil.copy2(f, dst)
                    copied.append(f"{item_name}{f.suffix}")
                except OSError:
                    pass

        msg = f"Added '{item_name}' to {catalog_name}.txt under {section}."
        if copied:
            msg += f"\n\nCreated: {', '.join(copied)}"
        messagebox.showinfo("Success", msg)

        # Clean up dat editor refs
        for attr in ("pending_fastener", "_dat_entries", "_dat_editor_vars", "_dat_numeric_vars", "_unit_var"):
            if hasattr(self, attr):
                try:
                    delattr(self, attr)
                except Exception:
                    pass
        try:
            self.add_item_entry.delete(0, "end")
        except Exception:
            pass
        self._on_selection_changed(None)

    def _add_new_catalog(self, section: str):
        """Create new catalog file and add to ifx_catalogs.txt."""
        name = (self.new_name_entry.get() or "").strip()
        if not name:
            messagebox.showwarning("Missing name", "Please enter a catalog name.")
            return
        if " " in name:
            messagebox.showwarning("Invalid name", "Spaces are not allowed in catalog names.")
            return
        if not self.catalog_index_path or not self.catalog_index_path.exists():
            messagebox.showerror("Error", "Catalog index file not found.")
            return

        catalog_path = get_catalog_file_path(self.catalogs_dir, name)
        if catalog_path.exists():
            messagebox.showwarning(
                "Exists", f"Catalog '{name}' already exists ({catalog_path.name})."
            )
            return

        # Create new catalog .txt with standard sections
        template = "\n".join(
            f"{s}\n" for s in DEFAULT_SECTIONS
        ).rstrip()
        try:
            catalog_path.parent.mkdir(parents=True, exist_ok=True)
            with open(catalog_path, "w", encoding="utf-8") as f:
                f.write(template)
        except OSError as e:
            messagebox.showerror("Error", f"Cannot create file: {e}")
            return

        # Append to ifx_catalogs.txt under the chosen section
        try:
            with open(self.catalog_index_path, "r", encoding="utf-8-sig") as f:
                lines = f.readlines()
        except OSError as e:
            messagebox.showerror("Error", f"Cannot read index: {e}")
            return

        # Find section, last item, and next #heading; remove blanks between
        next_heading_idx = len(lines)
        last_item_idx = -1
        for i, line in enumerate(lines):
            if line.strip() == section:
                last_item_idx = i
                j = i + 1
                while j < len(lines):
                    if lines[j].strip().startswith("#"):
                        next_heading_idx = j
                        break
                    if lines[j].strip():
                        last_item_idx = j
                    j += 1
                break

        insert_idx = last_item_idx + 1
        while insert_idx < next_heading_idx and insert_idx < len(lines) and not lines[insert_idx].strip():
            del lines[insert_idx]
            next_heading_idx -= 1
        lines.insert(insert_idx, f"{name}\n\n")
        try:
            with open(self.catalog_index_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
        except OSError as e:
            messagebox.showerror("Error", f"Cannot write index: {e}")
            return

        messagebox.showinfo("Success", f"Created catalog '{name}.txt' and added under {section}.")
        self.new_name_entry.delete(0, "end")
        self._load_catalog_index()

    def _add_to_catalog(self, catalog_name: str):
        """Add an item to a catalog file under the chosen section."""
        item_name = (self.add_item_entry.get() or "").strip().lower()
        section = self.add_section_combo.get()
        if not item_name:
            messagebox.showwarning("Missing name", "Please enter an item name.")
            return
        if " " in item_name:
            messagebox.showwarning("Invalid name", "Spaces are not allowed in item names.")
            return

        catalog_path = get_catalog_file_path(self.catalogs_dir, catalog_name)
        if not catalog_path.exists():
            messagebox.showerror(
                "Error", f"Catalog file not found: {catalog_path}"
            )
            return

        try:
            with open(catalog_path, "r", encoding="utf-8-sig") as f:
                lines = f.readlines()
        except OSError as e:
            messagebox.showerror("Error", f"Cannot read catalog: {e}")
            return

        # Find section and next #heading; insert right after last item of section
        # Remove any blank lines between last item and next # (avoid extra space)
        next_heading_idx = len(lines)
        last_item_idx = -1
        for i, line in enumerate(lines):
            if line.strip() == section:
                last_item_idx = i
                j = i + 1
                while j < len(lines):
                    if lines[j].strip().startswith("#"):
                        next_heading_idx = j
                        break
                    if lines[j].strip():
                        last_item_idx = j
                    j += 1
                break

        new_entry = f"{item_name}\n\n"
        insert_idx = last_item_idx + 1
        # Remove all blank lines between last item and next heading
        while insert_idx < next_heading_idx and insert_idx < len(lines) and not lines[insert_idx].strip():
            del lines[insert_idx]
            next_heading_idx -= 1
        lines.insert(insert_idx, new_entry)
        try:
            with open(catalog_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
        except OSError as e:
            messagebox.showerror("Error", f"Cannot write catalog: {e}")
            return

        # Show template selection screen
        self._build_template_selection_ui(item_name, section, catalog_name)


def main():
    app = IFXCatalogManager()
    app.mainloop()


if __name__ == "__main__":
    main()
