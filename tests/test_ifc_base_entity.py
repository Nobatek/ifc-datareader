"""Tests on IfcBaseEntity"""

import pytest

from ifc_datareader.ifc_base_entity import IfcBaseEntity
from ifc_datareader.schema import IfcSchemaEntity


class IfcCustomEntity(IfcBaseEntity):
    def __init__(self, raw_entity, schema, *, check_types=('IfcObject',)):
        super().__init__(raw_entity, schema, expected_types=check_types)


class TestIfcBaseEntity:

    def test_ifc_base_entity(self, schema_2x3, sample_ifcos):

        ifc_file = sample_ifcos
        raw_obj = ifc_file.by_type('IfcProject')[0]
        raw_info = raw_obj.get_info()

        custom_ent = IfcCustomEntity(raw_obj, schema_2x3)

        assert custom_ent._schema == schema_2x3
        assert custom_ent.schema_version == schema_2x3.version
        assert custom_ent._raw == raw_obj
        assert custom_ent.type_name == raw_info['type'] == 'IfcProject'
        assert custom_ent.global_id == raw_info['GlobalId'] == raw_obj.GlobalId
        assert custom_ent.name == raw_info['Name'] == raw_obj.Name
        assert custom_ent.description == raw_info['Description'] == \
            raw_obj.Description
        assert custom_ent.codename == custom_ent.name.lower().replace(
            ' ', '_').replace('(', '').replace(')', '')

        assert isinstance(custom_ent.schema_metadata, IfcSchemaEntity)
        assert custom_ent.schema_metadata.name == 'IfcProject'

        assert repr(custom_ent) == (
            '<{self.__class__.__name__}>('
            'schema_version={self.schema_version}'
            ', type="{self.type_name}"'
            ', name="{self.name}"'
            ', codename="{self.codename}"'
            ', description="{self.description}"'
            ')'.format(self=custom_ent))

        other_raw_obj = ifc_file.by_type('IfcSite')[0]
        assert other_raw_obj != raw_obj

    def test_ifc_base_entity_errors(self, schema_2x3, sample_ifcos):

        # IfcBaseEntity is an abstract class
        with pytest.raises(TypeError):
            IfcBaseEntity(None, None)

        # invalid type for raw_obj_entity
        with pytest.raises(ValueError):
            IfcCustomEntity(None, None)

        ifc_file = sample_ifcos
        raw_obj = ifc_file.by_type('IfcProject')[0]
        # invalid expected_types
        with pytest.raises(ValueError):
            IfcCustomEntity(raw_obj, schema_2x3, check_types='IfcObject')
