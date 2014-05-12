#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
""" Declarative classes which implement style sheet styling.

"""
from collections import defaultdict

from atom.api import Atom, Unicode, Typed, observe

from enaml.application import Application, deferred_call
from enaml.core.declarative import Declarative, d_


class Setter(Declarative):
    """ A declarative class for defining a style field setter.

    A :class:`Setter` is declared as a child of a :class:`Style`.
    It defines the value to be applied to a style field.

    """
    # The name 'field' was chosen since 'property' is a Python builtin.
    # 'field' also has the added benefit of being the same length as
    # 'value' which means that a group of Setter objects will be nicely
    # aligned in an Enaml source definition.
    #
    #: The style field to which this setter applies.
    field = d_(Unicode())

    #: The value to apply to the style field.
    value = d_(Unicode())

    def destroy(self):
        """ A reimplemented destructor.

        This will notify the :class:`StyleCache` when the setter is
        destroyed.

        """
        super(Setter, self).destroy()
        StyleCache._setter_destroyed(self)

    @observe('field', 'value')
    def _invalidate_cache(self, change):
        if change['type'] == 'update':
            StyleCache._setter_invalidated(self)


# Internal string split cache
_MAX_CACHE = 2000

_SPLIT_CACHE = {}

def _comma_split(text):
    cache = _SPLIT_CACHE
    if text in cache:
        return cache[text]
    if len(cache) >= _MAX_CACHE:
        cache.clear()
    result = tuple(s.strip() for s in text.split(u',') if s)
    cache[text] = result
    return result


class Style(Declarative):
    """ A declarative class for defining a style sheet style.

    A :class:`Style` is declared as a child of a :class:`StyleSheet`.
    It uses child :class:`Setter` objects to define the style fields
    to apply to widgets which are a match for the style.

    A :class:`Style` may have an arbitrary number of :class:`Setter`
    children.

    """
    #: The type name of the element which will match the style. An
    #: empty string will match all elements. Multiple elements can
    #: be separated by a comma and will match using logical OR
    #: semantics.
    element = d_(Unicode())

    #: The name of the widget style class which will match the style.
    #: An empty string will match all style classes. Multiple classes
    #: can be separated by a comma and will match using logical OR
    #: semantics.
    style_class = d_(Unicode())

    #: The object name of the widget which will match the style. An
    #: empty string will match all object names. Multiple object names
    #: can be separated by a comma and will match using logical OR
    #: semantics.
    object_name = d_(Unicode())

    #: The pseudo-class which must be active for the style to apply. An
    #: empty string will apply the syle for all pseudo-classes. Multiple
    #: classes can be separated by a colon will match using logical AND
    #: semantics. Commas can be used to separate multiple classes which
    #: will match using logical OR semantics.
    pseudo_class = d_(Unicode())

    #: The pseudo-element to which the style applies. An empty string
    #: indicates the style applies to the primary element. Multiple
    #: pseudo elements can be separated comma and match using logical
    #: OR semantics.
    pseudo_element = d_(Unicode())

    def setters(self):
        """ Get the :class:`Setter` objects declared for the style.

        Returns
        -------
        result : list
            The :class:`Setter` objects declared for the style.

        """
        return [c for c in self.children if isinstance(c, Setter)]

    def match(self, item):
        """ Get whether or not the style matches an item.

        Parameters
        ----------
        item : :class:`Stylable`
            The item to test for a style match.

        Returns
        -------
        result : int
            The match value for the item. A value less than zero
            indicates no match. A value greater than or equal to zero
            indicates a match and the specificity of the match.

        """
        specificity = 0

        if self.object_name:
            item_name = item.name
            if item_name and item_name in _comma_split(self.object_name):
                specificity += 0x100
            else:
                return -1

        if self.style_class:
            item_class = item.style_class
            if item_class:
                count = 0
                style_classes = _comma_split(self.style_class)
                for item_class in item_class.split():
                    if item_class in style_classes:
                        count += 1
                if count > 0:
                    specificity += 0x10 * count
                else:
                    return -1
            else:
                return -1

        if self.element:
            elements = _comma_split(self.element)
            for t in type(item).__mro__:
                if t.__name__ in elements:
                    specificity += 0x1
                    break
            else:
                return -1

        return specificity

    def destroy(self):
        """ A reimplemented destructor.

        This will notify the :class:`StyleCache` when the style is
        destroyed.

        """
        super(Style, self).destroy()
        StyleCache._style_destroyed(self)

    def child_added(self, child):
        """ A reimplemented child added event handler.

        This will notify the :class:`StyleCache` if the :class:`Setter`
        children of the style have changed.

        """
        super(Style, self).child_added(child)
        if self.is_initialized and isinstance(child, Setter):
            StyleCache._style_setters_changed(self)

    def child_removed(self, child):
        """ A reimplemented child removed event handler.

        This will notify the :class:`StyleCache` if the :class:`Setter`
        children of the style have changed.

        """
        super(Style, self).child_removed(child)
        if self.is_initialized and isinstance(child, Setter):
            StyleCache._style_setters_changed(self)

    @observe('element', 'style_class', 'object_name')
    def _invalidate_match_cache(self, change):
        if change['type'] == 'update':
            StyleCache._style_match_invalidated(self)

    @observe('pseudo_class', 'pseudo_element')
    def _invalidate_pseudo_cache(self, change):
        if change['type'] == 'update':
            StyleCache._style_pseudo_invalidated(self)


