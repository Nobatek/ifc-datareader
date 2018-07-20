"""Tests on IFC object entity property."""

import pytest

from ifc_datareader.ifc_object_entity_property import (
    IfcObjectEntityPropertyBase, IfcObjectEntitySimpleProperty,
    IfcObjectEntityTypeProperty)


class TestIfcObjectEntityProperty:

    def test_ifc_object_entity_property(self, schema_2x3, sample_ifcos):

        ifc_file = sample_ifcos
        # get an IfcPropertySet, for exmaple at line 221
        raw_obj = ifc_file.by_guid('3XVK9DSXz5VBeIwkdMkNOi')

        # get a single property (IfcSimpleProperty)
        raw_prop = raw_obj.HasProperties[0]

        # automatically instanciate property with create class method
        prop = IfcObjectEntityPropertyBase.create(raw_prop, schema_2x3)
        assert isinstance(prop, IfcObjectEntitySimpleProperty)
        assert prop.property_set is None
        assert prop.property_set_name is None
        assert prop.value == 4000.0 == raw_prop.NominalValue.wrappedValue
        assert prop.value_type_name == 'IfcLengthMeasure' == \
            raw_prop.NominalValue.is_a()
        assert prop.unit is None and prop.unit == raw_prop.Unit

        # same property, created manually
        prop_bis = IfcObjectEntitySimpleProperty(raw_prop, schema_2x3)
        assert prop_bis.property_set is None
        assert prop_bis.property_set_name is None
        assert prop_bis.value == 4000.0 == raw_prop.NominalValue.wrappedValue
        assert prop_bis.value_type_name == 'IfcLengthMeasure' == \
            raw_prop.NominalValue.is_a()
        assert prop_bis.unit is None and prop.unit == raw_prop.Unit

        assert prop == prop_bis

        assert repr(prop) == (
            '<{self.__class__.__name__}>('
            'schema_version={self.schema_version}'
            ', type_name="{self.type_name}"'
            ', name="{self.name}"'
            ', codename="{self.codename}"'
            ', description="{self.description}"'
            ', value={self.value}'
            ', unit="{self.unit}"'
            ', value_type_name="{self.value_type_name}"'
            ', property_set_name="{self.property_set_name}"'
            ')'.format(self=prop))

        # IfcPropertySet inherits from IfcPropertySetDefinition
        # so it works also to create IfcObjectEntityTypeProperty instances...
        assert raw_obj.is_a('IfcPropertySetDefinition')
        pattr = schema_2x3.get_entity(raw_obj.is_a()).attributes[0]
        # automatically instanciate type property with create class method
        tprop = IfcObjectEntityPropertyBase.create(
            raw_obj, schema_2x3, prop_name=pattr.name)
        assert isinstance(tprop, IfcObjectEntityTypeProperty)
        assert tprop.name == pattr.name
        assert tprop.value == raw_obj[pattr.name]
        assert tprop.value_type_name == pattr.ifc_type_name

        # same thing, creating manually
        tprop_bis = IfcObjectEntityTypeProperty(
            raw_obj, pattr.name, schema_2x3)
        assert tprop_bis.name == pattr.name
        assert tprop_bis.value == raw_obj[pattr.name]
        assert tprop_bis.value_type_name == pattr.ifc_type_name

        assert tprop == tprop_bis

        # IfcObjectEntityTypeProperty again with another raw data
        # get an IfcDoorLiningProperties (IfcPropertySetDefinition), line 49393
        raw_pset_def = ifc_file.by_guid('0gLqRgVw5CUfhJ9lHgf5OT')

        # automatically (create method)
        pattr = schema_2x3.get_entity(raw_pset_def.is_a()).attributes[0]
        tprop2 = IfcObjectEntityPropertyBase.create(
            raw_pset_def, schema_2x3, prop_name=pattr.name)
        assert isinstance(tprop2, IfcObjectEntityTypeProperty)
        assert tprop2.name == pattr.name
        assert tprop2.value == raw_pset_def[pattr.name]
        assert tprop2.value_type_name == pattr.ifc_type_name

        # manually (class instanciation)
        tprop2_bis = IfcObjectEntityTypeProperty(
            raw_pset_def, pattr.name, schema_2x3)
        assert tprop2_bis.name == pattr.name
        assert tprop2_bis.value == raw_pset_def[pattr.name]
        assert tprop2_bis.value_type_name == pattr.ifc_type_name

        assert tprop2 == tprop2_bis

        # all props are not equals
        assert prop != tprop and prop_bis != tprop_bis
        assert prop != tprop2 and prop_bis != tprop2_bis
        assert tprop != tprop2 and tprop_bis != tprop2_bis

    def test_ifc_object_entity_property_errors(self, schema_2x3, sample_ifcos):

        # IfcObjectEntityPropertyBase is an abstract class
        with pytest.raises(TypeError):
            IfcObjectEntityPropertyBase(None, None)

        # invalid type for raw_data
        with pytest.raises(AttributeError):
            IfcObjectEntityPropertyBase.create(None, schema_2x3)

        # invalid type for raw_property
        with pytest.raises(ValueError):
            IfcObjectEntitySimpleProperty(None, schema_2x3)

        ifc_file = sample_ifcos
        # get an IfcPropertySet, for exmaple at line 221
        raw_obj = ifc_file.by_guid('3XVK9DSXz5VBeIwkdMkNOi')
        # get a single property (IfcSimpleProperty)
        raw_prop = raw_obj.HasProperties[0]

        # invalid schema is acceptable for instanciation...
        prop = IfcObjectEntitySimpleProperty(raw_prop, None)
        # ...but not after
        with pytest.raises(AttributeError):
            prop.schema_metadata

        raw_pset_def = ifc_file.by_guid('0gLqRgVw5CUfhJ9lHgf5OT')
        pattr = schema_2x3.get_entity(raw_pset_def.is_a()).attributes[0]

        # invalid type for raw_type_pset
        with pytest.raises(ValueError):
            IfcObjectEntityTypeProperty(None, pattr.name, schema_2x3)

        # invalid schema is acceptable for instanciation...
        tprop = IfcObjectEntityTypeProperty(raw_pset_def, pattr.name, None)
        # ...but not after
        with pytest.raises(AttributeError):
            tprop.schema_metadata

        # invalid property name
        tprop = IfcObjectEntityTypeProperty(raw_pset_def, None, schema_2x3)
        with pytest.raises(AttributeError):
            tprop.codename
