"""IFC schema base element."""

import re
import copy
import abc


class IfcSchemaBaseObject(abc.ABC):
    """IFC schema generic element.

    :param str name: The element's name.
    :param IfcSchema schema: An `IfcSchema` instance.
    """

    @abc.abstractmethod
    def __init__(self, name, schema):
        self.name = name
        self.schema = schema

    def __repr__(self):
        return (
            '<{self.__class__.__name__}>('
            'name="{self.name}"'
            ', schema={self.schema}'
            ')'.format(self=self))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name and self.schema == other.schema
        return False


class IfcSchemaDefinedType(IfcSchemaBaseObject):
    """IFC schema defined type definition.

    :param str name: The defined type's name.
    :param str raw_value:
        The defined type's raw value (as read from schema file).
    :param IfcSchema schema: An `IfcSchema` instance.
    """

    _SIMPLE_TYPES = [
        'INTEGER', 'REAL', 'STRING', 'NUMBER', 'LOGICAL', 'BOOLEAN']

    def __init__(self, name, raw_value, schema):
        super().__init__(name, schema)
        self._raw_value = raw_value

    def __repr__(self):
        return (
            '<{self.__class__.__name__}>('
            'name="{self.name}"'
            ', type_name="{self.type_name}"'
            ', is_ref={self.is_ref}'
            ', ref_type={self.ref_type}'
            ')'.format(self=self))

    @property
    def type_name(self):
        """Get the type's name. It can be a simple type or another referenced
        defined type (the type's name is then prefixed with a '#')."""
        raw_values = re.split(' |\\) |\\(', self._raw_value)
        # add the reference prefix (#) if it is not a simple type
        if len(set(raw_values) & set(self._SIMPLE_TYPES)) <= 0:
            return '#{}'.format(self._raw_value)
        return self._raw_value

    @property
    def is_ref(self):
        """True if defined type is a reference to another defined type."""
        return self.type_name.startswith('#')

    @property
    def ref_type(self):
        """Get the referenced defined type (from schema)."""
        if self.is_ref:
            return self.schema.get_defined_type(self._raw_value)
        return None


class IfcSchemaSelectType(IfcSchemaBaseObject):
    """IFC schema select type definition.

    :param str name: The select type's name.
    :param str raw_types:
        The select type's raw types (as read from schema file).
    :param IfcSchema schema: An `IfcSchema` instance.
    """

    def __init__(self, name, raw_types, schema):
        super().__init__(name, schema)
        self._raw_types = raw_types

    def __repr__(self):
        return (
            '<{self.__class__.__name__}>('
            'name="{self.name}"'
            ', entity_names={self.entity_names}'
            ')'.format(self=self))

    @property
    def entity_names(self):
        """Get a tuple of the entity's name selected, ascendingly sorted."""
        return tuple(sorted(self._raw_types.replace('\n\t', '').split(',')))

    @property
    def entities(self):
        """Get a tuple of entities selected, ascendingly sorted by name."""
        return tuple(
            self.schema.get_entity(name) for name in self.entity_names)


class IfcSchemaEnum(IfcSchemaBaseObject):
    """IFC schema enumeration definition.

    :param str name: The enumeration's name.
    :param str raw_values:
        The enumeration's raw values (as read from schema file).
    :param IfcSchema schema: An `IfcSchema` instance.
    """

    def __init__(self, name, raw_values, schema):
        super().__init__(name, schema)
        self._raw_values = raw_values

    def __repr__(self):
        return (
            '<{self.__class__.__name__}>('
            'name="{self.name}"'
            ', values={self.values}'
            ')'.format(self=self))

    @property
    def values(self):
        """Get a tuple of the enumeration's values, ascendingly sorted."""
        return tuple(sorted(self._raw_values.replace('\n\t', '').split(',')))


