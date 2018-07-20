"""Tests on IFC schema elements."""

import pytest

from ifc_datareader.schema.ifc_schema_objects import (
    IfcSchemaBaseObject,
    IfcSchemaDefinedType, IfcSchemaSelectType, IfcSchemaEnum,
    IfcSchemaEntity, IfcSchemaEntityAttribute, IfcSchemaEntityInverse)


class TestIfcSchemaBaseElement:

    def test_ifc_schema_base_object(self, schema_2x3, schema_4):

        class IfcSchemaElt(IfcSchemaBaseObject):
            def __init__(self, name, schema):
                super().__init__(name, schema)

        schema_elt = IfcSchemaElt('fifth_element', schema_2x3)
        assert schema_elt.name == 'fifth_element'
        assert schema_elt.schema == schema_2x3

        assert repr(schema_elt) == (
            '<{self.__class__.__name__}>('
            'name="{self.name}"'
            ', schema={self.schema}'
            ')'.format(self=schema_elt))

        schema_elt_doppleganger = IfcSchemaElt('fifth_element', schema_2x3)
        assert schema_elt_doppleganger == schema_elt

        schema_elt_fakefriend = IfcSchemaElt('fifth_element', schema_4)
        assert schema_elt_fakefriend != schema_elt

        assert schema_elt != 'fifth_element'

    def test_ifc_schema_base_object_errors(self):

        # IfcSchemaBaseObject is an abstract class
        with pytest.raises(TypeError):
            IfcSchemaBaseObject(None, None)


class TestIfcSchemaDefinedType:

    def test_ifc_schema_defined_type(self, schema_2x3):

        def_type = IfcSchemaDefinedType('IfcLengthMeasure', 'REAL', schema_2x3)
        assert def_type.name == 'IfcLengthMeasure'
        assert def_type.schema == schema_2x3
        assert def_type.type_name == 'REAL'
        assert not def_type.is_ref
        assert def_type.ref_type is None

        assert repr(def_type) == (
            '<{self.__class__.__name__}>('
            'name="{self.name}"'
            ', type_name="{self.type_name}"'
            ', is_ref={self.is_ref}'
            ', ref_type={self.ref_type}'
            ')'.format(self=def_type))

        other_def_type = IfcSchemaDefinedType(
            'IfcPositiveLengthMeasure', 'IfcLengthMeasure', schema_2x3)
        assert other_def_type.name == 'IfcPositiveLengthMeasure'
        assert other_def_type.schema == schema_2x3
        assert other_def_type.type_name == '#IfcLengthMeasure'
        assert other_def_type.is_ref
        assert other_def_type.ref_type == def_type

    def test_ifc_schema_defined_type_errors(self, schema_2x3):

        bad_def_type = IfcSchemaDefinedType(
            'IfcCustom', 'bad_raw_val', schema_2x3)
        assert bad_def_type.name == 'IfcCustom'
        assert bad_def_type.schema == schema_2x3
        # /!\ as raw_value is not one of _SIMPLE_TYPES, it is considered as
        #  a reference to another defined type...
        assert bad_def_type.type_name == '#bad_raw_val'
        assert bad_def_type.is_ref
        # ...that is undefined
        with pytest.raises(KeyError):
            bad_def_type.ref_type


