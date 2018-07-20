"""IFC object entity"""

import copy

from .ifc_base_entity import IfcBaseEntity
from .ifc_object_entity_pset import IfcObjectEntityPropertySetBase
from .ifc_object_entity_quantity import IfcObjectEntityQuantityBase


class IfcObjectEntity(IfcBaseEntity):
    """IFC extended object entity definition.

    :param ifcopenshell.entity_instance raw_obj_entity:
        An entity's raw data instance.
    :param IfcSchema schema: The IFC schema specification description of data.
    :param tuple expected_types: (optional, default ('IfcObject',))
        A tuple of IFC types that validates `raw_obj_entity`.
    :raises ValueError:
        When `raw_obj_entity`, `schema` or `expected_types` is not valid.
        When `raw_obj_entity` does not inherit from one of `expected_types`.
    """

    def __init__(self, raw_obj_entity, schema, *,
                 expected_types=('IfcObject',)):
        super().__init__(raw_obj_entity, schema, expected_types=expected_types)

        # attributes below are in 'lazy' load style (loaded on call)
        self._parent = None
        self._kids = None
        self._property_sets = None
        self._quantities = None
        self._object_type = None
        # TODO: treat materials case
        # Add a 'self._materials = None' and all related code to get
        #  information about entity's relations with materials.

    def __repr__(self):
        kids_count = len(self.kids or ())
        psets_count = len(self.property_sets or ())
        quantities_count = len(self.quantities or ())
        return (
            '<{self.__class__.__name__}>('
            'schema_version={self.schema_version}'
            ', type_name="{self.type_name}"'
            ', global_id="{self.global_id}"'
            ', name="{self.name}"'
            ', codename="{self.codename}"'
            ', description="{self.description}"'
            ', kids_count="{kids_count}"'
            ', psets_count="{psets_count}"'
            ', quantities_count="{quantities_count}"'
            ')'.format(
                self=self, kids_count=kids_count, psets_count=psets_count,
                quantities_count=quantities_count))

    @property
    def composition_type(self):
        """Try to get the composition type of this entity.
        (`IfcSpatialStructureElement` type entities have a `CompositionType`
        attribute, which values are described by `IfcElementCompositionEnum`
        and can be a choice between [COMPLEX, ELEMENT, PARTIAL])."""
        # get CompositionType value only for IfcSpatialStructureElement
        if self._raw.is_a('IfcSpatialStructureElement'):
            return self.info.get('CompositionType')
        return None

    @property
    def is_element(self):
        """Try to see if this entity is an undivided element itself.

        In entities of `IfcSpatialStructureElement` type, a `CompositionType`
        attribute can have 3 values (described by `IfcElementCompositionEnum`):
            COMPLEX - a group or aggregation of similar elements
            ELEMENT - a (undivided) element itself
            PARTIAL - a subelement or part

        To make data reading simpler, we only focus on ELEMENT entities.
        So this function returns True when an `IfcSpatialStructureElement`
        entity's `CompositionType` equals ELEMENT value."""
        return self.composition_type == 'ELEMENT'

    @property
    def object_type(self):
        """Get the entity's related object type."""
        if self._object_type is None:
            self._object_type = self._load_object_type()
        return self._object_type

    @property
    def parent(self):
        """Get the entity's related parent."""
        if self._parent is None:
            self._parent = self._load_parent()
        return self._parent

    @property
    def kids(self):
        """Get the entity's related kids."""
        if self._kids is None:
            self._kids = self._load_kids()
        return self._kids

    @property
    def property_sets(self):
        """Get a tuple of the entity's related property sets."""
        if self._property_sets is None:
            self._property_sets = self._load_property_sets()
        return self._property_sets

    @property
    def quantities(self):
        """Get a tuple of related quantities (see `IfcElementQuantity`)."""
        if self._quantities is None:
            self._quantities = self._load_quantities()
        return self._quantities

    def _load_object_type(self):
        """Try to get the object type description.

        When entity is inherits from `IfcObject`, an `IsDefinedBy` inverse
        gives a set of [0:?] `IfcRelDefines` entities (each can be an
        `IfcRelDefinesByProperties` or an `IfcRelDefinesByType`).
        Here we are only interested in the `IfcRelDefinesByType` and his
        `RelatingType` attribute that describes the object type entity.

        :return IfcObjectEntity: The object type instance if any, else None.
        """
        if self._raw.is_a('IfcObject'):
            for cur_rel in self._raw.IsDefinedBy:
                if cur_rel.is_a('IfcRelDefinesByType'):
                    # Return the first occurence found (in principle
                    #  IFC specification allows one at max in `IsDefinedBy`).
                    return IfcObjectEntity(
                        cur_rel.RelatingType, self._schema,
                        expected_types=('IfcTypeProduct',))
        return None

    def _load_parent(self):
        """Try to load parent entity using relating object link.

        :return IfcObjectEntity: The parent entity if any, else None.
        """
        raw_parent_entity = self._get_relating_object()
        if raw_parent_entity is not None:
            return IfcObjectEntity(raw_parent_entity, schema=self._schema)
        return None

    def _load_kids(self):
        """Try to load kid entities using related objects links.

        :return tuple:
            The kid entities (as IfcObjectEntity instances) if any, else None.
        """
        raw_kid_entities = self._get_related_objects()
        if raw_kid_entities is not None:
            return tuple(
                IfcObjectEntity(cur_raw_kid_entity, schema=self._schema)
                for cur_raw_kid_entity in raw_kid_entities)
        return None

    def _get_relating_object(self):
        """Try to get a relating object (it is the parent entity).

        When entity inherits from `IfcObjectDefinition`, a `Decomposes` inverse
        gives a set of [0:1] `IfcRelDecomposes` (or inherited), which have a
        `RelatingObject` attribute pointing to the entity's parent.
        If entity is an `IfcElement`, a `ContainedInStructure` attribute is
        defined as a set of [0:1] `IfcRelContainedInSpatialStructure` which
        have a `RelatingStructure` attribute pointing to the entity's parent.
        With an `IfcFeatureElementSubtraction` a `VoidsElements` inverse gives
        an `IfcRelVoidsElement` having a `RelatingBuildingElement` pointing to
        the entity's parent.

        :return IfcObjectDefinition: The relating object found.
            (for correct use do not forget to instanciate an `IfcObjectEntity`
            with this raw entity instance - `IfcObjectDefinition` instance)
        """
        # /!\ try entity types in reverse inheritance order
        #  (for example `IfcElement` is a subtype of `IfcObjectDefinition`)
        if (self._raw.is_a('IfcFeatureElementSubtraction')
                and len(self._raw.VoidsElements) == 1):
            return self._raw.VoidsElements[0].RelatingBuildingElement
        elif (self._raw.is_a('IfcElement')
              and len(self._raw.ContainedInStructure) == 1):
            return self._raw.ContainedInStructure[0].RelatingStructure
        elif (self._raw.is_a('IfcObjectDefinition')
              and len(self._raw.Decomposes) == 1):
            return self._raw.Decomposes[0].RelatingObject
        return None

    def _get_related_objects(self):
        """Try to get a set of related objects (they are the kids' entity).

        When entity inherits from `IfcObjectDefinition`, an `IsDecomposedBy`
        inverse returns a set of [1:?] `IfcRelDecomposes` (or inherited
        relation), which have a `RelatedObjects` attribute.
        If entity is an `IfcZone` instance, `IsGroupedBy` inverse is used.

        :return tuple: The list of related objects found.
            Objects are `IfcObjectDefinition` instances (do not forget later
            to instanciate `IfcObjectEntity` with these raw entity instances).
        """
        if self._raw.is_a('IfcObjectDefinition'):
            if self._raw.is_a('IfcZone'):
                entity_relations = self._raw.IsGroupedBy
            else:
                entity_relations = self._raw.IsDecomposedBy
            # Now retrieve all `IfcObjectDefinition` from each `RelatedObjects`
            #  (note that each is already a tuple of `IfcObjectDefinition`).
            related_objects = ()
            for cur_relation in entity_relations:
                related_objects += cur_relation.RelatedObjects
            return related_objects
        return None

    def _load_property_sets(self):
        """Try to get a set of property sets.

        When entity inherits from `IfcObject`, an `IsDefinedBy` inverse returns
        a set of [0:1] `IfcRelDefines` entities.
        `IfcRelDefines` has 2 subtypes:
            - `IfcRelDefinesByProperties`, has a `RelatingPropertyDefinition`
                attribute describing property sets throught the `HasProperties`
                attribute (returns a tuple of `IfcPropertySet`).
            - `IfcRelDefinesByType`, has a `RelatingType` attribute that
                describes property sets throught the `HasPropertySets`
                attribute (returns a tuple of `IfcPropertySet`).

        In this function we are only interested in `IfcRelDefinesByProperties`,
        ignoring all `IfcElementQuantity` entities (see quantities).

        :return tuple:
            All property set instances (`IfcObjectEntityPropertySetBase`).
        """
        raw_psets = ()
        # get data from `IfcObjectDefinition` entities...
        # ...which can be an `IfcObject`...
        if self._raw.is_a('IfcObject'):
            for cur_rel in self._raw.IsDefinedBy:
                if cur_rel.is_a('IfcRelDefinesByProperties'):
                    cur_raw_pset = cur_rel.RelatingPropertyDefinition
                    # ignore `IfcElementQuantity` properties (see quantities)
                    if not cur_raw_pset.is_a('IfcElementQuantity'):
                        raw_psets += (cur_raw_pset,)
        # ...or an `IfcTypeObject`
        elif self._raw.is_a('IfcTypeObject'):
            raw_psets = self._raw.HasPropertySets
        else:
            # print some debug alerts about the ignored `raw_data` property set
            IfcBaseEntity._print_debug_warning(self._raw, item='pset')

        # return our `IfcObjectEntityPropertySetBase` stuff
        if len(raw_psets) > 0:
            psets = ()
            for cur_raw_pset in raw_psets:
                pset = IfcObjectEntityPropertySetBase.create(
                    cur_raw_pset, schema=self._schema)
                if pset is not None:
                    psets += (pset,)
            return psets
        return None

    def _load_quantities(self):
        """Try to get a set of the entity's quantities.

        When entity inherits from `IfcObject`, an `IsDefinedBy` inverse returns
        a set of [0:1] `IfcRelDefines` entities.
        `IfcRelDefines` has 2 subtypes:
            - `IfcRelDefinesByProperties`, has a `RelatingPropertyDefinition`
                attribute describing property sets throught the `HasProperties`
                attribute (returns a tuple of `IfcPropertySet`).
            - `IfcRelDefinesByType`, has a `RelatingType` attribute that
                describes property sets throught the `HasPropertySets`
                attribute (returns a tuple of `IfcPropertySet`).

        In this function we are only interested in `IfcRelDefinesByProperties`,
        and particularly all `IfcElementQuantity` entities.

        :return tuple:
            All entity's quantity instances (`IfcObjectEntityQuantityBase`).
        """
        if self._raw.is_a('IfcObject'):
            # focus on `IfcRelDefinesByProperties` and `IfcElementQuantity`
            raw_elmt_qty = tuple(
                cur_rel.RelatingPropertyDefinition
                for cur_rel in self._raw.IsDefinedBy
                if (cur_rel.is_a('IfcRelDefinesByProperties')
                    and cur_rel.RelatingPropertyDefinition.is_a(
                        'IfcElementQuantity')))

            # Each `IfcElementQuantity` has a `Quantities` attribute that
            #  returns a set of `IfcPhysicalQuantity`.
            # Return our `IfcObjectEntityQuantityBase` stuff with that.
            all_quantities = ()
            for cur_elmt_qty in raw_elmt_qty:
                for cur_qty in cur_elmt_qty.Quantities:
                    qty = IfcObjectEntityQuantityBase.create(
                        cur_qty, schema=self._schema)
                    if qty is not None:
                        all_quantities += (qty,)
            return all_quantities
        return None

    def get_property_set_codenames(self):
        """Get a tuple of all entity's property sets codename.

        :return tuple: All entity's property sets codename.
        """
        return tuple(pset.codename for pset in self.property_sets or ())

    def get_property_set(self, pset_codename):
        """Get an entity's property set, searching by its codename.

        :param str pset_codename: The entity property set's codename to find.
        :return IfcObjectEntityPropertySetBase:
            The entity's property set instance found.
        """
        for pset in self.property_sets or ():
            if pset_codename == pset.codename:
                return pset
        return None

    def get_property_codenames(self, *, pset_codename=None):
        """Get a tuple of all property's codenames in the entity's
        property sets.

        :param str pset_codename: (optional, default None)
            The property set's codename from which property's codenames are
            requested. If `None`, all property's codenames of all entity's
            property sets are returned.
        :return tuple: All property's codenames found.
        """
        prop_codenames = ()
        for pset in self.property_sets or ():
            if pset_codename is None or pset.codename == pset_codename:
                prop_codenames += pset.get_property_codenames()
        return prop_codenames

    def get_properties(self, *, pset_codename=None):
        """Get a tuple of all entity's properties.

        :param str pset_codename: (optional, default None)
            The property set's codename from which property's are requested.
            If `None`, a merge of all entity property sets' values is done.
        :return tuple: All entity's property instances found.
        """
        # note that we do not care if `pset_codename` exists or not
        props = ()
        for pset in self.property_sets or ():
            if pset_codename is None or pset.codename == pset_codename:
                props += copy.copy(pset.properties) or ()
        return props

    def get_property(self, property_codename, *, pset_codename=None):
        """Get an entity's property, searching by its codename.

        :param str property_codename: The entity's property codename.
        :param str pset_codename: (optional, default None)
            The property set's codename in which the property is searched.
            If `None`, the property is looked into all entity's property sets
            (returning the first occurence found).
        :return IfcObjectEntityPropertyBase: The entity's property found.
        """
        for prop in self.get_properties(pset_codename=pset_codename):
            if property_codename == prop.codename:
                return prop
        return None

    def get_property_value(self, property_codename, *, pset_codename=None):
        """Try to get an entity property's value/unit.

        :param str property_codename: The entity's property codename.
        :param str pset_codename: (optional, default None)
            The property set's codename in which the property is searched.
            If `None`, the property is looked into all entity's property sets
            (returning the first occurence found).
        :return tuple: (property_value, property_unit,)
        """
        prop = self.get_property(
            property_codename, pset_codename=pset_codename)
        if prop is not None:
            return (prop.value, prop.unit,)
        return (None, None)
