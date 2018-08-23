"""IFC data reader."""

from pathlib import Path
import ifcopenshell

from .ifc_object_entity import IfcObjectEntity
from .schema import IfcSchema


class IfcDataReader():
    """IFC data reader to explore an IFC data file.
    Gives some features to ease IFC data access and navigation.

    :param str|Path filename: IFC full filename (absolute path) to read.
    """

    def __init__(self, filename):
        self.filename = Path(filename)
        if not self.filename.is_file():
            raise ValueError('Invalid filename: {}'.format(filename))

        self._ifcos_file = ifcopenshell.open(str(self.filename))
        self.ifc_schema = IfcSchema(self.schema_version)
        self.ifc_project = self._read_project()

    def __repr__(self):
        return (
            '<{self.__class__.__name__}>('
            'filename="{self.filename}"'
            ', schema_version="{self.schema_version}"'
            ', ifc_project_name="{self.ifc_project.name}"'
            ')'.format(self=self))

    @property
    def schema_version(self):
        """Get IFC file schema version."""
        ifc_file_schema = self._ifcos_file.wrapped_data.header.file_schema
        if len(ifc_file_schema.schema_identifiers) > 0:
            return ifc_file_schema.schema_identifiers[0]
        if len(ifcopenshell.schema_identifier) > 0:
            return ifcopenshell.schema_identifier[0]
        return None

    def _read_project(self):
        """Get the unique `IfcProjet` entity."""
        res = self._read_entities('IfcProject')
        if len(res) != 1:
            raise TypeError(
                'Invalid IFC file: must contain a unique `IfcProject` entity!')
        return res[0]

    def _read_entities(self, entity_name, *, parent_entity=None):
        """Get a tuple of all `entity_name` entities, having `parent_entity` as
        family ascendant (if defined).

        :param str entity_name: IFC entity class name.
        :param IfcObjectEntity parent_entity: (optional, default None)
            If defined it filters read entities having this value as parent.
        :raises ValueError:
            When entity_name is not valid.
            When parent_entity instance is not valid.
        """
        if (parent_entity is not None
                and not isinstance(parent_entity, IfcObjectEntity)):
            raise ValueError(
                'Invalid parent entity instance: {}'.format(parent_entity))
        try:
            # find entities using entity_name
            entities = tuple(
                IfcObjectEntity(cur_raw_entity, schema=self.ifc_schema)
                for cur_raw_entity in self._ifcos_file.by_type(entity_name))
            # filter found entities with parent entity matching
            if parent_entity is not None:
                entities = tuple(
                    cur_entity for cur_entity in entities
                    if cur_entity.parent.global_id == parent_entity.global_id)
            return entities
        except RuntimeError:
            raise ValueError('Invalid entity name: {}'.format(entity_name))
        return None

    def read_sites(self, *, undivided_only=True):
        """Get a tuple of all `IfcSite` entities in the file.

        :param bool undivided_only: (optional, default True)
            All entities must have an 'ELEMENT' as `CompositionType` value.
        :return tuple: All IfcObjectEntity instances found.
        """
        site_entities = ()
        for cur_ent in self._read_entities('IfcSite'):
            if not undivided_only or (undivided_only and cur_ent.is_element):
                site_entities += (cur_ent,)
            elif (cur_ent.parent is not None and cur_ent.parent.is_element
                  and cur_ent.parent.is_a('IfcSite')):
                site_entities += (cur_ent.parent,)
        return site_entities

    def read_buildings(self, *, undivided_only=True, parent_entity=None):
        """Get a tuple of all `IfcBuilding` entities in the file.

        :param bool undivided_only:
            All entities must have an 'ELEMENT' as `CompositionType` value.
        :param IfcObjectEntity parent_entity: (optional, default None)
            If defined it filters read entities having this value as parent.
        :return tuple: All IfcObjectEntity instances found.
        """
        return tuple(
            cur_ent
            for cur_ent in self._read_entities(
                'IfcBuilding', parent_entity=parent_entity)
            if not undivided_only or (undivided_only and cur_ent.is_element))

    def read_building_storeys(
            self, *, undivided_only=True, parent_entity=None):
        """Get a tuple of all `IfcBuildingStorey` entities in the file.

        :param bool undivided_only: (optional, default True)
            All entities must have an 'ELEMENT' as `CompositionType` value.
        :param IfcObjectEntity parent_entity: (optional, default None)
            If defined it filters read entities having this value as parent.
        :return tuple: All IfcObjectEntity instances found.
        """
        return tuple(
            cur_ent
            for cur_ent in self._read_entities(
                'IfcBuildingStorey', parent_entity=parent_entity)
            if not undivided_only or (undivided_only and cur_ent.is_element))

    def read_spaces(self, *, undivided_only=True, parent_entity=None):
        """Get a tuple of all `IfcSpace` entities in the file.

        :param bool undivided_only: (optional, default True)
            All entities must have an 'ELEMENT' as `CompositionType` value.
        :param IfcObjectEntity parent_entity: (optional, default None)
            If defined it filters read entities having this value as parent.
        :return tuple: All IfcObjectEntity instances found.
        """
        return tuple(
            cur_ent
            for cur_ent in self._read_entities(
                'IfcSpace', parent_entity=parent_entity)
            if not undivided_only or (undivided_only and cur_ent.is_element))

    def read_zones(self):
        """Get a tuple of all `IfcZone` entities in the file.

        :return tuple: All IfcObjectEntity instances found.
        """
        return self._read_entities('IfcZone')

    def read_walls(self):
        """Get a tuple of all `IfcWall` and `IfcWallStandardCase` entities in
        the file.
        :return tuple: All IfcObjectEntity instances found.
        """
        return self._read_entities('IfcWall') +\
            self._read_entities('IfcWallStandardCase')

    def read_windows(self):
        """Get a tuple of all `IfcWindows` entities in
        the file.
        :return tuple: All IfcObjectEntity instances found.
        """
        return self._read_entities('IfcWindow')

    def read_entity(self, entity_name, *, parent_entity=None):
        """Get a tuple of all `entity_name` entities in the file,
        having `parent_entity` as family ascendant (if defined).

        :param str entity_name: An IFC entity class name.
        :param IfcObjectEntity parent_entity: (optional, default None)
            If defined it filters read entities having this value as parent.
        :return tuple: All IfcObjectEntity instances found.
        """
        return self._read_entities(entity_name, parent_entity=parent_entity)

    def get_object(self, entity):
        """Simple conversion method: get an IfcObjectEntity from a raw entity

        :param raw entity entity: An IFC entity
        :return IfcObjectEntity: The converted entity
        """
        return IfcObjectEntity(entity, schema=self.ifc_schema)