class TestIfcSchemaSelectType:

    def test_ifc_schema_select_type(self, schema_2x3):

        raw_types = 'IfcDerivedUnit\n\t,IfcNamedUnit\n\t,IfcMonetaryUnit'
        sel_type = IfcSchemaSelectType('IfcUnit', raw_types, schema_2x3)
        assert sel_type.name == 'IfcUnit'
        assert sel_type.schema == schema_2x3
        assert sel_type._raw_types == raw_types
        assert sel_type.entity_names == (
            'IfcDerivedUnit', 'IfcMonetaryUnit', 'IfcNamedUnit',)
        assert len(sel_type.entities) == 3
        for ent in sel_type.entities:
            assert isinstance(ent, IfcSchemaEntity)
        assert sel_type.entities[0].name == 'IfcDerivedUnit'
        assert sel_type.entities[1].name == 'IfcMonetaryUnit'
        assert sel_type.entities[2].name == 'IfcNamedUnit'

        assert repr(sel_type) == (
            '<{self.__class__.__name__}>('
            'name="{self.name}"'
            ', entity_names={self.entity_names}'
            ')'.format(self=sel_type))

    def test_ifc_schema_select_type_errors(self, schema_2x3):

        bad_sel_type = IfcSchemaSelectType('IfcCustom', None, schema_2x3)
        assert bad_sel_type.name == 'IfcCustom'
        assert bad_sel_type.schema == schema_2x3
        assert bad_sel_type._raw_types is None
        # /!\ as raw_types is None, no entity names could be found...
        with pytest.raises(AttributeError):
            bad_sel_type.entity_names
        with pytest.raises(AttributeError):
            bad_sel_type.entities

        bad_sel_type = IfcSchemaSelectType('IfcCustom', 'IfcBad', schema_2x3)
        assert bad_sel_type.name == 'IfcCustom'
        assert bad_sel_type.schema == schema_2x3
        assert bad_sel_type._raw_types == 'IfcBad'
        assert bad_sel_type.entity_names == ('IfcBad',)
        # /!\ as raw_types is unknown, no entity instance could be found...
        with pytest.raises(KeyError):
            bad_sel_type.entities


class TestIfcSchemaEnum:

    def test_ifc_schema_enum(self, schema_2x3):

        raw_values = 'WATER\n\t,STEAM\n\t,USERDEFINED\n\t,NOTDEFINED'
        enum = IfcSchemaEnum('IfcBoilerTypeEnum', raw_values, schema_2x3)
        assert enum.name == 'IfcBoilerTypeEnum'
        assert enum.schema == schema_2x3
        assert enum._raw_values == raw_values
        assert enum.values == ('NOTDEFINED', 'STEAM', 'USERDEFINED', 'WATER',)

        assert repr(enum) == (
            '<{self.__class__.__name__}>('
            'name="{self.name}"'
            ', values={self.values}'
            ')'.format(self=enum))

    def test_ifc_schema_enum_errors(self, schema_2x3):

        bad_enum = IfcSchemaEnum('IfcCustom', None, schema_2x3)
        assert bad_enum.name == 'IfcCustom'
        assert bad_enum.schema == schema_2x3
        assert bad_enum._raw_values is None
        # /!\ as raw_values is None, no enum values could be found...
        with pytest.raises(AttributeError):
            bad_enum.values


class TestIfcSchemaEntityAttribute:

    def test_ifc_schema_entity_attribute(self, ifc_root_entity, schema_2x3):

        ent_attr = IfcSchemaEntityAttribute(
            'RefLatitude', 'OPTIONAL IfcCompoundPlaneAngleMeasure',
            ifc_root_entity)
        assert ent_attr.name == 'RefLatitude'
        assert ent_attr.schema == ifc_root_entity.schema == schema_2x3
        assert ent_attr._raw_type == 'OPTIONAL IfcCompoundPlaneAngleMeasure'
        assert ent_attr.is_optional
        assert not ent_attr.is_set_of
        assert ent_attr.set_of_min is None
        assert ent_attr.set_of_max is None
        assert ent_attr.ifc_type_name == 'IfcCompoundPlaneAngleMeasure'
        assert isinstance(ent_attr.ifc_type_info, IfcSchemaBaseObject)

        assert '<{}>('.format(ent_attr.__class__.__name__) in repr(ent_attr)

        ent_attr = IfcSchemaEntityAttribute(
            'Coordinates', 'LIST [1:3] OF IfcLengthMeasure', ifc_root_entity)
        assert ent_attr.name == 'Coordinates'
        assert ent_attr.schema == ifc_root_entity.schema == schema_2x3
        assert ent_attr._raw_type == 'LIST [1:3] OF IfcLengthMeasure'
        assert not ent_attr.is_optional
        assert ent_attr.is_set_of
        assert ent_attr.set_of_min == '1'
        assert ent_attr.set_of_max == '3'
        assert ent_attr.ifc_type_name == 'IfcLengthMeasure'
        assert isinstance(ent_attr.ifc_type_info, IfcSchemaBaseObject)

    def test_ifc_schema_entity_attribute_errors(self, ifc_root_entity):

        # attr_raw_type must be a string
        with pytest.raises(AttributeError):
            IfcSchemaEntityAttribute(None, None, ifc_root_entity)

        # empty attr_raw_type string leads to nothing
        bad_ent_attr = IfcSchemaEntityAttribute('', '', ifc_root_entity)
        assert not bad_ent_attr.is_optional
        assert bad_ent_attr.ifc_type_name == ''
        assert bad_ent_attr.ifc_type_info is None

        # parent entity isntance must not be None
        with pytest.raises(AttributeError):
            IfcSchemaEntityAttribute('', '', None)


