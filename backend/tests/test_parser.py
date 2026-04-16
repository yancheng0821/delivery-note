"""Tests for parser module."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from parser import parse_material_excel

FIXTURE_PATH = os.path.join(os.path.dirname(__file__), "采购材料清单.xlsx")


def test_parse_returns_list():
    result = parse_material_excel(FIXTURE_PATH)
    assert isinstance(result, list)
    assert len(result) > 0


def test_parse_first_item_fields():
    result = parse_material_excel(FIXTURE_PATH)
    first = result[0]
    assert first["index"] == 1
    assert first["material_name"] == "弹簧式安全阀"
    assert first["spec"] == "A27W-16T DN20 整定压力0.84MPA"
    assert first["quantity"] == 3.0
    assert first["unit"] == "个"
    assert isinstance(first["unit_price"], float)
    assert isinstance(first["amount"], float)


def test_parse_skips_empty_material_name():
    result = parse_material_excel(FIXTURE_PATH)
    for item in result:
        assert item["material_name"] is not None
        assert item["material_name"].strip() != ""


def test_parse_numeric_fields_are_float():
    result = parse_material_excel(FIXTURE_PATH)
    for item in result:
        assert isinstance(item["unit_price"], float)
        assert isinstance(item["quantity"], float)
        assert isinstance(item["amount"], float)


def test_parse_amount_calculated_from_price_and_qty():
    """amount should equal unit_price * quantity."""
    result = parse_material_excel(FIXTURE_PATH)
    for item in result:
        expected = round(item["unit_price"] * item["quantity"], 2)
        assert item["amount"] == expected
