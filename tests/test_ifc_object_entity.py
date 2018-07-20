"""Tests on IfcObjectEntity"""

import pytest

from ifc_datareader.ifc_object_entity import IfcObjectEntity
from ifc_datareader.ifc_object_entity_pset import (
    IfcObjectEntityPropertySetBase)
from ifc_datareader.ifc_object_entity_quantity import (
    IfcObjectEntityQuantityBase)
from ifc_datareader.ifc_object_entity_property import (
    IfcObjectEntityPropertyBase)


class TestIfcObjectEntity():

    def test_ifc_object_entity(self, schema_2x3, sample_ifcos):

        ifc_file = sample_ifcos
        # get an IfSpace, for example at line 124
        obj_id = '3VbjARZ9f3feA5ls423TIy'
        raw_obj = ifc_file.by_guid(obj_id)

        obj_ent = IfcObjectEntity(raw_obj, schema_2x3)
        assert obj_ent.global_id == obj_id == raw_obj.GlobalId
        assert obj_ent.name == '42' == raw_obj.Name
        assert obj_ent.type_name == 'IfcSpace' == raw_obj.is_a()
        assert obj_ent.composition_type == 'ELEMENT'
        assert obj_ent.is_element
        assert obj_ent.object_type is None

        assert '<{}>('.format(obj_ent.__class__.__name__) in repr(obj_ent)

        # get parent raw object
        parent_raw_obj = ifc_file.by_guid('3bhrzEe_P3q8bqpKn5gzPC')
        parent_ent = IfcObjectEntity(parent_raw_obj, schema_2x3)
        assert obj_ent.parent is not None
        assert isinstance(obj_ent.parent, IfcObjectEntity)
        assert obj_ent.parent == parent_ent
        # current entity should be in parent kids
        assert obj_ent in parent_ent.kids

        assert obj_ent.kids == ()

        assert len(obj_ent.property_sets) == 6
        for pset in obj_ent.property_sets:
            assert isinstance(pset, IfcObjectEntityPropertySetBase)
        # get related IfcPropertySet (at line 221)
        raw_pset = ifc_file.by_guid('3XVK9DSXz5VBeIwkdMkNOi')
        pset = IfcObjectEntityPropertySetBase.create(raw_pset, schema_2x3)
        assert obj_ent.property_sets[0] == pset

        assert len(obj_ent.quantities) == 1
        for quantity in obj_ent.quantities:
            assert isinstance(quantity, IfcObjectEntityQuantityBase)
        # get related IfcElementQuantity (at line 129)
        raw_qties = ifc_file.by_guid('0y1XPVQ2bFi962bGE5XTfW')
        quantity_bis = IfcObjectEntityQuantityBase.create(
            raw_qties.Quantities[0], schema_2x3)
        assert obj_ent.quantities[0] == quantity_bis

        pset_codenames = obj_ent.get_property_set_codenames()
        assert len(pset_codenames) == len(obj_ent.property_sets)
        for pset_codename in pset_codenames:
            assert isinstance(obj_ent.get_property_set(pset_codename),
                              IfcObjectEntityPropertySetBase)
        assert obj_ent.get_property_set('unknown') is None

        prop_codenames = obj_ent.get_property_codenames()
        props = obj_ent.get_properties()
        assert len(prop_codenames) == len(props)
        for prop_codename in prop_codenames:
            prop = obj_ent.get_property(prop_codename)
            assert isinstance(prop, IfcObjectEntityPropertyBase)
            assert prop in props
        assert obj_ent.get_property('unknown') is None

        pset = obj_ent.property_sets[0]
        other_pset = obj_ent.property_sets[1]
        assert pset != other_pset
        prop_cns = obj_ent.get_property_codenames(pset_codename=pset.codename)
        other_prop_cns = obj_ent.get_property_codenames(
            pset_codename=other_pset.codename)
        assert prop_cns != other_prop_cns
        props = obj_ent.get_properties(pset_codename=pset.codename)
        assert props == pset.properties
        other_props = obj_ent.get_properties(pset_codename=other_pset.codename)
        assert other_props == other_pset.properties
        assert props != other_props
        assert len(prop_cns) == len(props)
        assert len(other_prop_cns) == len(other_props)
        for prop_cn in prop_cns:
            prop = obj_ent.get_property(prop_cn)
            assert isinstance(prop, IfcObjectEntityPropertyBase)
            assert prop in props
            assert prop not in other_props
        for other_prop_cn in other_prop_cns:
            prop = obj_ent.get_property(other_prop_cn)
            assert isinstance(prop, IfcObjectEntityPropertyBase)
            assert prop in other_props
            assert prop not in props

        prop = pset.properties[0]
        assert obj_ent.get_property_value(prop.codename) == \
            (prop.value, prop.unit,)
        assert obj_ent.get_property_value(
            prop.codename, pset_codename=pset.codename) == \
            (prop.value, prop.unit,)
        assert obj_ent.get_property_value(
            prop.codename, pset_codename='unknown') == (None, None,)

    def test_ifc_object_entity_errors(self, schema_2x3, sample_ifcos):

        # load a non valid ifcopenshell entity instance
        with pytest.raises(ValueError):
            IfcObjectEntity('wrong', schema_2x3)

        ifc_file = sample_ifcos
        # get an IfSpace, for example at line 124
        raw_obj = ifc_file.by_guid('3VbjARZ9f3feA5ls423TIy')

        # invalid schema is acceptable for instanciation...
        obj_ent = IfcObjectEntity(raw_obj, None)
        # ...until it is needed
        with pytest.raises(AttributeError):
            obj_ent.schema_metadata
