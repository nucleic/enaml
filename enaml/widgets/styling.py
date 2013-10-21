#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from collections import defaultdict

from atom.api import Atom, Unicode, Typed, observe

from enaml.application import deferred_call
from enaml.core.declarative import Declarative, d_


class Rule(Declarative):
    """ A declarative class for defining a rule in a rule set.

    If a Rule has a parent, it must be a RuleSet object. Failing to
    adhere to this condition is a programming error.

    """
    #: The style property to which the rule applies. An empty property
    #: name will cause the rule to be ignored. The properties supported
    #: by a widget are toolkit dependent.
    property = d_(Unicode())

    #: The value to apply to the style property. An empty value will
    #: cause the rule to be ignored.
    value = d_(Unicode())

    def destroy(self):
        """ A reimplemented destructor.

        This will inform the style cache when the rule is destroyed.

        """
        super(Rule, self).destroy()
        StyleCache.rule_destroyed(self)

    @observe('property', 'value')
    def _invalidate_cache(self, change):
        """ An observer which invalidates the style rule cache.

        """
        if change['type'] == 'update':
            StyleCache.rule_invalidated(self)


class RuleSet(Declarative):
    """ A declarative class for defining a rule set in a style sheet.

    If a RuleSet has a parent, it must be a StyleSheet object. Failing
    to adhere to this condition is a programming error.

    """
    #: The type name of the element which will match the rule set. A
    #: comma separated string can be used to match more than one
    #: element. An empty string will match all elements.
    element_name = d_(Unicode())

    #: The name of the widget style class which will match the rule set.
    #: A comma separated string can be used to match more than one style
    #: class. An empty string will match all style classes.
    style_class = d_(Unicode())

    #: The object name of the widget which will match the rule set. A
    #: comma separated string can be used to match more than one object
    #: name. An empty string will match all object names.
    object_name = d_(Unicode())

    #: The pseudostate to which the style applies. A comma separated
    #: string can be used to match more than one pseudostate. An empty
    #: string will match all pseudostates. The pseudostates supported
    #: by a widget are toolkit dependent.
    pseudostate = d_(Unicode())

    #: The subcontrol to which the style applies. A comma separated
    #: string can be used to match more than one subcontrol. An empty
    #: string indicates no subcontrol. The subcontrols supported by a
    #: widget are toolkit dependent.
    subcontrol = d_(Unicode())

    #: The private cached tuple of element names.
    _elements = Typed(tuple)

    #: The private cached tuple of style classes.
    _style_classes = Typed(tuple)

    #: The private cached tuple of object names.
    _object_names = Typed(tuple)

    #: The private cached tuple of pseudostates.
    _pseudostates = Typed(tuple)

    #: The private cached tuple of subcontrols.
    _subcontrols = Typed(tuple)

    @property
    def element_names(self):
        """ A property which gets the cached tuple of element names.

        """
        names = self._element_names
        if names is None:
            names = tuple(s.strip() for s in self.element_name.split(u','))
            self._element_names = names
        return names

    @property
    def style_classes(self):
        """ A property which gets the cached tuple of style classes.

        """
        classes = self._style_classes
        if classes is None:
            classes = tuple(s.strip() for s in self.style_class.split(u','))
            self._style_classes = classes
        return classes

    @property
    def object_names(self):
        """ A property which gets the cached tuple of object names.

        """
        names = self._object_names
        if names is None:
            names = tuple(s.strip() for s in self.object_name.split(u','))
            self._object_names = names
        return names

    @property
    def pseudostates(self):
        """ A property which gets the cached tuple of pseudostates.

        """
        states = self._pseudostates
        if states is None:
            states = tuple(s.strip() for s in self.pseudostate.split(u','))
            self._pseudostates = states
        return states

    @property
    def subcontrols(self):
        """ A property which gets the cached tuple of subcontrols.

        """
        controls = self._subcontrols
        if controls is None:
            controls = tuple(s.strip() for s in self.subcontrol.split(u','))
            self._subcontrols = controls
        return controls

    def rules(self):
        """ Get the rules declared for the rule set.

        Returns
        -------
        result : list
            The list of Rule objects declared for the rule set.

        """
        return [c for c in self.children if isinstance(c, Rule)]

    def match(self, item):
        """ Get the whether or not the rule set matches an item.

        Parameters
        ----------
        item : Stylable
            The stylable item to test for a match.

        Returns
        -------
        result : int
            An integer indicating the match for the given item. A value
            less than zero indicates no match. A value greater than or
            equal to zero indicates a match and the specificity of that
            match.

        """
        specificity = 0

        object_names = self.object_names
        if object_names:
            name = item.name
            if name and name in object_names:
                specificity += 4
            else:
                return -1

        style_classes = self.style_classes
        if style_classes:
            style_class = item.style_class
            if style_class and style_class in style_classes:
                specificity += 2
            else:
                return -1

        element_names = self.element_names
        if element_names:
            for t in type(item).__mro__:
                if t.__name__ in element_names:
                    specificity += 1
                    break
            else:
                return -1

        return specificity

    def destroy(self):
        """ A reimplemented destructor.

        This will inform the style cache when the rule set is destroyed.

        """
        super(RuleSet, self).destroy()
        StyleCache.rule_set_destroyed(self)

    @observe('element_name', 'style_class', 'object_name')
    def _invalidate_match_cache(self, change):
        """ An observer which invalidates the rule set match cache.

        """
        if change['type'] == 'update':
            name = change['name']
            setattr(self, '_%ss' % name, None)  # clear the property cache
            StyleCache.rule_set_match_invalidated(self)

    @observe('pseudostate', 'subcontrol')
    def _invalidate_data_cache(self, change):
        """ An observer which invalidates the rule set data cache.

        """
        if change['type'] == 'update':
            name = change['name']
            setattr(self, '_%ss' % name, None)  # clear the property cache
            StyleCache.rule_set_data_invalidated(self)


