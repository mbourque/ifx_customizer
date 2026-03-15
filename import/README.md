# Creating Importable Fastener Catalogs

You can contribute premade fastener catalogs to this project. These catalogs can be imported directly into the IFX library and will automatically merge with the existing catalog structure.

Follow the steps below to create a compatible catalog package.

---

## 1. Create the Required Folder Structure

Create a folder named:

parts

Inside this folder create the following two directories:

parts/ifx_catalogs  
parts/ifx_fastener_data

These match the folders used by IFX for catalog definitions and fastener data.

---

## 2. Create or Extend the Catalog Index

Inside `parts/ifx_catalogs` place a file named:

ifx_catalogs.txt

This file lists the catalog entries that should be merged into the user's existing IFX catalog index during import.

If the catalog references a new entry that does not already exist in the user's environment, include the corresponding `.txt` catalog file in this same folder.

Example contents:

#screws  
mcmaster_screws  
metric_socket_head_cap_screws

Each referenced catalog must also have its corresponding catalog definition file present.

---

## 3. Add Fastener Data Files

Place all fastener definition files in:

parts/ifx_fastener_data

Each fastener family requires its `.dat` file containing the INSTANCE table and parameter definitions used by IFX.

Typical contents include:

bolt_hex.dat  
socket_head_cap_screw.dat  
flat_washer.dat  
hex_nut.dat  
dowel_pin.dat

---

## 4. Create the Creo Part Files

Using Creo Parametric 6 and this tool:

1. Generate the fastener parts from the templates.  
2. Ensure the **SYMBOL name matches the Creo part filename**.  
3. Place the generated `.prt` files in the same `ifx_fastener_data` folder.

Example:

parts/ifx_fastener_data/HEX_BOLT.prt  
parts/ifx_fastener_data/HEX_BOLT.dat

Keep naming consistent so IFX can resolve the part correctly during placement.

---

## 5. Package the Library

Once the folders are complete:

1. Zip the `parts` folder.

Example:

parts.zip

2. Rename the extension from `.zip` to `.ifx`.

Example:

metric_socket_bolts.ifx

The `.ifx` file is simply a packaged archive that the catalog manager can import.

---

## 6. Test the Catalog

Before submitting:

1. Import the `.ifx` file using the IFX catalog manager.  
2. Verify the catalog appears under the correct section such as:

#screws  
#washers  
#nuts  
#pins  
#inserts  

3. Place several fasteners in an assembly to confirm:

- sizes appear correctly  
- Creo parts load properly  
- parameters populate correctly  

---

## 7. Submit Your Catalog

Once tested, submit the `.ifx` package to this project or send it to me directly.

Helpful information to include:

- catalog name  
- fastener type such as bolts, washers, or inserts  
- standard such as ASME, ISO, or DIN  
- supplier reference if included such as Fastenal or McMaster  

Well structured contributions help build a reusable fastener ecosystem that works consistently inside Creo assemblies and bills of materials.