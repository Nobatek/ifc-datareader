"""IFC schema reader."""

from pathlib import Path
import re

from .ifc_schema_objects import (
    IfcSchemaDefinedType, IfcSchemaSelectType, IfcSchemaEnum, IfcSchemaEntity)


IFC_SCHEMAS = {
    'IFC2X3': 'specs/IFC2X3_TC1.exp',
    'IFC4': 'specs/IFC4_ADD2.exp',
}


class IfcSchema:
    """IFC schema reader object.

    :param str schema_name: The schema name to load.
    :param str|Path schema_filepath: (optional, default None)
        If not defined, schema file is deduced from schema_name.
        Else overrides default schema file corresponding to schema_name.
    :raises ValueError:
        When `schema_name` not in available choices (see IFC_SCHEMAS).
    """

    def __init__(self, schema_name, *, schema_filepath=None):
        if schema_filepath is None:
            if schema_name not in IFC_SCHEMAS:
                raise ValueError('Invalid schema name: {}'.format(schema_name))
            schema_dirpath = Path(__file__).parent
            schema_filepath = schema_dirpath / IFC_SCHEMAS.get(schema_name)
        else:
            schema_filepath = Path(schema_filepath)

        with open(str(schema_filepath)) as schema_file:
            self._raw_data = schema_file.read()

        self._defined_types_by_name = self._read_defined_types()
        self._select_types_by_name = self._read_select_types()
        self._enumerations_by_name = self._read_enumerations()
        self._entities_by_name = self._read_entities()

    def __repr__(self):
        return (
            '<{self.__class__.__name__}>('
            'version={self.version}'
            ', defined_types={nb_defined_types}'
            ', select_types={nb_select_types}'
            ', enumerations={nb_enumerations}'
            ', entities={nb_entities}'
            ')'.format(
                self=self, nb_defined_types=len(self._defined_types_by_name),
                nb_select_types=len(self._select_types_by_name),
                nb_enumerations=len(self._enumerations_by_name),
                nb_entities=len(self._entities_by_name)))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.version == other.version
        return False

    @property
    def version(self):
        """Parse schema raw data to get its version."""
        return re.search('SCHEMA (.*);', self._raw_data).groups()[0]

    @property
    def defined_type_names(self):
        """Get a tuple of the defined type's name, ascendingly sorted."""
        return tuple(sorted(self._defined_types_by_name))

    @property
    def defined_types(self):
        """Get a tuple of the defined types, ascendingly sorted by name."""
        return tuple(
            self._defined_types_by_name[name]
            for name in self.defined_type_names)

    @property
    def select_type_names(self):
        """Return a tuple of the select type's name, ascendingly sorted."""
        return tuple(sorted(self._select_types_by_name))

    @property
    def select_types(self):
        """Get a tuple of the select types, ascendingly sorted by name."""
        return tuple(self._select_types_by_name[name]
                     for name in self.select_type_names)

    @property
    def enumeration_names(self):
        """Get a tuple of the enumerations's name, ascendingly sorted."""
        return tuple(sorted(self._enumerations_by_name))

    @property
    def enumerations(self):
        """Get a tuple of the enumerations, ascendingly sorted by name."""
        return tuple(self._enumerations_by_name[name]
                     for name in self.enumeration_names)

    @property
    def entity_names(self):
        """Get a tuple of the entities's name, ascendingly sorted."""
        return tuple(sorted(self._entities_by_name))

    @property
    def entities(self):
        """Get a tuple of the entities, ascendingly sorted by name."""
        return tuple(self._entities_by_name[name]
                     for name in self.entity_names)

    def _read_defined_types(self):
        # parse schema raw data to return `IfcSchemaDefinedType` instances
        def_types = {}
        for cur_iter in re.finditer('TYPE (.*) = (.*);', self._raw_data):
            name, value = cur_iter.groups()
            def_types[name] = IfcSchemaDefinedType(name, value, self)
        return def_types

    def _read_select_types(self):
        # parse schema raw data to return `IfcSchemaSelectType` instances
        sel_types = {}
        for cur_iter in re.finditer(
                'TYPE (.*) = SELECT\\n\\t\\((.*(?:\\n\\t,.*)*)\\);',
                self._raw_data):
            name, values = cur_iter.groups()
            sel_types[name] = IfcSchemaSelectType(name, values, self)
        return sel_types

    def _read_enumerations(self):
        # parse schema raw data to return `IfcSchemaEnum` instances
        enums = {}
        for cur_iter in re.finditer(
                'TYPE (.*) = ENUMERATION OF\\n\\t\\((.*(?:\\n\\t,.*)*)\\);',
                self._raw_data):
            name, values = cur_iter.groups()
            enums[name] = IfcSchemaEnum(name, values, self)
        return enums

    def _read_entities(self):
        # parse schema raw data to return `IfcSchemaEntity` instances
        ents = {}
        # Regexes must be greedy to prevent matching outer ENTITY and
        #  END_ENTITY strings. Regexes have re.DOTALL to match newlines.
        for cur_iter in re.finditer(
                'ENTITY (.*?)END_ENTITY;', self._raw_data, re.DOTALL):
            raw_entity_str = cur_iter.groups()[0]
            name = re.search('(.*?)[;|\\s]', raw_entity_str).groups()[0]
            ents[name] = IfcSchemaEntity(name, raw_entity_str, self)
        return ents

    def get_defined_type(self, defined_type_name):
        """Search an defined type instance by its name.

        :param str defined_type_name: The defined type's name to find.
        :return IfcSchemaDefinedType: The defined type instance found.
        :raises KeyError: When defined_type_name does not exist.
        """
        return self._defined_types_by_name[defined_type_name]

    def get_select_type(self, select_type_name):
        """Search a select type instance by its name.

        :param str select_type_name: The select type's name to find.
        :return IfcSchemaSelectType: The select type instance found.
        :raises KeyError: When select_type_name does not exist.
        """
        return self._select_types_by_name[select_type_name]

    def get_enumeration(self, enum_name):
        """Search an enumeration instance by its name.

        :param str enum_name: The enumeration's name to find.
        :return IfcSchemaEnum: The enumeration instance found.
        :raises KeyError: When enum_name does not exist.
        """
        return self._enumerations_by_name[enum_name]

    def get_entity(self, entity_name):
        """Search an entity instance by its name.

        :param str entity_name: The entity's name to find.
        :return IfcSchemaEntity: The entity instance found.
        :raises KeyError: When entity_name does not exist.
        """
        return self._entities_by_name[entity_name]

    def get_element(self, element_name):
        """Search for the element in schema.

        :param str element_name: The element name to search for.
        :return IfcSchemaBaseElement: The found element or None.
        """
        # search in defined types, select types, enumerations and entities
        for get_func_name in ('get_defined_type', 'get_select_type',
                              'get_enumeration', 'get_entity',):
            try:
                return getattr(self, get_func_name)(element_name)
            except KeyError:
                pass
        # not found, so maybe it is nothing...
        return None

    def entity_inherits(
            self, entity_name, parent_entity_name, *, deep_inheritance=True):
        """Return True if `parent_entity_name` is a supertype of `entity_name`.

        :param str entity_name: An entity's name.
        :param str parent_entity_name: The possibly inherited entity's name.
        :param bool deep_inheritance: If True propagate inheritance to parents.
        :return bool: True if inheritance could be verified, else False.
        :raises KeyError: When entity_name does not exist.
        """
        return self._entities_by_name[entity_name].inherits(
            parent_entity_name, deep_inheritance=deep_inheritance)
