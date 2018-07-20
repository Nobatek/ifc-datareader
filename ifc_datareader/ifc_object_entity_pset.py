"""IFC object entity property set"""

import abc

from .ifc_base_entity import IfcBaseEntity
from .ifc_object_entity_property import IfcObjectEntityPropertyBase


class IfcObjectEntityPropertySetBase(IfcBaseEntity, abc.ABC):
    """IFC extended entity property set base class.

    :param ifcopenshell.entity_instance raw_pset:
        An entity's raw data instance.
    :param IfcSchema schema: The IFC schema specification description of data.
    :param tuple expected_types: (optional, default ('IfcObject',))
        A tuple of IFC types that validates `raw_pset`.
    :raises ValueError:
        When `raw_pset`, `schema` or `expected_types` is not valid.
        When `raw_pset` does not inherit from one of `expected_types`.
    """

    @abc.abstractmethod
    def __init__(self, raw_pset, schema, *, expected_types=None):
        super().__init__(raw_pset, schema, expected_types=expected_types)

        # attributes below are in 'lazy' load style (loaded on call)
        self._properties = None

    def __repr__(self):
        props_count = len(self.properties or ())
        return (
            '<{self.__class__.__name__}>('
            'schema_version={self.schema_version}'
            ', type_name="{self.type_name}"'
            ', name="{self.name}"'
            ', codename="{self.codename}"'
            ', props_count={props_count}'
            ')'.format(self=self, props_count=props_count))

    @property
    def properties(self):
        """Get properties."""
        if self._properties is None:
            self._properties = self._load_properties()
        return self._properties

    @abc.abstractmethod
    def _load_properties(self):
        return self._properties

    def get_property_codenames(self):
        """Get a tuple of all available property's codename."""
        return tuple(prop.codename for prop in self.properties or ())

    @classmethod
    def create(cls, raw_data, schema):
        """Try to instanciate the appropriate property set child class,
        according to what `raw_data` describes.

        :param ifcopenshell.entity_instance raw_data:
            The property set's raw data instance.
        :param IfcSchema schema:
            The IFC schema specification description of data.
        :return IfcObjectEntityPropertySetBase: The property set instance.
        :raises ValueError:
            When `raw_data`, `schema` or `expected_types` is not valid.
            When `raw_data` does not inherit from one of `expected_types`.
        """
        if raw_data.is_a('IfcPropertySet'):
            return IfcObjectEntityPropertySet(raw_data, schema)
        elif raw_data.is_a('IfcPropertySetDefinition'):
            return IfcObjectEntityTypePropertySet(raw_data, schema)
        else:
            # print some debug alerts about the ignored `raw_data` property set
            IfcBaseEntity._print_debug_warning(raw_data, item='pset')
        return None


class IfcObjectEntityPropertySet(IfcObjectEntityPropertySetBase):
    """IFC extended entity property set class,
    suitable for `IfcPropertySet` property sets.

    :param ifcopenshell.entity_instance raw_pset:
        An entity's raw data instance.
    :param IfcSchema schema: The IFC schema specification description of data.
    :raises ValueError:
        When `raw_pset`, `schema` or `expected_types` is not valid.
        When `raw_pset` does not inherit from one of `expected_types`.
    """

    def __init__(self, raw_pset, schema):
        super().__init__(raw_pset, schema, expected_types=('IfcPropertySet',))

    def _load_properties(self):
        if self._properties is None:
            self._properties = ()
            for cur_prop in self._raw.HasProperties:
                prop = IfcObjectEntityPropertyBase.create(
                    cur_prop, self._schema, pset=self)
                if prop is not None:
                    self._properties += (prop,)
        return super()._load_properties()


class IfcObjectEntityTypePropertySet(IfcObjectEntityPropertySetBase):
    """IFC extended entity object type property set class, to manage
    `IfcTypeProduct` special property sets.

    :param ifcopenshell.entity_instance raw_pset:
        The property set definition's raw data instance.
    :param IfcSchema schema: The IFC schema specification description of data.
    :raises ValueError:
        When `raw_pset`, `schema` or `expected_types` is not valid.
        When `raw_pset` does not inherit from one of `expected_types`.
    """

    def __init__(self, raw_pset_def, schema):
        super().__init__(
            raw_pset_def, schema, expected_types=('IfcPropertySetDefinition',))

    def _load_properties(self):
        if self._properties is None:
            self._properties = ()
            # use schema metadata to get current entity's attributes
            for p_name in self.schema_metadata.attribute_names:
                prop = IfcObjectEntityPropertyBase.create(
                    self._raw, self._schema, pset=self, prop_name=p_name)
                if prop is not None:
                    self._properties += (prop,)
        return super()._load_properties()