class StyleSheet(Declarative):
    """ A declarative class for defining a widget style sheet.

    A :class:`StyleSheet` is declared as a child of a :class:`Stylable`
    widget. It uses child :class:`Style` objects to apply styling to its
    parent widget **and all of the widget's decendents**. A
    :class:`StyleSheet` can also be provided to the global
    :class:`Application <enaml.application.Application>`, in which case
    the styling will be applied to all stylable widgets. The effective
    style sheet for a widget is the union of all its ancestor style
    sheets plus the application style sheet.

    A :class:`StyleSheet` may have an arbitrary number of :class:`Style`
    children. The child style objects are applied to a widget in the
    order of their match specificity within the style sheet.

    """
    def destroy(self):
        """ A reimplemented destructor.

        This will notify the :class:`StyleCache` when the style sheet
        is destroyed.

        """
        super(StyleSheet, self).destroy()
        StyleCache._style_sheet_destroyed(self)

    def styles(self):
        """ Get the :class:`Style` objects declared for the style sheet.

        Returns
        -------
        result : list
            The :class:`Style` objects declared for the style sheet.

        """
        return [c for c in self.children if isinstance(c, Style)]

    def child_added(self, child):
        """ A reimplemented child added event handler.

        This will notify the :class:`StyleCache` if the :class:`Style`
        children of the style sheet have changed.


        """
        super(StyleSheet, self).child_added(child)
        if self.is_initialized and isinstance(child, Style):
            StyleCache._style_sheet_styles_changed(self)

    def child_removed(self, child):
        """ A reimplemented child removed event handler.

        This will notify the :class:`StyleCache` if the :class:`Style`
        children of the style sheet have changed.

        """
        super(StyleSheet, self).child_removed(child)
        if self.is_initialized and isinstance(child, Style):
            StyleCache._style_sheet_styles_changed(self)


class Stylable(Declarative):
    """ A mixin class for defining stylable declarative objects.

    This class can be used as a mixin with any
    :class:`Declarative <enaml.core.Declarative>` class which wishes
    to support style sheets.

    """
    #: The style class to which this item belongs. Multiple classes
    #: can be separated with whitespace. An empty string indicates
    #: the widget does not belong to any style class.
    style_class = d_(Unicode())

    def destroy(self):
        """ A reimplemented destructor.

        This will notify the :class:`StyleCache` when the stylable item
        is destroyed.

        """
        super(Stylable, self).destroy()
        StyleCache._item_destroyed(self)

    def style_sheet(self):
        """ Get the :class:`StyleSheet` defined on the item.

        Returns
        -------
        result : :class:`StyleSheet` or None
            The last :class:`StyleSheet` child defined on the item,
            or None if the item has no such child.

        """
        for child in reversed(self.children):
            if isinstance(child, StyleSheet):
                return child

    def restyle(self):
        """ Restyle the object.

        This method will be called when the style dependencies for the
        object have changed. It should be reimplemented in a subclass
        to take appropriate action for the restyle.

        """
        pass

    def parent_changed(self, old, new):
        """ A reimplemented parent changed event handler.

        This will notifiy the :class:`StyleCache` if the parent of
        the item has changed.

        """
        super(Stylable, self).parent_changed(old, new)
        if self.is_initialized:
            StyleCache._item_parent_changed(self)

    def child_added(self, child):
        """ A reimplemented child added event handler.

        This will notify the :class:`StyleCache` if the
        :class:`StyleSheet` children of the item have changed.

        """
        super(Stylable, self).child_added(child)
        if self.is_initialized and isinstance(child, StyleSheet):
            StyleCache._item_style_sheet_changed(self)

    def child_removed(self, child):
        """ A reimplemented child removed event handler.

        This will notify the :class:`StyleCache` if the
        :class:`StyleSheet` children of the item have changed.

        """
        super(Stylable, self).child_removed(child)
        if self.is_initialized and isinstance(child, StyleSheet):
            StyleCache._item_style_sheet_changed(self)

    @observe('style_class')
    def _invalidate_style_class(self, change):
        if change['type'] == 'update':
            StyleCache._item_style_class_invalidated(self)