class StyleSheet(Declarative):
    """ A declarative class for defining Enaml widget style sheets.

    """
    def destroy(self):
        """ A reimplemented destructor.

        This method informs the style cache when the sheet is destroyed.

        """
        super(StyleSheet, self).destroy()
        StyleCache.style_sheet_destroyed(self)

    def rule_sets(self):
        """ Get the rule sets declared for the style sheet.

        Returns
        -------
        result : list
            The list of RuleSet objects declared for the style sheet.

        """
        return [c for c in self.children if isinstance(c, RuleSet)]


class Stylable(Declarative):
    """ A mixin class for defining stylable declarative objects.

    This class should be mixed in to any declarative class which wishes
    to support Enaml stylesheets.

    """
    #: The style class to which this item belongs. An empty string
    #: indicates the widget does not belong to any style class.
    style_class = d_(Unicode())

    def destroy(self):
        """ A reimplemented destructor.

        This method informs the style cache when the item is destroyed.

        """
        super(Stylable, self).destroy()
        StyleCache.item_destroyed(self)

    def style_sheet(self):
        """ Get the style sheet defined on the item.

        Returns
        -------
        result : StyleSheet or None
            The last StyleSheet child defined on the item, or None if
            the item has no such child.

        """
        for child in reversed(self.children):
            if isinstance(child, StyleSheet):
                return child

    def restyle(self):
        """ Restyle the object.

        This method will be called when the style dependencies for the
        object have changed. It should be reimplemented in a subclass
        to forward the call to the toolkit as needed.

        """
        pass


class RestyleTask(Atom):
    """ A task which is posted to restyle items as needed.

    """
    #: The set of stylable items which need to be restyled.
    dirty = Typed(set, ())

    def __call__(self):
        StyleCache._restyle_task = None
        for item in self.dirty:
            item.restyle()


