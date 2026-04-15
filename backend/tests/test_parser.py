"""Tests for parser module."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from parser import parse_material_excel

FIXTURE_PATH = os.path.join(os.path.dirname(__file__), "物料申请清单.xlsx")


def test_parse_returns_list():
    result = parse_material_excel(FIXTURE_PATH)
    assert isinstance(result, list)
    assert len(result) > 0


def test_parse_first_item_fields():
    result = parse_material_excel(FIXTURE_PATH)
    first = result[0]
    assert first["index"] == 1
    assert first["purchase_date"] == "2026.3.24"
    assert first["submitter"] == "程文强"
    assert first["device_name"] == "空压机"
    assert first["material_name"] == "磁力启动器"
    assert first["spec"] == "【QCX5-22】5.5-7.5KW_380V空压机"
    assert first["unit_price"] == 120.0
    assert first["quantity"] == 5.0
    assert first["unit"] == "套"
    assert first["amount"] == 600.0


def test_parse_skips_empty_material_name():
    result = parse_material_excel(FIXTURE_PATH)
    for item in result:
        assert item["material_name"] is not None
        assert item["material_name"].strip() != ""


def test_parse_inherits_merged_fields():
    """Row 3 (空压机地脚轮 7寸) has no B/C/D — should inherit from row 2."""
    result = parse_material_excel(FIXTURE_PATH)
    second = result[1]  # index=2, 空压机地脚轮 7寸
    assert second["material_name"] == "空压机地脚轮"
    assert second["purchase_date"] == "2026.3.24"
    assert second["submitter"] == "程文强"
    assert second["device_name"] == "空压机"


def test_parse_string_numbers_converted():
    """Some rows have string values for 单价/数量. Should be converted to float."""
    result = parse_material_excel(FIXTURE_PATH)
    for item in result:
        assert isinstance(item["unit_price"], float)
        assert isinstance(item["quantity"], float)
        assert isinstance(item["amount"], float)
