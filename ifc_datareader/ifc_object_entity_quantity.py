"""IFC object entity quantity."""

import abc

from .ifc_base_entity import IfcBaseEntity


# TODO: treat IfcPhysicalComplexQuantity case?
# if yes, write an `IfcObjectEntityComplexQuantity` class


class IfcObjectEntityQuantityBase(IfcBaseEntity, abc.ABC):
    """IFC extended entity quantity base class.

    :param ifcopenshell.entity_instance raw_data:
        The quantity's raw data instance.
    :param IfcSchema schema: The IFC schema specification description of data.
    :param tuple expected_types: (optional, default ('IfcPhysicalQuantity',))
        A tuple of IFC types that validates `raw_data`.
    :raises ValueError:
        When `raw_data`, `schema` or `expected_types` is not valid.
        When `raw_data` does not inherit from one of `expected_types`.
    """

    @abc.abstractmethod
    def __init__(self, raw_data, schema, *,
                 expected_types=('IfcPhysicalQuantity',)):
        super().__init__(raw_data, schema, expected_types=expected_types)

        # attributes below are in 'lazy' load style (loaded on call)
        self._value = None
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
            ')'.format(self=self))

    @property
    def value(self):
        """Get the quantity's value."""
        return self._value

    @property
    def unit(self):
        """Get the quantity's unit."""
        return self._unit

    @classmethod
    def create(cls, raw_data, schema):
        """Try to instanciate the appropriate quantity child class,
        according to what `raw_data` describes.

        :param ifcopenshell.entity_instance raw_data:
            The quantity's raw data instance.
        :param IfcSchema schema:
            The IFC schema specification description of data.
        :return IfcObjectEntityQuantityBase: The quantity instance created.
        :raises ValueError:
            When `raw_data`, `schema` or `expected_types` is not valid.
            When `raw_data` does not inherit from one of `expected_types`.
        """
        if raw_data.is_a('IfcPhysicalSimpleQuantity'):
            return IfcObjectEntitySimpleQuantity(raw_data, schema)
        else:
            # print some debug alerts about the ignored `raw_data` quantity
            IfcBaseEntity._print_debug_warning(raw_data, item='quantity')
        return None


class IfcObjectEntitySimpleQuantity(IfcObjectEntityQuantityBase):
    """IFC extended entity simple quantity class
    (see `IfcPhysicalSimpleQuantity`).

    :param ifcopenshell.entity_instance raw_data:
        The quantity's raw data instance.
    :param IfcSchema schema: The IFC schema specification description of data.
    :raises ValueError:
        When `raw_data`, `schema` or `expected_types` is not valid.
        When `raw_data` does not inherit from one of `expected_types`.
    """

    def __init__(self, raw_data, schema):
        super().__init__(
            raw_data, schema, expected_types=('IfcPhysicalSimpleQuantity',))

    @property
    def value(self):
        """Get the quantity's value."""
        if self._value is None:
            try:
                value_name = '{}Value'.format(
                    self.type_name[len('IfcQuantity'):])
                self._value = self.info[value_name]
            except (KeyError, AttributeError):
                pass
        return super().value

    @property
    def unit(self):
        """Get the quantity's unit."""
        if self._unit is None:
            self._unit = self.info.get('Unit')
        return super().unit
