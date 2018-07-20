"""Tests for IFC schema reader tool."""

import pytest

from ifc_datareader.schema import IfcSchema
from ifc_datareader.schema.ifc_schema_objects import (
    IfcSchemaDefinedType, IfcSchemaSelectType, IfcSchemaEnum, IfcSchemaEntity,
    IfcSchemaEntityAttribute, IfcSchemaEntityInverse)


class TestIfcSchemaReader:

    def test_ifc_schema_reader(self):

        ifc_schema = IfcSchema('IFC2X3')
        assert ifc_schema.version == 'IFC2X3'
        assert len(ifc_schema.defined_types) == 117
        assert len(ifc_schema.select_types) == 46
        assert len(ifc_schema.enumerations) == 164
        assert len(ifc_schema.entities) == 653

        # get IfcAreaMeasure defined type (simple defined type)
        def_typ_area = ifc_schema.get_defined_type('IfcAreaMeasure')
        assert isinstance(def_typ_area, IfcSchemaDefinedType)
        assert def_typ_area.name == 'IfcAreaMeasure'
        assert def_typ_area.type_name == 'REAL'
        assert not def_typ_area.is_ref
        assert def_typ_area.ref_type is None

        # get IfcPositiveLengthMeasure defined type (reference defined type)
        def_typ_plm = ifc_schema.get_defined_type('IfcPositiveLengthMeasure')
        assert isinstance(def_typ_plm, IfcSchemaDefinedType)
        assert def_typ_plm.name == 'IfcPositiveLengthMeasure'
        assert def_typ_plm.type_name == '#IfcLengthMeasure'
        assert def_typ_plm.is_ref
        assert def_typ_plm.ref_type.name == 'IfcLengthMeasure'
        assert isinstance(def_typ_plm.ref_type, IfcSchemaDefinedType)

        # get IfcUnit select type
        sel_typ_unit = ifc_schema.get_select_type('IfcUnit')
        assert isinstance(sel_typ_unit, IfcSchemaSelectType)
        assert sel_typ_unit.name == 'IfcUnit'
        assert sel_typ_unit.entity_names == (
            'IfcDerivedUnit', 'IfcMonetaryUnit', 'IfcNamedUnit',)
        assert len(sel_typ_unit.entities) == len(sel_typ_unit.entity_names)
        for cur_ent in sel_typ_unit.entities:
            assert isinstance(cur_ent, IfcSchemaEntity)
        assert sel_typ_unit.entities == (
            ifc_schema.get_entity('IfcDerivedUnit'),
            ifc_schema.get_entity('IfcMonetaryUnit'),
            ifc_schema.get_entity('IfcNamedUnit'),)

        # get IfcWallTypeEnum enumeration
        enum_wt = ifc_schema.get_enumeration('IfcWallTypeEnum')
        assert isinstance(enum_wt, IfcSchemaEnum)
        assert enum_wt.name == 'IfcWallTypeEnum'
        assert enum_wt.values == (
            'ELEMENTEDWALL', 'NOTDEFINED', 'PLUMBINGWALL', 'POLYGONAL',
            'SHEAR', 'STANDARD', 'USERDEFINED',)

        # get IfcObject entity
        ent_obj = ifc_schema.get_entity('IfcObject')
        assert ent_obj.name == 'IfcObject'
        assert ent_obj.supertype_name == 'IfcObjectDefinition'
        assert ent_obj.attribute_names == ('ObjectType',)
        assert ent_obj.not_optional_attribute_names == ()
        assert ent_obj.inverse_names == ('IsDefinedBy',)
        # IfcObject inverse
        ent_obj_inv_idb = ent_obj.get_inverse('IsDefinedBy')
        assert ent_obj_inv_idb.ifc_type_name == 'IfcRelDefines'
        assert ent_obj_inv_idb.ifc_type_info == (
            ifc_schema.get_entity('IfcRelDefines'))
        assert not ent_obj_inv_idb.is_optional
        assert ent_obj_inv_idb.is_set_of
        assert ent_obj_inv_idb.set_of_min == '0'
        assert ent_obj_inv_idb.set_of_max == '?'
        assert ent_obj_inv_idb.is_relation
        assert ent_obj_inv_idb.for_attr == 'RelatedObjects'

        # get IfcObjectDefinition entity
        ent_obj_def = ifc_schema.get_entity('IfcObjectDefinition')
        assert ent_obj_def.name == 'IfcObjectDefinition'
        assert ent_obj_def.supertype_name == 'IfcRoot'
        assert ent_obj_def.attribute_names == ()
        assert ent_obj_def.not_optional_attribute_names == ()
        assert ent_obj_def.inverse_names == (
            'Decomposes', 'HasAssignments', 'HasAssociations',
            'IsDecomposedBy',)
        # IfcObject inverse
        ent_obj_def_inv_d = ent_obj_def.get_inverse('Decomposes')
        assert ent_obj_def_inv_d.ifc_type_name == 'IfcRelDecomposes'
        assert ent_obj_def_inv_d.ifc_type_info == (
            ifc_schema.get_entity('IfcRelDecomposes'))
        assert not ent_obj_def_inv_d.is_optional
        assert ent_obj_def_inv_d.is_set_of
        assert ent_obj_def_inv_d.set_of_min == '0'
        assert ent_obj_def_inv_d.set_of_max == '1'
        assert ent_obj_def_inv_d.is_relation
        assert ent_obj_def_inv_d.for_attr == 'RelatedObjects'

        # get IfcRoot entity
        ent_root = ifc_schema.get_entity('IfcRoot')
        assert ent_root.name == 'IfcRoot'
        assert ent_root.supertype_name is None
        assert ent_root.attribute_names == (
            'Description', 'GlobalId', 'Name', 'OwnerHistory',)
        assert ent_root.not_optional_attribute_names == (
            'GlobalId', 'OwnerHistory',)
        assert ent_root.inverse_names == ()
        # IfcRoot attributes
        ent_root_attr_gid = ent_root.get_attribute('GlobalId')
        assert ent_root_attr_gid.ifc_type_name == 'IfcGloballyUniqueId'
        assert ent_root_attr_gid.ifc_type_info == (
            ifc_schema.get_defined_type('IfcGloballyUniqueId'))
        assert not ent_root_attr_gid.is_optional
        assert not ent_root_attr_gid.is_set_of
        assert ent_root_attr_gid.set_of_min is None
        assert ent_root_attr_gid.set_of_max is None
        ent_root_attr_name = ent_root.get_attribute('Name')
        assert ent_root_attr_name.ifc_type_name == 'IfcLabel'
        assert ent_root_attr_name.ifc_type_info == (
            ifc_schema.get_defined_type('IfcLabel'))
        assert ent_root_attr_name.is_optional
        assert not ent_root_attr_name.is_set_of
        assert ent_root_attr_name.set_of_min is None
        assert ent_root_attr_name.set_of_max is None

        # get IfcProject entity
        ent_prj = ifc_schema.get_entity('IfcProject')
        assert isinstance(ent_prj, IfcSchemaEntity)
        assert ent_prj.name == 'IfcProject'
        assert ent_prj.supertype_name == 'IfcObject'
        assert ent_prj.supertype == ent_obj
        assert ent_prj.attribute_names == (
            'LongName', 'Phase', 'RepresentationContexts', 'UnitsInContext',)
        assert ent_prj.not_optional_attribute_names == (
            'RepresentationContexts', 'UnitsInContext',)
        assert len(ent_prj.attributes) == len(ent_prj.attribute_names)
        for cur_attr in ent_prj.attributes:
            assert isinstance(cur_attr, IfcSchemaEntityAttribute)
        assert ent_prj.inverse_names == ()
        assert len(ent_prj.inverse) == len(ent_prj.inverse_names)
        for cur_inv in ent_prj.inverse:
            assert isinstance(cur_inv, IfcSchemaEntityInverse)

        # IfcProject get_all_attributes
        for cur_prj_attr in ent_prj.get_all_attributes():
            assert isinstance(cur_prj_attr, IfcSchemaEntityAttribute)
            assert cur_prj_attr.name in (
                ent_root.attribute_names + ent_obj_def.attribute_names +
                ent_obj.attribute_names + ent_prj.attribute_names)
        for cur_prj_not_opt_attr in ent_prj.get_all_attributes(
                include_optional=False):
            assert isinstance(cur_prj_not_opt_attr, IfcSchemaEntityAttribute)
            assert cur_prj_not_opt_attr.name in (
                ent_root.not_optional_attribute_names +
                ent_obj_def.not_optional_attribute_names +
                ent_obj.not_optional_attribute_names +
                ent_prj.not_optional_attribute_names)

        # IfcProject get_all_attribute_names
        assert ent_prj.get_all_attribute_names() == (
            ent_root.attribute_names + ent_obj_def.attribute_names +
            ent_obj.attribute_names + ent_prj.attribute_names)
        assert ent_prj.get_all_attribute_names(include_optional=False) == (
            ent_root.not_optional_attribute_names +
            ent_obj_def.not_optional_attribute_names +
            ent_obj.not_optional_attribute_names +
            ent_prj.not_optional_attribute_names)
        assert ent_prj.get_all_attribute_names(
            include_optional=False, include_classname=True) == (
                'IfcRoot.GlobalId', 'IfcRoot.OwnerHistory',
                'IfcProject.RepresentationContexts',
                'IfcProject.UnitsInContext',)

        # IfcProject get_all_inverse
        for cur_prj_inv in ent_prj.get_all_inverse():
            assert isinstance(cur_prj_inv, IfcSchemaEntityInverse)
            assert cur_prj_inv.name in (
                ent_root.inverse_names + ent_obj_def.inverse_names +
                ent_obj.inverse_names + ent_prj.inverse_names)

        # IfcProject get_all_inverse_names
        assert ent_prj.get_all_inverse_names() == (
            ent_root.inverse_names + ent_obj_def.inverse_names +
            ent_obj.inverse_names + ent_prj.inverse_names)
        assert ent_prj.get_all_inverse_names(include_classname=True) == (
            'IfcObjectDefinition.Decomposes',
            'IfcObjectDefinition.HasAssignments',
            'IfcObjectDefinition.HasAssociations',
            'IfcObjectDefinition.IsDecomposedBy', 'IfcObject.IsDefinedBy',)

        # inheritance
        # schema entity_inherits shortcut
        assert ifc_schema.entity_inherits('IfcProject', 'IfcObject')
        assert ifc_schema.entity_inherits(
            'IfcProject', 'IfcObject', deep_inheritance=False)
        assert ifc_schema.entity_inherits('IfcProject', 'IfcRoot')
        assert not ifc_schema.entity_inherits(
            'IfcProject', 'IfcRoot', deep_inheritance=False)
        assert not ifc_schema.entity_inherits('IfcProject', 'IfcUnitEnum')
        assert not ifc_schema.entity_inherits('IfcProject', 'unknown')
        # entity inherits
        assert ent_prj.inherits('IfcObject')
        assert ent_prj.inherits('IfcObject', deep_inheritance=False)
        assert ent_prj.inherits('IfcRoot')
        assert not ent_prj.inherits('IfcRoot', deep_inheritance=False)
        assert not ent_prj.inherits('IfcUnitEnum')
        assert not ent_prj.inherits('IfcUnitEnum', deep_inheritance=False)
        assert not ent_prj.inherits('unknown')
        assert not ent_prj.inherits('unknown', deep_inheritance=False)

        # entity get_subtype_names
        ent_bld_elmt = ifc_schema.get_entity('IfcBuildingElement')
        ent_bld_elmt_subtype_names = ent_bld_elmt.get_subtype_names()
        assert ent_bld_elmt_subtype_names == (
            'IfcBeam', 'IfcBuildingElementComponent',
            'IfcBuildingElementProxy', 'IfcColumn', 'IfcCovering',
            'IfcCurtainWall', 'IfcDoor', 'IfcFooting', 'IfcMember', 'IfcPile',
            'IfcPlate', 'IfcRailing', 'IfcRamp', 'IfcRampFlight', 'IfcRoof',
            'IfcSlab', 'IfcStair', 'IfcStairFlight', 'IfcWall', 'IfcWindow',)
        assert ent_bld_elmt.get_subtype_names(deep_inheritance=True) == (
            'IfcBeam', 'IfcBuildingElementComponent',
            'IfcBuildingElementPart', 'IfcBuildingElementProxy',
            'IfcColumn', 'IfcCovering', 'IfcCurtainWall', 'IfcDoor',
            'IfcFooting', 'IfcMember', 'IfcPile', 'IfcPlate', 'IfcRailing',
            'IfcRamp', 'IfcRampFlight', 'IfcReinforcingBar',
            'IfcReinforcingElement', 'IfcReinforcingMesh', 'IfcRoof',
            'IfcSlab', 'IfcStair', 'IfcStairFlight', 'IfcTendon',
            'IfcTendonAnchor', 'IfcWall', 'IfcWallStandardCase',
            'IfcWindow',)

        # entity get_subtype_names
        ent_bld_elmt_subtypes = ent_bld_elmt.get_subtypes()
        for cur_subtype in ent_bld_elmt_subtypes:
            assert isinstance(cur_subtype, IfcSchemaEntity)
        assert len(ent_bld_elmt_subtypes) == len(ent_bld_elmt_subtype_names)

    def test_ifc_schema_reader_version(
            self, schema_2x3, schema_4, schema_custom_filepath):

        schema_2 = IfcSchema('IFC2X3')
        assert schema_2 == schema_2x3

        assert schema_2x3 != schema_4
        assert schema_2x3 != 'IFC2X3'

        # load a custom schema
        ifc_schema = IfcSchema(None, schema_filepath=schema_custom_filepath)
        assert ifc_schema.version == 'IFC42'
        assert len(ifc_schema.defined_types) == 1
        assert len(ifc_schema.select_types) == 0
        assert len(ifc_schema.enumerations) == 0
        assert len(ifc_schema.entities) == 0

    def test_ifc_schema_reader_errors(self, schema_2x3):

        # load a not supported schema version
        with pytest.raises(ValueError):
            IfcSchema('not_available_schema')

        # unknown defined type
        with pytest.raises(KeyError):
            schema_2x3.get_defined_type('unknown')
        # unknown select type
        with pytest.raises(KeyError):
            schema_2x3.get_select_type('unknown')
        # unknown enumeration
        with pytest.raises(KeyError):
            schema_2x3.get_enumeration('unknown')
        # unknown entity
        with pytest.raises(KeyError):
            schema_2x3.get_entity('unknown')

        # unknown entity
        with pytest.raises(KeyError):
            schema_2x3.entity_inherits('unknown', 'IfcObject')
