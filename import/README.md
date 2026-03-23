# Creating Importable Fastener Catalogs

You can contribute premade fastener catalogs to this project. These catalogs can be imported directly into the IFX library and will automatically merge with the existing catalog structure.

Follow the steps below to create a compatible catalog package.

---

## 1. Create the Required Folder Structure

Create a folder named `parts`.

At minimum, it must contain:

```text
parts/
  ifx_catalogs/
  ifx_fastener_data/
```

You can also include these optional folders when your package adds new templates or icons:

```text
parts/
  ifx_fastener_templates/
  ifx_fastener_icons/
```

These match the folders used by IFX for catalog definitions, fastener data, templates, and icons.

---

## 2. Create or Extend the Catalog Index

Inside `parts/ifx_catalogs` place a file named:

```text
ifx_catalogs.txt
```

This file is **required**. It lists the catalog entries that should be merged into the user's existing IFX catalog index during import.

If the catalog references a new entry that does not already exist in the user's environment, include the corresponding `.txt` catalog file in this same folder.

**Example contents:**

```text
#screws
mcmaster_screws
metric_socket_head_cap_screws

#nuts

#washers

#inserts
```

Each referenced catalog must also have its corresponding catalog definition file present in `parts/ifx_catalogs`:

```text
parts/ifx_catalogs/mcmaster_screws.txt
parts/ifx_catalogs/metric_socket_head_cap_screws.txt
```
These files should be in the following format:

```text
#screws
bolt_hex
socket_head_cap_screw

#nuts
hex_nut

#washers
flat_washer

#inserts
```

During import:

- `parts/ifx_catalogs/ifx_catalogs.txt` is always **merged** into the user's local `ifx_catalogs.txt`
- other `.txt` files in `parts/ifx_catalogs/` are copied into the user's catalog folder

---

## 3. Add Fastener Data Files

Place all fastener definition files in:

```text
parts/ifx_fastener_data/
```

**Typical examples:**

```text
bolt_hex.dat
socket_head_cap_screw.dat
flat_washer.dat
hex_nut.dat
dowel_pin.dat
```

Note: Each fastener family requires its `.dat` file containing the INSTANCE table and parameter definitions used by IFX. If you are using a part you created yourself the `.dat` file will need to have corresponding IDs for the fastener SURFACE and DATUM AXIS. You can use the config option `show_selected_item_id yes` to show them in Creo.

During import, files under `parts/ifx_fastener_data/` are copied into the user's IFX fastener data folder.

---

## 4. Optional: Add Template and Icon Files

If your package includes new templates or icons, place them under:

```text
parts/ifx_fastener_templates/
parts/ifx_fastener_icons/
```

Preserve the same relative folder structure IFX uses.

**Example:**

```text
parts/ifx_fastener_templates/screws/screw_19/screw_19.dat
parts/ifx_fastener_templates/screws/screw_19/screw_19.prt
parts/ifx_fastener_templates/screws/screw_19/screw_19_inch.prt
parts/ifx_fastener_templates/screws/screw_19/screw_19.gif
parts/ifx_fastener_templates/screws/screw_19/screw_19_detail.gif

parts/ifx_fastener_icons/screws/screw_19_icon.gif
```

During import:

- missing directories are created automatically
- files are copied into the matching `ifx/parts/...` folder
- if a template or icon file already exists locally, it is skipped and not overwritten

---

## 5. Create the Creo Part Files

Using Creo Parametric 6 and this tool:

1. Generate the fastener parts from the templates.  
2. Ensure the **SYMBOL name matches the Creo part filename**.  
3. Place the generated `.prt` files in the same `ifx_fastener_data` folder.

**Example:**

```text
parts/ifx_fastener_data/HEX_BOLT.prt
parts/ifx_fastener_data/HEX_BOLT.dat
```

Keep naming consistent so IFX can resolve the part correctly during placement. Remove any version numbers from part filenames (e.g. bolt.prt.5)

---

## 6. Package the Library

Once the folders are complete:

1. Zip the `parts` folder **so that `parts` is the top-level folder inside the archive**.

   ```text
   mcmaster-carr.zip
   ```

   The archive should look like this inside:

   ```text
   parts/
     ifx_catalogs/
     ifx_fastener_data/
     ifx_fastener_templates/   # optional
     ifx_fastener_icons/       # optional
   ```

   Do **not** wrap `parts` inside another folder such as:

   ```text
   mcmaster_carr/parts/...
   ```

2. Rename the extension from `.zip` to `.ifx`.

   ```text
   mcmaster-carr.ifx
   ```

The `.ifx` file is simply a packaged archive that the catalog manager can import.

---

## 7. Test the Catalog

Before submitting:

1. Import the `.ifx` file using the IFX catalog manager.  
2. Verify the catalog appears under the correct section, such as:

   ```text
   #screws
   #washers
   #nuts
   #pins
   #inserts
   ```

3. Place several fasteners in an assembly to confirm:

- **sizes** appear correctly  
- **Creo parts** load properly  
- **parameters** populate correctly  
- imported templates and icons appear in the correct IFX folders if they were included

---

## 8. Submit Your Catalog

Once tested, submit the `.ifx` package to this project or send it directly.

Helpful information to include:

- catalog name  
- fastener type (bolts, washers, inserts, etc.)  
- standard (ASME, ISO, DIN, etc.)  
- supplier reference if included (Fastenal, McMaster-Carr, etc.)  

Well-structured contributions help build a reusable fastener ecosystem that works consistently inside Creo assemblies and bills of materials.