# Creo IFX Customizer

A desktop application for managing IFX fastener catalogs. Create new catalogs, add fasteners from templates, and append data rows to existing fastener files. You can also import premade fastener catalogs. 

Compatible with Creo 6 or later. 

## Installation & Creo Setup

1. **Download** the project and extract it to a separate directory (e.g. `C:\dev\IFX Customizer`).
2. **Copy** the exisitng ifx folder from your Creo installation `{creo_location}\Common Files\ifx` to `{install_location}\ifx`.
3. **Configure Creo IFX** to point to the IFX parts folder: `{install_location}\ifx\parts`. This is where Creo reads catalogs and fastener data from. You can find it by opening an assembly and going to **Tools > Intelligent Fastener > Options > PATH_ABS_LIBRARY**

## Quick Start (No Python Required)

A pre-built Windows executable is available in the `dist` folder:

```
dist/ifx_catalog_manager.exe
```
Important: **Move** the executable out of the dist folder and into the root folder of the installation (e.g. `C:\dev\IFX Customizer`). Double-click the executable or run it from a terminal. No Python installation needed. Bypass the warning by clicking More info and Run anyway.

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
- A **dimension legend** is shown when available
- **Validation:** Numeric fields must use decimals or whole numbers. SYMBOL cannot match the item name
- **Cancel:** Returns to the previous screen without saving

## Usage

Run the application and choose to create a new category of fasteners under **#screws** or **#pins**. Give it a meaningful name without spaces. Then choose that new name from the **Category** drop down. You can then start creating fastener family libraries under that category.

Choose a name without spaces and select the type of fastener from the drop down. Options include **#screws**, **#nuts**, **#washers**, **#inserts**, or **#pins**.

Then select the template for the fastener. Look carefully at the pictures of each fastener to choose the correct one. Some screws have full threads and others have partial threads.

Next choose the units and enter all dimensional values accordingly.

### Field Descriptions

**SYMBOL**  
A unique Creo part name without spaces. This will be used as the name of the part when it is placed by IFX.

**STRING**  
The nominal size such as `"1/2-13"` or `"M12x1.75"`. This appears in the drop down when choosing the fastener size in IFX.

**BUW_NAME**  
A descriptive name such as `"Hex Head Bolt"`.

**BUW_TYPE**  
The fastener standard such as `"ANSI/ASME"`, `"DIN"`, or `"ISO"`.

**BUW_SIZE**  
Plain text description of the fastener size, for example `"1/2-13 x 2"`.

### Creating the Fastener

After entering all fields click the **Create** button. The fastener will be created from the selected template. You can then create additional fasteners of the same type with different sizes.

### Important Notes

Each **SYMBOL** must be unique across the entire library. Do not reuse SYMBOL names. Choose a unique part name or part number to avoid conflicts.

You can create many variations of screws with different dimensions.

Washers, nuts, and inserts behave slightly differently. IFX selects the first item in the family that fits the screw. If you need additional sizes or types you must create a separate family name. For example do not create the same washer diameter with variations of thickness. Only create different diameters within a fastener family so IFX selects the item that matches the corresponding screw diameter.

### (Optional) Creating Creo Parameters for Fasteners

**Create** a text file named `param_relations.txt` in your `ifx/parts/ifx_fastener_data` folder to create your own parameters using the following:

NAME = BUW_NAME  
TYPE = BUW_TYPE  
SIZE = BUW_SIZE  

or

DESCRIPTION = BUW_NAME + " " + BUW_SIZE + " " + BUW_TYPE

---

## Importing premade catalogs

You can import a premade catalog of fasteners by using the **Import...** button and selecting a `.ifx` file found in the `import` directory.

If you want to **author and share your own importable catalogs**, read the [`detailed guide`](https://github.com/mbourque/ifx_customizer/blob/master/import/README.md).

---

## Learn More

Visit the [`PTC Help Center`](https://support.ptc.com/help/creo/creo_pma/r7.0/usascii/index.html#page/assembly/intelligent_fastener/About_Working_with_Intelligent_Fastener.html) for information on using and customizing IFX.

## License

See `License.txt` if present.
