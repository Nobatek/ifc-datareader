"""Tests on IFC object entity property set."""

import pytest

from ifc_datareader.ifc_object_entity_pset import (
    IfcObjectEntityPropertySetBase, IfcObjectEntityPropertySet,
    IfcObjectEntityTypePropertySet)
from ifc_datareader.ifc_object_entity_property import (
    IfcObjectEntitySimpleProperty, IfcObjectEntityTypeProperty)


class TestIfcObjectEntityPropertySet:

    def test_ifc_object_entity_pset(self, schema_2x3, sample_ifcos):

        ifc_file = sample_ifcos
        # get an IfcPropertySet, for exmaple at line 221
        raw_obj = ifc_file.by_guid('3XVK9DSXz5VBeIwkdMkNOi')

        pset = IfcObjectEntityPropertySetBase.create(raw_obj, schema_2x3)
        assert isinstance(pset, IfcObjectEntityPropertySet)
        assert pset.name == 'Dimensions' == raw_obj.Name
        assert len(pset.properties) == len(raw_obj.HasProperties)
        for prop in pset.properties:
            assert isinstance(prop, IfcObjectEntitySimpleProperty)
            assert prop.property_set_name == pset.name

        pset_bis = IfcObjectEntityPropertySet(raw_obj, schema_2x3)
        assert pset_bis.name == 'Dimensions' == raw_obj.Name
        assert len(pset_bis.properties) == len(raw_obj.HasProperties)
        for prop in pset_bis.properties:
            assert isinstance(prop, IfcObjectEntitySimpleProperty)
            assert prop.property_set_name == pset_bis.name

        assert pset == pset_bis

        assert '<{}>('.format(pset.__class__.__name__) in repr(pset)

        # get an IfcDoorLiningProperties (IfcPropertySetDefinition), line 49393
        raw_pset_def = ifc_file.by_guid('0gLqRgVw5CUfhJ9lHgf5OT')
        pset_attrs = schema_2x3.get_entity(raw_pset_def.is_a()).attributes

        tpset = IfcObjectEntityPropertySetBase.create(raw_pset_def, schema_2x3)
        assert tpset.name == raw_pset_def.Name
        assert tpset.type_name == raw_pset_def.is_a()
        assert len(tpset.properties) == len(pset_attrs)
        for tprop in tpset.properties:
            assert isinstance(tprop, IfcObjectEntityTypeProperty)

        tpset_bis = IfcObjectEntityTypePropertySet(raw_pset_def, schema_2x3)
        assert tpset_bis.name == raw_pset_def.Name
        assert tpset_bis.type_name == raw_pset_def.is_a()
        assert len(tpset_bis.properties) == len(pset_attrs)
        for tprop in tpset_bis.properties:
            assert isinstance(tprop, IfcObjectEntityTypeProperty)

        assert tpset == tpset_bis

        # all property sets are not equals
        assert pset != tpset
        assert pset_bis != tpset_bis

    def test_ifc_object_entity_pset_errors(self, schema_2x3, sample_ifcos):

        # IfcObjectEntityPropertyBase is an abstract class
        with pytest.raises(TypeError):
            IfcObjectEntityPropertySetBase(None, None)

        # invalid type for raw_data
        with pytest.raises(AttributeError):
            IfcObjectEntityPropertySetBase.create(None, schema_2x3)

        # invalid type for raw_pset
        with pytest.raises(ValueError):
            IfcObjectEntityPropertySet(None, schema_2x3)

        ifc_file = sample_ifcos
        # get an IfcPropertySet, for exmaple at line 221
        raw_obj = ifc_file.by_guid('3XVK9DSXz5VBeIwkdMkNOi')

        # invalid schema is acceptable for instanciation...
        pset = IfcObjectEntityPropertySet(raw_obj, None)
        # ...but not after
        with pytest.raises(AttributeError):
            pset.schema_metadata

        # invalid type for raw_pset_def
        with pytest.raises(ValueError):
            IfcObjectEntityTypePropertySet(None, schema_2x3)

        # get an IfcDoorLiningProperties (IfcPropertySetDefinition), line 49393
        raw_pset_def = ifc_file.by_guid('0gLqRgVw5CUfhJ9lHgf5OT')
        # pset_attrs = schema_2x3.get_entity(raw_pset_def.is_a()).attributes

        # invalid schema is acceptable for instanciation...
        tpset = IfcObjectEntityTypePropertySet(raw_pset_def, None)
        # ...but not after
        with pytest.raises(AttributeError):
            tpset.schema_metadata
