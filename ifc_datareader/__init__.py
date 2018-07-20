"""
IFC data reading

The main goal of these classes is to help manipulating IFC entities,
by abstracting as much as possible all the specifications and tricks of the IFC
(relations, property sets, ...).

- IfcDataReader: main class
    Allows to read IFC data files (throught ifcopenshell)
    Returns `IfcObjectEntity` instances

- IfcBaseEntity:
    All classes below inherits from it
    Allows a quick access to main IFC entity attributes (type, name, ...)
    Offers IFC entity validation using the type

- IfcObjectEntity: main ifc data class
    Inherits from `IfcBaseEntity`
    Allows to access all the data of an IFC entity
    Some extra feature is available to quick access parent and kids entities
        (returned as `IfcObjectEntity` instances), whatever the IFC entity read
    Allows a quick access to property sets (and property values) using
        `IfcObjectEntityPropertySet` instances, whatever the IFC entity read
    Also allows access to object type (when described),
        returned as an `IfcObjectEntity` instance

- IfcObjectEntityPropertySet:
    Inherits from `IfcBaseEntity`
    Allows a quick access to a set of property values,
        returned as `IfcObjectEntityPropertyBase` instances
    Another feature gives all available properties (by name or codename)

- IfcObjectEntityPropertyBase:
    Inherits from `IfcBaseEntity`
    Describes generically what is supposed to be an IFC property
        (`IfcProperty`, `IfcPhysicalQuantity`, ...) by exposing property value
        and property unit
- IfcObjectEntityProperty:
    Inherits from `IfcObjectEntityPropertyBase`
    Specific class to parse `IfcProperty` type entities
- IfcObjectEntityPropertyQuantity:
    Inherits from `IfcObjectEntityPropertyBase`
    Specific class to parse `IfcPhysicalQuantity` type entities
"""

# TODO: add logging

from .ifc_data_reader import IfcDataReader  # noqa
from .ifc_object_entity import IfcObjectEntity  # noqa
from .schema import IfcSchema, IFC_SCHEMAS  # noqa