class IfcSchemaEntityAttribute(IfcSchemaBaseObject):
    """IFC schema entity property (attribute or inverse) definition.

    :param str attr_name: The attribute's (or inverse's) name.
    :param str attr_raw_type:
        The attribute's raw type definition (as read from schema file).
    :param IfcSchemaEntity entity:
        The entity instance that contains this attribute instance.
    """

    def __init__(self, attr_name, attr_raw_type, entity):
        super().__init__(attr_name, entity.schema)
        self._raw_type = attr_raw_type
        self.entity = entity
        self.is_set_of = False
        self.set_of_min = None
        self.set_of_max = None
        self.ifc_type_name = self._raw_type
        if self.is_optional:
            self.ifc_type_name = self._raw_type.replace('OPTIONAL ', '')

        self._extract_raw_type()

    def __repr__(self):
        def _get_and_format_field_value(field_name):
            value = getattr(self, field_name, None)
            if isinstance(value, str):
                value = '"{}"'.format(value)
            return value

        _field_names = [
            a for a in dir(self)
            if a[:1] != '_' and not callable(getattr(self, a))]

        return '<{self.__class__.__name__}>({attrs})'.format(
            self=self, attrs=', '.join(['{}={}'.format(
                field_name, _get_and_format_field_value(field_name)
            ) for field_name in _field_names]))

    @property
    def is_optional(self):
        """Is it an optional attribute?"""
        return self._raw_type.startswith('OPTIONAL')

    @property
    def ifc_type_info(self):
        """Get the attribute type info."""
        return self.schema.get_element(self.ifc_type_name)

    def _extract_raw_type(self):
        extracted_meta = re.search(
            ('(?:(?:SET|LIST)\\s(?:\\[([0-9]+):([\\?0-9]+)\\])?(?:\\sOF\\s)?)?'
             '(Ifc[a-zA-Z]+)(?:\\sFOR (.*))?$'),
            self._raw_type)
        if extracted_meta is not None:
            self.set_of_min = extracted_meta.groups()[0]
            self.set_of_max = extracted_meta.groups()[1]
            if self.set_of_min is not None or self.set_of_max is not None:
                self.is_set_of = True
            self.ifc_type_name = extracted_meta.groups()[2]
        return extracted_meta


class IfcSchemaEntityInverse(IfcSchemaEntityAttribute):
    """IFC schema entity inverse relation definition.

    :param str inverse_name: The inverse's name.
    :param str inv_raw_type:
        The inverse's raw type definition (as read from schema file).
    :param IfcSchemaEntity entity:
        The entity instance that contains this attribute instance.
    """

    def __init__(self, inverse_name, inv_raw_type, entity):
        self.for_attr = None
        super().__init__(inverse_name, inv_raw_type, entity)

    @property
    def is_relation(self):
        """Is this inverse an `IfcRelationship` instance?"""
        # ...an entity inverse value is NOT ALWAYS a relation !
        return self.schema.entity_inherits(
            self.ifc_type_name, 'IfcRelationship')

    def _extract_raw_type(self):
        extracted_meta = super()._extract_raw_type()
        if extracted_meta is not None:
            self.for_attr = extracted_meta.groups()[3]


