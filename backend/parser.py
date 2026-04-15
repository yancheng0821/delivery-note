"""Parse material purchase Excel files."""

import openpyxl


def parse_material_excel(file_path: str) -> list[dict]:
    """Parse a material purchase Excel file and return a list of material dicts.

    Handles merged cells by inheriting values from the previous row
    for columns B (purchase_date), C (submitter), D (device_name).
    """
    wb = openpyxl.load_workbook(file_path, data_only=True)
    ws = wb.active

    materials = []
    last_purchase_date = None
    last_submitter = None
    last_device_name = None

    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        # Column E = material_name (index 4)
        material_name = row[4].value
        if not material_name or str(material_name).strip() == "":
            continue

        material_name = str(material_name).strip()

        # Inherit merged fields
        purchase_date = row[1].value
        if purchase_date is not None:
            last_purchase_date = str(purchase_date).strip()
        submitter = row[2].value
        if submitter is not None:
            last_submitter = str(submitter).strip()
        device_name = row[3].value
        if device_name is not None:
            last_device_name = str(device_name).strip()

        # Parse numeric fields — may be string or number
        raw_price = row[9].value  # Column J
        raw_qty = row[10].value   # Column K
        unit = row[11].value      # Column L

        try:
            unit_price = float(raw_price) if raw_price is not None else 0.0
        except (ValueError, TypeError):
            unit_price = 0.0

        try:
            quantity = float(raw_qty) if raw_qty is not None else 0.0
        except (ValueError, TypeError):
            quantity = 0.0

        amount = round(unit_price * quantity, 2)

        spec = row[5].value  # Column F
        spec = str(spec).strip() if spec else ""

        remark = row[14].value  # Column O
        remark = str(remark).strip() if remark else ""

        materials.append({
            "index": len(materials) + 1,
            "purchase_date": last_purchase_date or "",
            "submitter": last_submitter or "",
            "device_name": last_device_name or "",
            "material_name": material_name,
            "spec": spec,
            "unit_price": unit_price,
            "quantity": quantity,
            "unit": str(unit).strip() if unit else "",
            "amount": amount,
            "remark": remark,
        })

    wb.close()
    return materials