class TestIfcSchemaEntityInverse:

    def test_ifc_schema_entity_inverse(self, ifc_root_entity, schema_2x3):

        inv_raw_type = (
            'SET [0:?] OF IfcRelContainedInSpatialStructure'
            ' FOR RelatingStructure')
        ent_inv = IfcSchemaEntityInverse(
            'ContainsElements', inv_raw_type, ifc_root_entity)
        assert ent_inv.name == 'ContainsElements'
        assert ent_inv.schema == ifc_root_entity.schema == schema_2x3
        assert ent_inv._raw_type == inv_raw_type
        assert not ent_inv.is_optional
        assert ent_inv.is_set_of
        assert ent_inv.set_of_min == '0'
        assert ent_inv.set_of_max == '?'
        assert ent_inv.for_attr == 'RelatingStructure'
        assert ent_inv.ifc_type_name == 'IfcRelContainedInSpatialStructure'
        assert isinstance(ent_inv.ifc_type_info, IfcSchemaBaseObject)
        assert ent_inv.is_relation

        inv_raw_type = (
            'SET [0:1] OF IfcTimeSeriesReferenceRelationship'
            ' FOR ReferencedTimeSeries')
        ent_inv = IfcSchemaEntityInverse(
            'DocumentedBy', inv_raw_type, ifc_root_entity)
        assert ent_inv.name == 'DocumentedBy'
        assert ent_inv.schema == ifc_root_entity.schema == schema_2x3
        assert ent_inv._raw_type == inv_raw_type
        assert not ent_inv.is_optional
        assert ent_inv.is_set_of
        assert ent_inv.set_of_min == '0'
        assert ent_inv.set_of_max == '1'
        assert ent_inv.for_attr == 'ReferencedTimeSeries'
        assert ent_inv.ifc_type_name == 'IfcTimeSeriesReferenceRelationship'
        assert isinstance(ent_inv.ifc_type_info, IfcSchemaBaseObject)
        assert not ent_inv.is_relation

        inv_raw_type = 'IfcRelProjectsElement FOR RelatedFeatureElement'
        ent_inv = IfcSchemaEntityInverse(
            'ProjectsElements', inv_raw_type, ifc_root_entity)
        assert ent_inv.name == 'ProjectsElements'
        assert ent_inv.schema == ifc_root_entity.schema == schema_2x3
        assert ent_inv._raw_type == inv_raw_type
        assert not ent_inv.is_optional
        assert not ent_inv.is_set_of
        assert ent_inv.set_of_min is None
        assert ent_inv.set_of_max is None
        assert ent_inv.for_attr == 'RelatedFeatureElement'
        assert ent_inv.ifc_type_name == 'IfcRelProjectsElement'
        assert isinstance(ent_inv.ifc_type_info, IfcSchemaBaseObject)
        assert ent_inv.is_relation

    def test_ifc_schema_entity_inverse_errors(self, ifc_root_entity):

        # inv_raw_type must be a string
        with pytest.raises(AttributeError):
            IfcSchemaEntityInverse(None, None, ifc_root_entity)

        # empty inv_raw_type string leads to nothing
        bad_ent_inv = IfcSchemaEntityInverse('', '', ifc_root_entity)
        with pytest.raises(KeyError):
            bad_ent_inv.is_relation
        assert not bad_ent_inv.is_optional
        assert bad_ent_inv.ifc_type_name == ''
        assert bad_ent_inv.ifc_type_info is None

        # parent entity isntance must not be None
        with pytest.raises(AttributeError):
            IfcSchemaEntityInverse('', '', None)


