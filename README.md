# IFX Catalog Manager

A desktop application for managing IFX fastener catalogs. Create new catalogs, add fasteners from templates, and append data rows to existing fastener files.

## Installation & Creo Setup

1. **Download** the project and extract it to a separate directory (e.g. `C:\dev\IFX Customizer`).
2. **Copy** the exisitng ifx folder from your Creo installation `{creo_location}Common Files\ifx` to `{install_location}\ifx`.
3. **Configure Creo IFX** to point to the IFX parts folder: `{install_location}\ifx\parts`. This is where Creo reads catalogs and fastener data from. You can find it by opening an assembly and going to **Tools > Intelligent Fastner > Options > PATH_ABS_LIBRARY**

## Quick Start (No Python Required)

A pre-built Windows executable is available in the `dist` folder:

```
dist/ifx_catalog_manager.exe
```

Double-click the executable or run it from a terminal. No Python installation needed. Bypass the warning.

---

## Running from Source (Python Required)

**Requirements:** Python 3.10+, CustomTkinter, Pillow

Create and activate a virtual environment, then install dependencies:

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

With the virtual environment activated:

```bash
python ifx_catalog_manager.py
```

## Expected Folder Structure

Point the app at your IFX data root folder. It looks for:

```
YourIFXFolder/
├── ifx/parts/
│   ├── ifx_catalogs/           # Catalog index and catalog files
│   │   ├── ifx_catalogs.txt
│   │   ├── McMaster_Carr.txt   # Example catalog
│   │   └── ...
│   └── ifx_fastener_data/      # Output: created fastener .prt and .dat files
│       ├── mynut.prt
│       ├── mynut.dat
│       └── ...
├── ifx_fastener_templates/     # Template sources (screws, nuts, washers, etc.)
│   ├── screws/
│   │   ├── screw_01/
│   │   ├── screw_81/
│   │   └── ...
│   ├── nuts/
│   ├── washers/
│   ├── inserts/
│   └── pins/
```
---

## How to Use

### 1. Set the IFX Data Folder

Use **Browse** to select the root folder containing your IFX installation copy. The app will search for `ifx_catalogs` and set `ifx_fastener_data` and `ifx_fastener_templates` automatically.

### 2. Add a New Catalog

1. Select a **section heading** from the dropdown (e.g. `#screws`)
2. Enter a catalog name (no spaces)
3. Click **Add new catalog**

Creates `{name}.txt` and adds it to the catalog index.

### 3. Add a Fastener to a Catalog

1. Select a **catalog** from the dropdown (e.g. `McMaster_Carr`)
2. Enter an **item name** (no spaces; stored lowercase)
3. Choose **Add under section** (e.g. `#screws`)
4. Click **Add to catalog**

**If the fastener does not exist on disk:**
- Select a template from the grid (click to select)
- Click **Create from template**
- Fill in the Enter values form (Units, SYMBOL, dimensions, etc.)
- Click **Create**

**If the fastener already exists** (`.prt` and `.dat` in `ifx_fastener_data`):
- The template picker is skipped
- You go straight to the Enter values form
- Units are fixed from the existing `.dat` (read-only)
- Click **Create** to append a new row to the `.dat` file (no catalog edit, no `.prt` copy)

### 4. Enter Values Form

- **Units:** MM or INCH (disabled in append mode)
- **SYMBOL, STRING, DN, LG, …:** Fill according to the template
- **INFO:** Auto-set to the fastener name (hidden field)
- A **dimension legend** (`*_detail.gif`) is shown when available
- **Validation:** Numeric fields must use decimals or whole numbers. SYMBOL cannot match the item name
- **Cancel:** Returns to the previous screen without saving

### 5. What Gets Created

When creating a **new** fastener:

- Catalog `.txt` is updated with the item name
- `{item_name}.prt` is copied (MM → `template.prt`, INCH → `template_inch.prt` if it exists)
- `{item_name}.dat` is created with header and one data row

When **appending** to an existing fastener:

- Only the `.dat` file is updated (new row appended)
- No catalog change, no `.prt` copy

---

## Template Requirements

Templates live under `ifx_fastener_templates/{type}/`:

| Section  | Folder   | Example templates |
|----------|----------|-------------------|
| #screws  | screws   | screw_01, screw_81 |
| #washers | washers  | washer_01        |
| #nuts    | nuts     | nut_01, nut_51   |
| #inserts | inserts  | insert_01        |
| #pins    | pins     | pin_01           |

Each template folder must:

1. **Match names:** Folder name must match the `.dat` filename (e.g. `screw_61/screw_61.dat`)
2. **Contain:** `{name}.dat` and `{name}.prt` (or `{name}_inch.prt` for inch)
3. `{name}_detail.gif` for the dimension legend on the Enter values screen

The `.dat` file must have:

- A `SYMBOL` row with variable names (tab-separated)
- An `INSTANCE` row for types (used for numeric validation)
- A `UNIT` line (MM or INCH)

---

## Catalog File Format

**Index** (`ifx_catalogs.txt`):

```
#screws
McMaster_Carr   

#washers
...
```

**Catalog** (e.g. `McMaster_Carr.txt`):

```
#screws
mynut
hexbolt

#nuts
...
```

---

## License

See `License.txt` if present.
