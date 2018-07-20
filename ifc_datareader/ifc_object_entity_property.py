"""IFC object entity property."""

import abc

from .ifc_base_entity import IfcBaseEntity


# TODO: treat IfcComplexProperty case?
# if yes, write an `IfcObjectEntityComplexProperty` class


class IfcObjectEntityPropertyBase(IfcBaseEntity, abc.ABC):
    """IFC extended entity property base class.

    :param ifcopenshell.entity_instance raw_property:
        The property's raw data instance.
    :param IfcSchema schema: The IFC schema specification description of data.
    :param tuple expected_types: (optional, default None)
        A tuple of IFC types that validates `raw_property`.
    :param IfcObjectEntityPropertySetBase pset: (optional, default None)
        The property set instance that contains the property.
    :raises ValueError:
        When `raw_property`, `schema` or `expected_types` is not valid.
        When `raw_property` does not inherit from one of `expected_types`.
    """

    @abc.abstractmethod
    def __init__(
            self, raw_property, schema, *, expected_types=None, pset=None):
        super().__init__(raw_property, schema, expected_types=expected_types)

        self.property_set = pset

        # attributes below are in 'lazy' load style (loaded on call)
        self._value = None
        self._value_type_name = None
        self._unit = None

    def __repr__(self):
        return (
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
            ')'.format(self=self))

    def __eq__(self, other):
        if self.global_id is not None and other.global_id is not None:
            return super().__eq__(other)
        return (self.name == other.name
                and self.property_set == other.property_set)

    @property
    def value(self):
        """Get the property's value."""
        return self._value

    @property
    def value_type_name(self):
        """Get the property value's type (IFC class name)."""
        return self._value_type_name

    @property
    def unit(self):
        """Get the property's unit."""
        return self._unit

    @property
    def property_set_name(self):
        """Get the attached property set's name."""
        if self.property_set is not None:
            return self.property_set.name
        return None

    @classmethod
    def create(cls, raw_data, schema, *, pset=None, prop_name=None):
        """Try to instanciate the appropriate property child class,
        according to what `raw_data` describes.

        :param ifcopenshell.entity_instance raw_data:
            The property's raw data instance.
        :param IfcSchema schema:
            The IFC schema specification description of data.
        :param IfcObjectEntityPropertySetBase pset: (optional, default None)
            The property set instance that contains the property.
        :param str prop_name: (optional, default None)
            The property's name (in fact it is an object type
            `IfcPropertySetDefinition`'s attribute name).
        :return IfcObjectEntityPropertyBase: The property instance created.
        :raises ValueError:
            When `raw_data`, `schema` or `expected_types` is not valid.
            When `raw_data` does not inherit from one of `expected_types`.
        """
        if raw_data.is_a('IfcSimpleProperty'):
            return IfcObjectEntitySimpleProperty(
                raw_data, schema, pset=pset)
        elif raw_data.is_a('IfcPropertySetDefinition'):
            return IfcObjectEntityTypeProperty(
                raw_data, prop_name, schema, pset=pset)
        else:
            # print some debug alerts about the ignored `raw_data` property
            IfcBaseEntity._print_debug_warning(raw_data, item='property')
        return None


class IfcObjectEntitySimpleProperty(IfcObjectEntityPropertyBase):
    """IFC extended entity simple property class (see `IfcSimpleProperty`).

    :param ifcopenshell.entity_instance raw_property:
        The property's raw data instance.
    :param IfcShema schema: The IFC schema specification description of data.
    :param IfcObjectEntityPropertySetBase pset:
        The property set instance that contains the property.
    :raises ValueError:
        When `raw_property`, `schema` or `expected_types` is not valid.
        When `raw_property` does not inherit from one of `expected_types`.
    """

    def __init__(self, raw_property, schema, *, pset=None):
        super().__init__(raw_property, schema,
                         expected_types=('IfcSimpleProperty',), pset=pset)

    @property
    def value(self):
        """Get the property's value."""
        if self._value is None:
            try:
                self._value = self.info['NominalValue'].wrappedValue
            except (KeyError, AttributeError):
                pass
        return super().value

    @property
    def value_type_name(self):
        """Get the property value's type (IFC class name)."""
        if self._value_type_name is None:
            try:
                self._value_type_name = self.info['NominalValue'].is_a()
            except (KeyError, AttributeError):
                pass
        return super().value_type_name

    @property
    def unit(self):
        """Get the property's unit."""
        if self._unit is None:
            self._unit = self.info.get('Unit')
        return super().unit


class IfcObjectEntityTypeProperty(IfcObjectEntityPropertyBase):
    """IFC extended entity object type property class, to manage IFC entities
    like `IfcDoorLiningProperties` or `IfcDoorPanelProperties`... which
    inherits from `IfcPropertySetDefinition` but not from `IfcPropertySet`.
    This class exists because we want our code to behave with those
    properties as with the 'real' `IfcProperty` instances.
    Finally it seems to work...

    :param ifcopenshell.entity_instance raw_type_pset:
        The object type property set's raw data instance (where the
        property's value is stored).
    :param str prop_name:
        The property's name (in fact it is an object type
        `IfcPropertySetDefinition`'s attribute name).
    :param IfcShema schema: The IFC schema specification description of data.
    :param IfcObjectEntityPropertySetBase pset: (optional, default None)
        The property set instance that contains the property.
    :raises ValueError:
        When `raw_type_pset`, `schema` or `expected_types` is not valid.
        When `raw_type_pset` does not inherit from one of `expected_types`.
    """

    def __init__(self, raw_type_pset, prop_name, schema, *, pset=None):
        super().__init__(
            raw_type_pset, schema,
            expected_types=('IfcPropertySetDefinition',), pset=pset)

        self._prop_name = prop_name

    @property
    def name(self):
        """Get the object type property's name."""
        return self._prop_name

    @property
    def value(self):
        """Get the property's value."""
        if self._value is None:
            try:
                self._value = self.info[self._prop_name]
            except (KeyError, AttributeError):
                pass
        return super().value

    @property
    def value_type_name(self):
        """Get the object type property value's type (IFC class name)."""
        # use schema metadata to get this information
        prop_schema = self.schema_metadata.get_attribute(self._prop_name)
        return prop_schema.ifc_type_name
