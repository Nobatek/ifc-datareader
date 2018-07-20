"""IFC base entity"""

import abc
import ifcopenshell

from .tools import clean_str


class IfcBaseEntity(abc.ABC):
    """IFC base entity generic definition (kind of `IfcRoot`...).

    :param ifcopenshell.entity_instance raw_obj_entity:
        An entity's raw data instance.
    :param IfcSchema schema: The IFC schema specification description of data.
    :param tuple expected_types: (optional, default ('IfcObject',))
        A tuple of IFC types that validates `raw_obj_entity`.
    :raises ValueError:
        When `raw_obj_entity`, `schema` or `expected_types` is not valid.
        When `raw_obj_entity` does not inherit from one of `expected_types`.
    """

    @abc.abstractmethod
    def __init__(
            self, raw_obj_entity, schema, *, expected_types=('IfcObject',)):
        self._raw = raw_obj_entity
        self._schema = schema

        if not isinstance(self._raw, ifcopenshell.entity_instance):
            raise ValueError('Invalid raw object entity: {}'.format(self._raw))
        if not isinstance(expected_types, tuple):
            raise ValueError('Invalid expected types (must be defined): {}'
                             .format(expected_types))

        for cur_expected_type in expected_types:
            if not self._raw.is_a(cur_expected_type):
                raise ValueError('Invalid entity type: `{}`. {} expected.'
                                 .format(self._raw.is_a(), expected_types))

        self.info = self._raw.get_info()

    def __repr__(self):
        return (
            '<{self.__class__.__name__}>('
            'schema_version={self.schema_version}'
            ', type="{self.type_name}"'
            ', name="{self.name}"'
            ', codename="{self.codename}"'
            ', description="{self.description}"'
            ')'.format(self=self))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.global_id == other.global_id
        return False

    @property
    def schema_version(self):
        """Get the IFC version used by this entity."""
        if self._schema is not None:
            return self._schema.version
        return None

    @property
    def type_name(self):
        """Get the entity's type (IFC class name)."""
        return self.info.get('type')

    @property
    def global_id(self):
        """Get the entity's `GlobalId` (`IfcRoot` attribute)."""
        return self.info.get('GlobalId')

    @property
    def name(self):
        """Get the entity's `Name` (`IfcRoot` attribute)."""
        return self.info.get('Name')

    @property
    def description(self):
        """Get the entity's `Description` (`IfcRoot` attribute)."""
        return self.info.get('Description')

    @property
    def codename(self):
        """Get a 'cleaned' name, as a python object attribute name."""
        # get property codename 'lowered' and without spaces
        return clean_str(self.name).lower().replace(' ', '')

    @property
    def schema_metadata(self):
        """Get the entity's IFC schema metadata (its specification)."""
        return self._schema.get_entity(self.type_name)

    @staticmethod
    def _print_debug_warning(raw_data, *, item=''):
        # Print some debug alerts about an `ifcopenshell.entity_instance`.
        # Used on ignored objects when accessing raw data.
        print('>>>>WARNING>>>>')
        print('>>Ignored {} `{}`, attributes: {}'.format(
            item, raw_data.is_a(),
            raw_data.wrapped_data.get_attribute_names()))
        print('>>Raw data:', raw_data)
        print('<<<<WARNING<<<<')
