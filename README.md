# ifc-datareader

## About
An IFC file reader, using [IfcOpenShell](http://ifcopenshell.org/python.html).

This lib mainly aims to help on IFC entities manipulation, by abstracting
as much as possible all the specifications and tricks of the [IFC standard](
http://www.buildingsmart-tech.org/) (relations, property sets, ...).

## Examples

    from ifc_datareader import IfcDataReader

    # Open an IFC file and access metadata
    data_reader = IfcDataReader(ifc_file_path)
    assert data_reader.filename == ifc_file_path
    # IFC schema specifications loaded from version read in file
    assert data_reader.schema_version == 'IFC2X3'

    # Get IfcSite entities from the IFC file
    ifc_sites = data_reader.read_sites()
    assert len(ifc_sites) > 0
    first_ifc_site = ifc_sites[0]
    # IFC entity GlobalId
    assert first_ifc_site.global_id is not None
    # The parent of a site is expected to be a project
    assert first_ifc_site.parent == data_reader.ifc_project

    # Try the 'read_entity' feature
    ifc_site_entities = data_reader.read_entity('IfcSite')
    assert len(ifc_site_entities) == len(ifc_sites)
    assert ifc_site_entities == ifc_sites

## Installation

    pip install setup.py

**IfcOpenShell dependancy**

IfcOpenShell has to be installed manually:
- Download ifcopenshell-python archive from the [official site](
http://ifcopenshell.org/python.html) (acceptable version >= 0.5.0 preview 2).
- Place the extracted archive in the site-packages folder of the projet's
virtualenv: `$VENV_DIR/lib/python3.5/site-packages/`.

## Development

**Use a virtual environnement to debug or develop**

    # Create virtual environment
    $ virtualenv -p /usr/bin/python3 $ROOT_VENVS_DIR/ifc-datareader

    # Activate virtualenv
    $ source $ROOT_VENVS_DIR/ifc-datareader/bin/activate

**Tests**

    # Install test dependencies
    $ pip install -e .[test]

    # Run tests
    $ py.test

    # Skip slow tests
    $ py.test -m 'not slow'

    # Run tests with coverage
    $ py.test --cov=ifc_datareader --cov-report term-missing