class IfcSchemaEntity(IfcSchemaBaseObject):
    """IFC schema entity definition.

    :param str name: The entity's name.
    :param str raw_data: The entity's raw data (as read from schema file).
    :param IfcSchema schema: An `IfcSchema` instance.
    """

    _NO_ATTR = [
        'WHERE', 'INVERSE', 'WR2', 'WR3', 'WR4', 'WR5', 'UNIQUE', 'DERIVE']

    def __init__(self, name, raw_data, schema):
        super().__init__(name, schema)
        self._raw_data = raw_data
        self.supertype_name = None
        self._attributes_by_name = {}
        self._inverse_by_name = {}

        self._extract_raw_data()

    def __repr__(self):
        return (
            '<{self.__class__.__name__}>('
            'name="{self.name}"'
            ', supertype_name="{self.supertype_name}"'
            ', attribute_names={self.attribute_names}'
            ', not_optional_attribute_names='
            '{self.not_optional_attribute_names}'
            ', inverse_names={self.inverse_names}'
            ')'.format(self=self))

    @property
    def supertype(self):
        """Get the entity's supertype."""
        if self.supertype_name is not None:
            return self.schema.get_entity(self.supertype_name)
        return None

    @property
    def attribute_names(self):
        """Get a tuple of the attributes's names, ascendingly sorted."""
        return tuple(sorted(self._attributes_by_name))

    @property
    def attributes(self):
        """Get a tuple of the attributes, ascendingly sorted by name."""
        return tuple(
            self._attributes_by_name[name] for name in self.attribute_names)

    @property
    def not_optional_attribute_names(self):
        """Get a tuple of the attributes's names, ignoring optional ones,
        ascendingly sorted."""
        return tuple(
            attr.name for attr in self.attributes if not attr.is_optional)

    @property
    def not_optional_attributes(self):
        """Get a tuple of the attributes, ignoring optional ones,
        ascendingly sorted by name."""
        return tuple(self._attributes_by_name[name]
                     for name in self.not_optional_attribute_names)

    @property
    def inverse_names(self):
        """Get a tuple of the inverse's names, ascendingly sorted."""
        return tuple(sorted(self._inverse_by_name))

    @property
    def inverse(self):
        """Get a tuple of the inverse, ascendingly sorted by name."""
        return tuple(
            self._inverse_by_name[name] for name in self.inverse_names)

    def _extract_raw_data(self):
        # extract supertype_name from _raw_data
        subtypeofmatch = re.search('.*SUBTYPE OF \\((.*?)\\);', self._raw_data)
        if subtypeofmatch:
            self.supertype_name = subtypeofmatch.groups()[0]

        # Find the shortest string matched from the end of the entity
        #  type header to the first occurence of a _NO_ATTR string
        #  (when it occurs on a new line).
        inner_raw_data = re.search(
            ';(.*?)$', self._raw_data, re.DOTALL).groups()[0]

        # extract attributes from inner_raw_data
        attrs_str = min([
            inner_raw_data.partition('\n ' + noa)[0] for noa in self._NO_ATTR])
        for cur_iter_attr in re.finditer(
                '(.*?) : (.*?);', attrs_str, re.DOTALL):
            attr_name, attr_type = [
                s.replace('\n\t', '') for s in cur_iter_attr.groups()]
            self._attributes_by_name[attr_name] = IfcSchemaEntityAttribute(
                attr_name, attr_type, self)

        # extract inverse from inner_raw_data
        inverse_str = inner_raw_data.partition('\n INVERSE')[2]
        inverse_str = min([
            inverse_str.partition('\n ' + noa)[0] for noa in self._NO_ATTR])
        for cur_iter_inverse in re.finditer(
                '(.*?) : (.*?);', inverse_str, re.DOTALL):
            inv_name, inv_type = [
                s.replace('\n\t', '') for s in cur_iter_inverse.groups()]
            self._inverse_by_name[inv_name] = IfcSchemaEntityInverse(
                inv_name, inv_type, self)

    def get_attribute(self, attribute_name):
        """Search an `IfcSchemaEntityAttribute` instance by its name.

        :param str attribute_name: The atrribute's name to find.
        :return IfcSchemaEntityAttribute: The attribute found.
        :raise KeyError: When attribute_name does not exist.
        """
        return self._attributes_by_name[attribute_name]

    def get_all_attributes(self, *, include_optional=True):
        """Get a tuple of all attributes, including inherited.
        (different to `attributes` property which scope is only entity)

        :param bool include_optional: (optional, default True)
            If False ignore attributes marked as optional.
        :return tuple: All the entity's attributes (with inheritance).
        """
        inner_attr_name = 'attributes'
        if not include_optional:
            inner_attr_name = 'not_optional_{}'.format(inner_attr_name)
        all_attrs = copy.deepcopy(getattr(self, inner_attr_name, ()))
        # get inherited attribute_names, recursively
        if self.supertype is not None:
            all_attrs = self.supertype.get_all_attributes(
                include_optional=include_optional) + all_attrs
        return all_attrs

    def get_all_attribute_names(
            self, *, include_optional=True, include_classname=False):
        """Get a tuple of all attribute's name, including inherited.
        (different to `attribute_names` property which scope is only entity)

        :param bool include_optional: (optional, default True)
            If False ignore attributes marked as optional.
        :param bool include_classname: (optional, default False)
            If True prefix each attribute's name with its origin class name.
            For example: 'IfcRoot.GlobalId' instead of just 'GlobalId'
        :return tuple: All attribute's names.
        """
        def _build_name(classname, name):
            if include_classname:
                return '{}.{}'.format(classname, name)
            return name

        return tuple(
            _build_name(attr.entity.name, attr.name)
            for attr in self.get_all_attributes(
                include_optional=include_optional))

    def get_inverse(self, inverse_name):
        """Search an `IfcSchemaEntityInverse` instance by its name.

        :param str inverse_name: The inverse's name to find.
        :return IfcSchemaEntityInverse: The inverse instance found.
        :raise KeyError: When inverse_name does not exist.
        """
        return self._inverse_by_name[inverse_name]

    def get_all_inverse(self):
        """Get a tuple of all inverse, including inherited.
        (different to `inverse` property which scope is only entity)

        :return tuple:
            All inverse's entity attribute instances (with inheritance).
        """
        all_inv = copy.deepcopy(self.inverse)
        # get inherited inverse, recursively
        if self.supertype is not None:
            all_inv = self.supertype.get_all_inverse() + all_inv
        return all_inv

    def get_all_inverse_names(self, *, include_classname=False):
        """Get a tuple of all inverse's name, including inherited.
        (different to `inverse_names` property which scope is only entity)

        :param bool include_classname: (optional, default False)
            If True prefix each inverse's name with its origin class name.
            For example: 'IfcObject.IsDefinedBy' instead of just 'IsDefinedBy'
        :return tuple: All inverse's names.
        """
        def _build_name(classname, name):
            if include_classname:
                return '{}.{}'.format(classname, name)
            return name

        return tuple(
            _build_name(inv.entity.name, inv.name)
            for inv in self.get_all_inverse())

    def inherits(self, parent_entity_name, *, deep_inheritance=True):
        """Return True if `parent_entity_name` is a supertype.

        :param str parent_entity_name: The entity's name of inheritance.
        :param bool deep_inheritance: (optional, default True)
            If True propagate inheritance to parents.
        :return bool: True if inheritance is confirmed, else False.
        """
        if self.supertype_name == parent_entity_name:
            return True
        if deep_inheritance:
            # check inheritance from parent's supertype, recursively
            if self.supertype is not None:
                return self.supertype.inherits(
                    parent_entity_name, deep_inheritance=deep_inheritance)
        return False

    def get_subtypes(self, *, deep_inheritance=False):
        """Get a tuple of entity's subtypes.

        :param bool deep_inheritance: (optional, default False)
            If False ignore child subtypes.
        :return tuple: All entity's subtype instances.
        """
        return tuple(
            cur_ent for cur_ent in self.schema.entities
            if cur_ent.inherits(self.name, deep_inheritance=deep_inheritance))

    def get_subtype_names(self, *, deep_inheritance=False):
        """Get a tuple of all entity subtype's name.

        :param bool deep_inheritance: (optional, default False)
            If False ignore child subtypes.
        :return tuple: All entity's subtype names.
        """
        return tuple(
            cur_ent.name for cur_ent in self.get_subtypes(
                deep_inheritance=deep_inheritance))
