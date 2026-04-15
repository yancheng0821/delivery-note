"""Generate delivery note Excel files from template."""

import math
from copy import copy
from datetime import date
from io import BytesIO

import openpyxl


def split_amount_digits(amount: float) -> list:
    """Split an amount into 8 digit positions: 拾万,万,仟,佰,拾,元,角,分.

    Returns a list of 8 elements. Leading zeros are None, trailing zeros are 0.
    """
    amount = round(amount, 2)

    int_part = int(amount)
    dec_part = round((amount - int_part) * 100)

    jiao = dec_part // 10
    fen = dec_part % 10

    digits = []
    for divisor in [100000, 10000, 1000, 100, 10, 1]:
        digits.append(int_part // divisor)
        int_part = int_part % divisor

    digits.append(jiao)
    digits.append(fen)

    # Replace leading zeros with None (keep 元 position at index 5)
    result = []
    leading = True
    for i, d in enumerate(digits):
        if leading and d == 0 and i < 5:
            result.append(None)
        else:
            leading = False
            result.append(d)

    return result


# Template row offsets
# Copy 1 starts at row 2, Copy 2 starts at row 22
COPY_START_ROWS = [2, 22]
DATE_ROW_OFFSET = 2       # row 4 = 2+2
CUSTOMER_ROW_OFFSET = 3   # row 5
ADDRESS_ROW_OFFSET = 4    # row 6
ITEM_START_OFFSET = 7     # row 9 = 2+7
ITEM_COUNT = 6
TOTAL_ROW_OFFSET = 13     # row 15 = 2+13


def _fill_copy(ws, copy_start_row: int, customer: dict, materials: list[dict],
               order_number: str, today: date):
    """Fill one copy of the delivery note template."""
    date_str = f"                                 {today.year}      {today.month:02d}      {today.day:02d}日"
    ws.cell(row=copy_start_row + DATE_ROW_OFFSET, column=2).value = date_str

    ws.cell(row=copy_start_row + CUSTOMER_ROW_OFFSET, column=2).value = f"客户名称：{customer['name']}"
    ws.cell(row=copy_start_row + CUSTOMER_ROW_OFFSET, column=4).value = f"                    编号：{order_number}"

    addr = customer.get("address", "")
    contact = customer.get("contact", "")
    phone = customer.get("phone", "")
    ws.cell(row=copy_start_row + ADDRESS_ROW_OFFSET, column=2).value = (
        f"发往地址：{addr}                                             联系人：{contact}      电话：{phone}"
    )

    page_total = 0.0
    for i in range(ITEM_COUNT):
        row = copy_start_row + ITEM_START_OFFSET + i
        if i < len(materials):
            mat = materials[i]
            amount = round(mat["unit_price"] * mat["quantity"], 2)
            page_total += amount

            ws.cell(row=row, column=2).value = i + 1
            name_spec = mat["material_name"]
            if mat.get("spec"):
                name_spec += " " + mat["spec"]
            ws.cell(row=row, column=3).value = name_spec
            ws.cell(row=row, column=4).value = f"{int(mat['quantity'])}/{mat['unit']}"
            ws.cell(row=row, column=5).value = mat["unit_price"]

            digits = split_amount_digits(amount)
            for col_idx, digit in enumerate(digits):
                ws.cell(row=row, column=6 + col_idx).value = digit
        else:
            ws.cell(row=row, column=2).value = None
            ws.cell(row=row, column=3).value = None
            ws.cell(row=row, column=4).value = None
            ws.cell(row=row, column=5).value = None
            for col_idx in range(8):
                ws.cell(row=row, column=6 + col_idx).value = None

    total_row = copy_start_row + TOTAL_ROW_OFFSET
    total_digits = split_amount_digits(page_total)
    for col_idx, digit in enumerate(total_digits):
        ws.cell(row=total_row, column=6 + col_idx).value = digit


def _delete_rows(ws, start_row: int, count: int):
    """Delete rows by clearing content and shifting remaining rows up."""
    ws.delete_rows(start_row, count)


def _copy_template_rows(ws, source_start: int, dest_start: int, row_count: int):
    """Copy rows from source to destination, preserving values and basic formatting."""
    for i in range(row_count):
        src_row = source_start + i
        dst_row = dest_start + i
        if ws.row_dimensions[src_row].height:
            ws.row_dimensions[dst_row].height = ws.row_dimensions[src_row].height
        for col in range(1, ws.max_column + 1):
            src_cell = ws.cell(row=src_row, column=col)
            dst_cell = ws.cell(row=dst_row, column=col)
            dst_cell.value = src_cell.value
            if src_cell.has_style:
                dst_cell.font = copy(src_cell.font)
                dst_cell.border = copy(src_cell.border)
                dst_cell.fill = copy(src_cell.fill)
                dst_cell.number_format = src_cell.number_format
                dst_cell.protection = copy(src_cell.protection)
                dst_cell.alignment = copy(src_cell.alignment)


def generate_delivery_note(customer: dict, materials: list[dict],
                           template_path: str) -> BytesIO:
    """Generate a delivery note Excel from template."""
    wb = openpyxl.load_workbook(template_path)
    ws = wb.active

    today = date.today()
    total_pages = math.ceil(len(materials) / ITEM_COUNT)

    # Fill existing template copies
    for page_idx in range(min(total_pages, len(COPY_START_ROWS))):
        start = page_idx * ITEM_COUNT
        page_materials = materials[start:start + ITEM_COUNT]
        order_number = f"{today.strftime('%Y%m%d')}-{page_idx + 1:03d}"
        _fill_copy(ws, COPY_START_ROWS[page_idx], customer, page_materials,
                   order_number, today)

    # Handle additional pages beyond the 2 template copies
    if total_pages > len(COPY_START_ROWS):
        for page_idx in range(len(COPY_START_ROWS), total_pages):
            new_start_row = COPY_START_ROWS[-1] + (page_idx - len(COPY_START_ROWS) + 1) * 20
            _copy_template_rows(ws, source_start=2, dest_start=new_start_row, row_count=16)
            start = page_idx * ITEM_COUNT
            page_materials = materials[start:start + ITEM_COUNT]
            order_number = f"{today.strftime('%Y%m%d')}-{page_idx + 1:03d}"
            _fill_copy(ws, new_start_row, customer, page_materials,
                       order_number, today)

    # Delete unused template copies (delete from bottom to avoid row shift issues)
    for page_idx in range(len(COPY_START_ROWS) - 1, total_pages - 1, -1):
        # Each copy occupies rows: copy_start_row to copy_start_row + 15 (16 rows)
        # Plus gap rows between copies (rows 18-21 for copy1, etc.)
        copy_start = COPY_START_ROWS[page_idx]
        # Delete from the row before copy start (gap) to end of copy
        if page_idx == 1:
            # Copy 2: delete rows 18-37 (gap + copy2)
            _delete_rows(ws, 18, 20)
        elif page_idx == 0:
            # Copy 1: delete rows 1-17
            _delete_rows(ws, 1, 17)

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    wb.close()
    return output
