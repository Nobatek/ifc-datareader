"""Fixtures for tests"""

from pathlib import Path
import pytest
import ifcopenshell

from ifc_datareader import IfcSchema
from ifc_datareader.schema import IfcSchemaEntity


@pytest.fixture
def schema_2x3():
    return IfcSchema('IFC2X3')


@pytest.fixture
def schema_4():
    return IfcSchema('IFC4')


@pytest.fixture
def schema_custom_filepath(tmpdir):
    schema_data = (
        'SCHEMA IFC42;\n'
        '\n'
        'TYPE IfcConspiration = REAL;\n'
        'END_TYPE;\n'
        '\n'
        'END_SCHEMA;'
    )

    schema_filepath = tmpdir / 'custom_schema.exp'
    with open(str(schema_filepath), 'w') as file:
        file.write(schema_data)

    return str(schema_filepath)


@pytest.fixture
def ifc_root_entity():
    raw_data = (
        'ABSTRACT SUPERTYPE OF (ONEOF'
        '\n\t(IfcObjectDefinition'
        '\n\t,IfcPropertyDefinition'
        '\n\t,IfcRelationship));'
        '\n\tGlobalId : IfcGloballyUniqueId;'
        '\n\tOwnerHistory : IfcOwnerHistory;'
        '\n\tName : OPTIONAL IfcLabel;'
        '\n\tDescription : OPTIONAL IfcText;'
    )
    return IfcSchemaEntity('IfcRoot', raw_data, IfcSchema('IFC2X3'))


def _build_filepath(filename):
    samples_dirpath = Path(__file__).parent / 'samples'
    return samples_dirpath / filename


@pytest.fixture(params=['sample_test.ifc'])
def ifc_filepath(request):
    """Return an IFC file path."""
    return _build_filepath(request.param)


@pytest.fixture
def sample_ifcos():
    return ifcopenshell.open(str(_build_filepath('sample_test.ifc')))