class StyleCache(object):
    """ An object which manages the style sheet caches.

    All interaction with this class occurs through it's public class
    methods.

    """
    #: A private mapping of item to tuple of matching StyleSheet.
    _style_sheet_cache = {}

    #: A private mapping of item to tuple of matching RuleSet.
    _rule_set_cache = {}

    #: A private mapping of Rule to toolkit data.
    _toolkit_rule_cache = {}

    #: A private mapping of StyleSheet to set of matched items.
    _style_sheet_items = defaultdict(set)

    #: A private mapping of RuleSet to set of matched items.
    _rule_set_items = defaultdict(set)

    #: A RestyleTask which collapses item restyle requests.
    _restyle_task = None

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    @classmethod
    def style_sheets(cls, item):
        """ Get the style sheets which apply to the given item.

        Parameters
        ----------
        item : Stylable
            The stylable item of interest.

        Returns
        -------
        result : tuple
            A tuple of StyleSheet objects which apply to the item,
            in order of ascending precedence.

        """
        cache = cls._style_sheet_cache
        if item in cache:
            return cache[item]
        sheets = []
        parent = item.parent
        if parent is not None:
            sheets.extend(cls.style_sheets(parent))
        sheet = item.style_sheet()
        if sheet is not None:
            sheets.append(sheet)
        sheets = tuple(sheets)
        cache[item] = sheets
        items = cls._style_sheet_items
        for sheet in sheets:
            items[sheet].add(item)
        return sheets

    @classmethod
    def rule_sets(cls, item):
        """ Get the rule sets which apply to the given item.

        Parameters
        ----------
        item : Stylable
            The stylable item of interest.

        Returns
        -------
        result : tuple
            A tuple of RuleSet objects which apply to the item,
            in order of ascending precedence.

        """
        cache = cls._rule_set_cache
        if item in cache:
            return cache[item]
        rule_sets = []
        for sheet in cls.style_sheets(item):
            matches = []
            for rule_set in sheet.rule_sets():
                specificity = rule_set.match(item)
                if specificity >= 0:
                    matches.append((specificity, rule_set))
            if matches:
                matches.sort()
                rule_sets.extend(rule_set for _, rule_set in matches)
        rule_sets = tuple(rule_sets)
        cache[item] = rule_sets
        items = cls._rule_set_items
        for rule_set in rule_sets:
            items[rule_set].add(item)
        return rule_sets

    @classmethod
    def toolkit_rule(cls, rule, translate):
        """ Get the toolkit representation of a rule.

        This method will return the cached version of the toolkit rule,
        if available, or invoke the translator to create the cached
        version. The cached toolkit rule will be cleared when the rule
        object is invalidated.

        Parameters
        ----------
        rule : Rule
            The style rule of interest.

        translate : callable
            A callable which accepts a single Rule argument and returns
            a toolkit representation of the rule. The returned value is
            cached until the rule is invalidated.

        Returns
        -------
        result : object
            The toolkit representation of the rule.

        """
        cache = cls._toolkit_rule_cache
        if rule in cache:
            return cache[rule]
        result = cache[rule] = translate(rule)
        return result

    #--------------------------------------------------------------------------
    # Framework API
    #--------------------------------------------------------------------------
    @classmethod
    def rule_destroyed(cls, rule):
        pass

    @classmethod
    def rule_set_destroyed(cls, rule_set):
        pass

    @classmethod
    def style_sheet_destroyed(cls, sheet):
        pass

    @classmethod
    def item_destroyed(cls, item):
        pass

    @classmethod
    def rule_invalidated(cls, rule):
        """ Notify the cache that the rule data is invalid.

        Parameters
        ----------
        rule_set : Rule
            The rule object of interest.

        """
        cls._toolkit_rule_cache.pop(rule, None)
        cls._restyle_rule_set_data(rule.parent)

    @classmethod
    def rule_set_match_invalidated(cls, rule_set):
        """ Notify the cache that the rule set match is invalid.

        Parameters
        ----------
        rule_set : RuleSet
            The rule set object of interest.

        """
        cls._restyle_rule_set_match(rule_set)

    @classmethod
    def rule_set_data_invalidated(cls, rule_set):
        """ Notify the cache that the rule set data is invalid.

        Parameters
        ----------
        rule_set : RuleSet
            The rule set object of interest.

        """
        cls._restyle_rule_set_data(rule_set)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def __new__(cls, *args, **kwargs):
        raise TypeError('Cannot create instances of StyleCache')

    @classmethod
    def _request_items_restyle(cls, items):
        """ Request a restyle of the given items.

        This method will post a task on the event queue to collapse
        multiple restyle requests for the same objects.

        Parameters
        ----------
        items : iterable
            An iterable of Stylable items which should be restyled.

        """
        task = cls._restyle_task
        if task is None:
            task = cls._restyle_task = RestyleTask()
            deferred_call(task)
        task.dirty.update(items)

    @classmethod
    def _restyle_rule_set_data(cls, rule_set):
        """ Restyle the items styled by a given rule set.

        This method will request a restyle of all items styled by the
        given rule set. This should be called when the rule data of a
        rule set changes, but not when the match spec has changed.

        Parameters
        ----------
        rule_set : RuleSet
            The rule set object of interest. It is not necessary for
            this rule set to exist in the cache.

        """
        items = cls._rule_set_items.get(rule_set)
        if items is not None:
            cls._request_items_restyle(items)

    @classmethod
    def _restyle_rule_set_match(cls, rule_set):
        """ Restyle the items styled by a given rule set.

        This method will request a restyle of all items styled by the
        style sheet owning the rule set. This should be called only
        when the match spec of the rule set has changed.

        Parameters
        ----------
        rule_set : RuleSet
            The rule set object of interest. It is not necessary for
            this rule set to exist in the cache.

        """
        cls._rule_set_items.pop(rule_set, None)
        items = cls._style_sheet_items.get(rule_set.parent)
        if items is not None:
            cache = cls._rule_set_cache
            for item in items:
                cache.pop(item, None)
            cls._request_items_restyle(items)
