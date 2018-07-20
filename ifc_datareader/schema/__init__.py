"""IFC shema reading."""

from .ifc_schema_reader import IfcSchema, IFC_SCHEMAS  # noqa
from .ifc_schema_objects import (  # noqa
    IfcSchemaEntity, IfcSchemaEntityAttribute, IfcSchemaEntityInverse,
    IfcSchemaDefinedType, IfcSchemaSelectType, IfcSchemaEnum)