class _RestyleTask(Atom):
    dirty = Typed(set, ())
    def __call__(self):
        StyleCache._restyle_task = None
        for item in self.dirty:
            item.restyle()


def _app_style_sheet():
    app = Application.instance()
    if app is not None:
        sheet = app.style_sheet
        if sheet is not None and not sheet.is_initialized:
            sheet.initialize()
        return sheet


class StyleCache(object):
    """ An object which manages the styling caches.

    All interaction with this class is through public class methods.
    This class should be used by code which implements the styling for
    a stylable item. The public API methods can be used to query for
    the Style object which matchs a :class:`Stylable` item.

    """
    #: A private mapping of item to tuple of matching StyleSheet.
    _item_style_sheets = {}

    #: A private mapping of item to tuple of matching Style.
    _item_styles = {}

    #: A private mapping of StyleSheet to set of matched items.
    _style_sheet_items = defaultdict(set)

    #: A private mapping of Style to set of matched items.
    _style_items = defaultdict(set)

    #: The set of all items which have been queried for style.
    _queried_items = set()

    #: A private mapping of Setter to toolkit data.
    _toolkit_setters = {}

    #: A RestyleTask which collapses item restyle requests.
    _restyle_task = None

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    @classmethod
    def style_sheets(cls, item):
        """ Get the :class:`StyleSheet` objects which apply to an item.

        Parameters
        ----------
        item : :class:`Stylable`
            The stylable item of interest.

        Returns
        -------
        result : tuple
            The :class:`StyleSheet` objects which apply to the item,
            in order of ascending precedence.

        """
        cache = cls._item_style_sheets
        if item in cache:
            return cache[item]
        sheets = []
        parent = item.parent
        if parent is not None:
            sheets.extend(cls.style_sheets(parent))
        else:
            app_sheet = _app_style_sheet()
            if app_sheet is not None:
                sheets.append(app_sheet)
        if isinstance(item, Stylable):  # parent may not be a Stylable
            sheet = item.style_sheet()
            if sheet is not None:
                sheets.append(sheet)
            sheet_items = cls._style_sheet_items
            for sheet in sheets:
                sheet_items[sheet].add(item)
        sheets = cache[item] = tuple(sheets)
        cls._queried_items.add(item)
        return sheets

    @classmethod
    def styles(cls, item):
        """ Get the :class:`Style` objects which apply to an item.

        Parameters
        ----------
        item : :class:`Stylable`
            The stylable item of interest.

        Returns
        -------
        result : tuple
            The :class:`Style` objects which apply to the item, in
            order of ascending precedence.

        """
        cache = cls._item_styles
        if item in cache:
            return cache[item]
        styles = []
        for sheet in cls.style_sheets(item):
            matches = []
            for style in sheet.styles():
                specificity = style.match(item)
                if specificity >= 0:
                    matches.append((specificity, len(matches), style))
            if matches:
                matches.sort()
                styles.extend(style for _1, _2, style in matches)
        style_items = cls._style_items
        for style in styles:
            style_items[style].add(item)
        styles = cache[item] = tuple(styles)
        return styles

    @classmethod
    def toolkit_setter(cls, setter, translate):
        """ Get the toolkit representation of a setter.

        This method will return the cached toolkit setter, if available,
        or invoke the translator to create the cached setter. The cached
        toolkit setter will be cleared when the setter is invalidated.

        Parameters
        ----------
        setter : :class:`Setter`
            The style setter of interest.

        translate : callable
            A callable which accepts a single :class:`Setter` argument
            and returns a toolkit representation of the setter. The
            returned value is cached until the setter is invalidated.

        Returns
        -------
        result : object
            The toolkit representation of the setter.

        """
        cache = cls._toolkit_setters
        if setter in cache:
            return cache[setter]
        result = cache[setter] = translate(setter)
        return result

    #--------------------------------------------------------------------------
    # Protected Framework API
    #--------------------------------------------------------------------------
    @classmethod
    def _setter_destroyed(cls, setter):
        # If the parent of the setter is not being destroyed, it will
        # get a child_removed event which will trigger a restyle pass.
        # That logic does not need to be repeated here.
        cls._toolkit_setters.pop(setter, None)

    @classmethod
    def _style_destroyed(cls, style):
        # If the parent of the style is not being destroyed, it will
        # get a child_removed event which will trigger a restyle pass.
        # That logic does not need to be repeated here.
        cls._style_items.pop(style, None)

    @classmethod
    def _style_sheet_destroyed(cls, sheet):
        # If the parent of the sheet is not being destroyed, it will
        # get a child_removed event which will trigger a restyle pass.
        # That logic does not need to be repeated here.
        cls._style_sheet_items.pop(sheet, None)

    @classmethod
    def _item_destroyed(cls, item):
        cls._queried_items.discard(item)
        sheets = cls._item_style_sheets.pop(item, None)
        if sheets is not None:
            sheet_items = cls._style_sheet_items
            for sheet in sheets:
                if sheet in sheet_items:
                    sheet_items[sheet].discard(item)
        styles = cls._item_styles.pop(item, None)
        if styles is not None:
            style_items = cls._style_items
            for style in styles:
                if style in style_items:
                    style_items[style].discard(item)

    @classmethod
    def _setter_invalidated(cls, setter):
        cls._toolkit_setters.pop(setter, None)
        items = cls._style_items.get(setter.parent)
        if items is not None:
            cls._request_restyle(items)

    @classmethod
    def _style_match_invalidated(cls, style):
        cls._style_items.pop(style, None)
        items = cls._style_sheet_items.get(style.parent)
        if items is not None:
            cache = cls._item_styles
            for item in items:
                cache.pop(item, None)
            cls._request_restyle(items)

    @classmethod
    def _style_pseudo_invalidated(cls, style):
        items = cls._style_items.get(style)
        if items is not None:
            cls._request_restyle(items)

    @classmethod
    def _item_style_class_invalidated(cls, item):
        styles = cls._item_styles.pop(item, None)
        if styles is not None:
            style_items = cls._style_items
            for style in styles:
                if style in style_items:
                    style_items[style].discard(item)
        cls._request_restyle((item,))

    @classmethod
    def _style_setters_changed(cls, style):
        items = cls._style_items.get(style)
        if items is not None:
            cls._request_restyle(items)

    @classmethod
    def _style_sheet_styles_changed(cls, sheet):
        items = cls._style_sheet_items.get(sheet, None)
        if items is not None:
            styles = cls._item_styles
            for item in items:
                styles.pop(item, None)
            cls._request_restyle(items)

    @classmethod
    def _item_parent_changed(cls, item):
        # changing a parent is equivalent to changing style sheets
        cls._item_style_sheet_changed(item)

    @classmethod
    def _item_style_sheet_changed(cls, item):
        item_styles = cls._item_styles
        item_sheets = cls._item_style_sheets
        items = [i for i in item.traverse() if i in cls._queried_items]
        for item in items:
            sheets = item_sheets.pop(item, None)
            if sheets is not None:
                sheet_items = cls._style_sheet_items
                for sheet in sheets:
                    if sheet in sheet_items:
                        sheet_items[sheet].discard(item)
            styles = item_styles.pop(item, None)
            if styles is not None:
                style_items = cls._style_items
                for style in styles:
                    if style in style_items:
                        style_items[style].discard(item)
        cls._request_restyle(items)

    @classmethod
    def _app_sheet_changed(cls):
        if cls._queried_items:
            cls._item_style_sheets.clear()
            cls._item_styles.clear()
            cls._style_sheet_items.clear()
            cls._style_items.clear()
            cls._request_restyle(cls._queried_items)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def __new__(cls, *args, **kwargs):
        raise TypeError('Cannot create instances of StyleCache')

    @classmethod
    def _request_restyle(cls, items):
        task = cls._restyle_task
        if task is None:
            task = cls._restyle_task = _RestyleTask()
            deferred_call(task)
        task.dirty.update(items)
