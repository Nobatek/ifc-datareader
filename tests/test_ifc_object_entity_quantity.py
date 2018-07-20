"""Tests on IFC object entity quantity."""

import pytest

from ifc_datareader.ifc_object_entity_quantity import (
    IfcObjectEntityQuantityBase, IfcObjectEntitySimpleQuantity)


class TestIfcObjectEntityQuantity:

    def test_ifc_object_entity_quantity(self, schema_2x3, sample_ifcos):

        ifc_file = sample_ifcos
        # get an IfcElementQuantity, for exmaple at line 129
        raw_obj = ifc_file.by_guid('0y1XPVQ2bFi962bGE5XTfW')

        raw_qty = raw_obj.Quantities[0]
        quantity = IfcObjectEntitySimpleQuantity(raw_qty, schema_2x3)
        assert quantity.name == raw_qty.Name
        assert quantity.value == raw_qty.AreaValue
        assert quantity.unit == raw_qty.Unit

        quantity2 = IfcObjectEntityQuantityBase.create(raw_qty, schema_2x3)
        assert isinstance(quantity2, IfcObjectEntitySimpleQuantity)
        assert quantity2.name == quantity.name
        assert quantity2.value == quantity.value
        assert quantity2.unit == quantity.unit

        assert quantity == quantity2

        assert repr(quantity) == (
            '<{self.__class__.__name__}>('
            'schema_version={self.schema_version}'
            ', type_name="{self.type_name}"'
            ', name="{self.name}"'
            ', codename="{self.codename}"'
            ', description="{self.description}"'
            ', value={self.value}'
            ', unit="{self.unit}"'
            ')'.format(self=quantity))

    def test_ifc_object_entity_quantity_errors(self, schema_2x3, sample_ifcos):

        # IfcObjectEntityQuantityBase is an abstract class
        with pytest.raises(TypeError):
            IfcObjectEntityQuantityBase(None, None)

        # invalid type for raw_data
        with pytest.raises(ValueError):
            IfcObjectEntitySimpleQuantity(None, None)

        ifc_file = sample_ifcos
        raw_obj = ifc_file.by_type('IfcSite')[0]
        # IfcSite not in expected_types
        with pytest.raises(ValueError):
            IfcObjectEntitySimpleQuantity(raw_obj, schema_2x3)