class TestIfcSchemaEntity:

    def test_ifc_schema_entity_root(self, ifc_root_entity, schema_2x3):

        assert ifc_root_entity.name == 'IfcRoot'
        assert ifc_root_entity.schema == schema_2x3
        assert ifc_root_entity.supertype_name is None
        assert ifc_root_entity.supertype is None

        expected_attr_names = (
            'Description', 'GlobalId', 'Name', 'OwnerHistory',)
        expected_attr_names_not_opt = ('GlobalId', 'OwnerHistory',)

        assert ifc_root_entity.attribute_names == expected_attr_names
        assert len(ifc_root_entity.attributes) == len(expected_attr_names)
        for attr in ifc_root_entity.attributes:
            assert isinstance(attr, IfcSchemaEntityAttribute)
            assert attr.name in expected_attr_names

        assert ifc_root_entity.not_optional_attribute_names == (
            expected_attr_names_not_opt)
        assert len(ifc_root_entity.not_optional_attributes) == len(
            expected_attr_names_not_opt)
        for attr in ifc_root_entity.not_optional_attributes:
            assert isinstance(attr, IfcSchemaEntityAttribute)
            assert attr.name in expected_attr_names_not_opt

        root_subtypes = ifc_root_entity.get_subtypes()
        assert len(root_subtypes) == 3
        root_subtype_names = ifc_root_entity.get_subtype_names()
        assert len(root_subtype_names) == len(root_subtypes)
        for subtype in root_subtypes:
            assert isinstance(subtype, IfcSchemaEntity)
            assert subtype.name in root_subtype_names

        all_root_subtypes = ifc_root_entity.get_subtypes(deep_inheritance=True)
        assert len(all_root_subtypes) == 300
        all_root_subtype_names = ifc_root_entity.get_subtype_names(
            deep_inheritance=True)
        assert len(all_root_subtype_names) == len(all_root_subtypes)
        for subtype in all_root_subtypes:
            assert isinstance(subtype, IfcSchemaEntity)
            assert subtype.name in all_root_subtype_names

    def test_ifc_schema_entity(self, schema_2x3):

        raw_ent = (
            'SUBTYPE OF (IfcSpatialStructureElement);'
            '\n\tRefLatitude : OPTIONAL IfcCompoundPlaneAngleMeasure;'
            '\n\tRefLongitude : OPTIONAL IfcCompoundPlaneAngleMeasure;'
            '\n\tRefElevation : OPTIONAL IfcLengthMeasure;'
            '\n\tLandTitleNumber : OPTIONAL IfcLabel;'
            '\n\tSiteAddress : OPTIONAL IfcPostalAddress;')

        ent = IfcSchemaEntity('IfcSite', raw_ent, schema_2x3)
        assert ent.name == 'IfcSite'
        assert ent.schema == schema_2x3
        assert ent._raw_data == raw_ent
        assert ent.supertype_name == 'IfcSpatialStructureElement'
        assert isinstance(ent.supertype, IfcSchemaBaseObject)

        expected_attr_names = (
            'LandTitleNumber', 'RefElevation', 'RefLatitude', 'RefLongitude',
            'SiteAddress',)
        assert ent.attribute_names == expected_attr_names
        assert len(ent.attributes) == len(expected_attr_names)
        for attr in ent.attributes:
            assert isinstance(attr, IfcSchemaEntityAttribute)
            assert attr.name in expected_attr_names

        assert len(ent.not_optional_attribute_names) == 0
        assert len(ent.not_optional_attributes) == 0

        assert len(ent.inverse_names) == 0
        assert len(ent.inverse) == 0

        ent_attr = ent.get_attribute('RefLatitude')
        assert isinstance(ent_attr, IfcSchemaEntityAttribute)
        assert ent_attr.name == 'RefLatitude'
        assert ent_attr.schema == ent.schema

        all_attrs = ent.get_all_attributes()
        assert len(all_attrs) > len(ent.attributes)
        all_attrs_not_opt = ent.get_all_attributes(include_optional=False)
        assert len(all_attrs_not_opt) < len(all_attrs)

        all_attr_names = ent.get_all_attribute_names()
        assert len(all_attr_names) == len(all_attrs)
        assert all_attr_names == (
            'Description', 'GlobalId', 'Name', 'OwnerHistory', 'ObjectType',
            'ObjectPlacement', 'Representation', 'CompositionType', 'LongName',
            'LandTitleNumber', 'RefElevation', 'RefLatitude', 'RefLongitude',
            'SiteAddress',)
        all_attr_clsnames = ent.get_all_attribute_names(
            include_classname=True)
        assert all_attr_clsnames == (
            'IfcRoot.Description', 'IfcRoot.GlobalId', 'IfcRoot.Name',
            'IfcRoot.OwnerHistory', 'IfcObject.ObjectType',
            'IfcProduct.ObjectPlacement', 'IfcProduct.Representation',
            'IfcSpatialStructureElement.CompositionType',
            'IfcSpatialStructureElement.LongName', 'IfcSite.LandTitleNumber',
            'IfcSite.RefElevation', 'IfcSite.RefLatitude',
            'IfcSite.RefLongitude', 'IfcSite.SiteAddress',)
        all_attr_names_not_opt = ent.get_all_attribute_names(
            include_optional=False)
        assert len(all_attr_names_not_opt) == len(all_attrs_not_opt)
        assert all_attr_names_not_opt == (
            'GlobalId', 'OwnerHistory', 'CompositionType',)
        all_attr_clsnames_not_opt = ent.get_all_attribute_names(
            include_optional=False, include_classname=True)
        assert len(all_attr_clsnames_not_opt) == len(all_attrs_not_opt)
        assert all_attr_clsnames_not_opt == (
            'IfcRoot.GlobalId', 'IfcRoot.OwnerHistory',
            'IfcSpatialStructureElement.CompositionType',)

        all_inv_names = ent.get_all_inverse_names()
        assert all_inv_names == (
            'Decomposes', 'HasAssignments', 'HasAssociations',
            'IsDecomposedBy', 'IsDefinedBy', 'ReferencedBy',
            'ContainsElements', 'ReferencesElements', 'ServicedBySystems',)

        all_inv = ent.get_all_inverse()
        assert len(all_inv) == len(all_inv_names)
        for inv in all_inv:
            assert isinstance(inv, IfcSchemaEntityInverse)
            assert inv.name in all_inv_names

        all_inv_clsnames = ent.get_all_inverse_names(include_classname=True)
        assert all_inv_clsnames == (
            'IfcObjectDefinition.Decomposes',
            'IfcObjectDefinition.HasAssignments',
            'IfcObjectDefinition.HasAssociations',
            'IfcObjectDefinition.IsDecomposedBy', 'IfcObject.IsDefinedBy',
            'IfcProduct.ReferencedBy',
            'IfcSpatialStructureElement.ContainsElements',
            'IfcSpatialStructureElement.ReferencesElements',
            'IfcSpatialStructureElement.ServicedBySystems',)
        assert len(all_inv_clsnames) == len(all_inv) == len(all_inv_names)
        assert len(all_inv_clsnames) > len(ent.inverse)

        assert ent.inherits('IfcRoot')  # such as all IFC classes :)
        assert ent.inherits('IfcSpatialStructureElement')
        assert ent.inherits(
            'IfcSpatialStructureElement', deep_inheritance=False)

        assert ent.inherits('IfcProduct')
        assert not ent.inherits('IfcProduct', deep_inheritance=False)

        assert not ent.inherits('IfcProject')
        assert not ent.inherits('IfcProject', deep_inheritance=False)

        assert len(ent.get_subtype_names()) == 0
        assert len(ent.get_subtype_names(deep_inheritance=True)) == 0
        assert len(ent.get_subtypes()) == 0
        assert len(ent.get_subtypes(deep_inheritance=True)) == 0

    def test_ifc_schema_entity_with_inverse(self, schema_2x3):

        ent_name = 'IfcObject'
        raw_data = (
            'ABSTRACT SUPERTYPE OF (ONEOF'
            '\n\t(IfcActor'
            '\n\t,IfcControl'
            '\n\t,IfcGroup'
            '\n\t,IfcProcess'
            '\n\t,IfcProduct'
            '\n\t,IfcProject'
            '\n\t,IfcResource))'
            '\n SUBTYPE OF (IfcObjectDefinition);'
            '\n\tObjectType : OPTIONAL IfcLabel;'
            '\n INVERSE'
            '\n\tIsDefinedBy : SET [0:?] OF IfcRelDefines FOR RelatedObjects;'
            '\n WHERE'
            '\n\tWR1 : SIZEOF(QUERY(temp <* IsDefinedBy | '
            '\'IFC2X3.IFCRELDEFINESBYTYPE\' IN TYPEOF(temp))) <= 1;'
        )

        ent = IfcSchemaEntity(ent_name, raw_data, schema_2x3)
        assert ent.name == ent_name
        assert ent.schema == schema_2x3
        assert ent._raw_data == raw_data
        assert ent.supertype_name == 'IfcObjectDefinition'
        assert isinstance(ent.supertype, IfcSchemaBaseObject)

        assert ent.inverse_names == ('IsDefinedBy',)
        assert len(ent.inverse) == len(ent.inverse_names)
        assert ent.inverse[0].name == 'IsDefinedBy'

        ent_inv = ent.get_inverse('IsDefinedBy')
        assert isinstance(ent_inv, IfcSchemaEntityInverse)
        assert ent_inv.name == 'IsDefinedBy'
        assert ent_inv.schema == ent.schema == schema_2x3

        expected_all_inv_names = (
            'Decomposes', 'HasAssignments', 'HasAssociations',
            'IsDecomposedBy', 'IsDefinedBy',)
        assert ent.get_all_inverse_names() == expected_all_inv_names

        all_inv = ent.get_all_inverse()
        assert len(all_inv) == len(expected_all_inv_names)
        for inv in all_inv:
            assert isinstance(inv, IfcSchemaEntityInverse)
            assert inv.name in expected_all_inv_names

    def test_ifc_schema_entity_errors(self, schema_2x3):

        raw_ent = (
            'SUBTYPE OF (IfcSpatialStructureElement);'
            '\n\tRefLatitude : OPTIONAL IfcCompoundPlaneAngleMeasure;'
            '\n\tRefLongitude : OPTIONAL IfcCompoundPlaneAngleMeasure;'
            '\n\tRefElevation : OPTIONAL IfcLengthMeasure;'
            '\n\tLandTitleNumber : OPTIONAL IfcLabel;'
            '\n\tSiteAddress : OPTIONAL IfcPostalAddress;')

        ent = IfcSchemaEntity('IfcSite', raw_ent, schema_2x3)
        # unknown attribute
        with pytest.raises(KeyError):
            ent.get_attribute('bad')
        # unknown inverse
        with pytest.raises(KeyError):
            ent.get_inverse('bad')
