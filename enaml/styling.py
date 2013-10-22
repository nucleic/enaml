#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from collections import defaultdict

from atom.api import Atom, Unicode, Typed, observe

from enaml.application import Application, deferred_call
from enaml.core.declarative import Declarative, d_


class Setter(Declarative):
    """ A declarative class for defining a setter in a Style.

    """
    #: The name of the property to set.
    property = d_(Unicode())

    #: The value to apply to the property.
    value = d_(Unicode())

    def destroy(self):
        """ A reimplemented destructor.

        This will notify the style cache when the setter is destroyed.

        """
        super(Setter, self).destroy()
        StyleCache.setter_destroyed(self)

    @observe('property', 'value')
    def _invalidate_cache(self, change):
        """ An observer which invalidates the style setter cache.

        """
        if change['type'] == 'update':
            StyleCache.setter_invalidated(self)


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
    """ A declarative class for defining a style in a StyleSheet.

    """
    #: The type name of the element which will match the style. An
    #: empty string will match all elements. Multiple elements can
    #: be separated by a comma.
    element = d_(Unicode())

    #: The name of the widget style class which will match the style.
    #: An empty string will match all style classes. Multiple classes
    #: can be separated by a comma.
    style_class = d_(Unicode())

    #: The object name of the widget which will match the style. An
    #: empty string will match all object names. Multiple object names
    #: can be separated by a comma.
    object_name = d_(Unicode())

    #: The pseudo-class which must be active for the style to apply. An
    #: empty string will apply the syle for all pseudo-classes. Multiple
    #: psuedo-classes should be joined by a colon.
    pseudo_class = d_(Unicode())

    #: The pseudo-element to which the style applies. An empty string
    #: indicates the style applies to the main element.
    pseudo_element = d_(Unicode())

    def setters(self):
        """ Get the setters declared for the style.

        Returns
        -------
        result : list
            The list of Setter objects declared for the style.

        """
        return [c for c in self.children if isinstance(c, Setter)]

    def match(self, item):
        """ Get whether or not the style matches an item.

        Parameters
        ----------
        item : Stylable
            The stylable item to test for a match.

        Returns
        -------
        result : int
            An integer indicating the match for the given item. A value
            less than zero indicates no match. A value greater than or
            equal to zero indicates a match and the specificity of the
            match.

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

        This will notify the style cache when the style is destroyed.

        """
        super(Style, self).destroy()
        StyleCache.style_destroyed(self)

    def child_added(self, child):
        """ A reimplemented child added event handler.

        This handler notifies the style cache that the setter children
        of the style have changed.

        """
        super(Style, self).child_added(child)
        if self.is_initialized and isinstance(child, Setter):
            StyleCache.style_setters_changed(self)

    def child_removed(self, child):
        """ A reimplemented child removed event handler.

        This handler notifies the style cache that the setter children
        of the style have changed.

        """
        super(Style, self).child_removed(child)
        if self.is_initialized and isinstance(child, Setter):
            StyleCache.style_setters_changed(self)

    @observe('element', 'style_class', 'object_name')
    def _invalidate_match_cache(self, change):
        """ An observer which invalidates the style match cache.

        """
        if change['type'] == 'update':
            StyleCache.style_match_invalidated(self)

    @observe('pseudo_class', 'pseudo_element')
    def _invalidate_pseudo_cache(self, change):
        """ An observer which invalidates the style pseudo cache.

        """
        if change['type'] == 'update':
            StyleCache.style_pseudo_invalidated(self)


class StyleSheet(Declarative):
    """ A declarative class for defining an Enaml style sheet.

    """
    def destroy(self):
        """ A reimplemented destructor.

        This will notify the style cache when the sheet is destroyed.

        """
        super(StyleSheet, self).destroy()
        StyleCache.style_sheet_destroyed(self)

    def styles(self):
        """ Get the styles declared for the style sheet.

        Returns
        -------
        result : list
            The list of Style objects declared for the style sheet.

        """
        return [c for c in self.children if isinstance(c, Style)]

    def child_added(self, child):
        """ A reimplemented child added event handler.

        This handler notifies the style cache that the style children
        of the style sheet have changed.

        """
        super(StyleSheet, self).child_added(child)
        if self.is_initialized and isinstance(child, Style):
            StyleCache.style_sheet_styles_changed(self)

    def child_removed(self, child):
        """ A reimplemented child removed event handler.

        This handler notifies the style cache that the style children
        of the style sheet have changed.

        """
        super(StyleSheet, self).child_removed(child)
        if self.is_initialized and isinstance(child, Style):
            StyleCache.style_sheet_styles_changed(self)


class Stylable(Declarative):
    """ A mixin class for defining stylable declarative objects.

    This class should be mixed-in to any declarative class which
    should support Enaml style sheets.

    """
    #: The style class to which this item belongs. Multiple classes
    #: can be separated with whitespace. An empty string indicates
    #: the widget does not belong to any style class.
    style_class = d_(Unicode())

    def destroy(self):
        """ A reimplemented destructor.

        This will notify the style cache when the item is destroyed.

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
        to forward the call to the toolkit proxy.

        """
        pass

    @observe('style_class')
    def _invalidate_style_class(self, change):
        """ An observer which invalidates the style class cache.

        """
        if change['type'] == 'update':
            StyleCache.item_style_class_invalidated(self)


class _RestyleTask(Atom):
    """ A task which is posted to collapse item restyle requests.

    """
    #: The set of stylable items which require restyling.
    dirty = Typed(set, ())

    def __call__(self):
        StyleCache._restyle_task = None
        for item in self.dirty:
            item.restyle()


def _app_style_sheet():
    app = Application.instance()
    if app is not None:
        return app.style_sheet


class StyleCache(object):
    """ An object which manages the styling caches.

    All interaction with this class is through public class methods.

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
        """ Get the style sheets which apply to the given item.

        Parameters
        ----------
        item : Stylable
            The stylable item of interest.

        Returns
        -------
        result : tuple
            A tuple of StyleSheet objects which apply to the item, in
            order of ascending precedence.

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
            items = cls._style_sheet_items
            for sheet in sheets:
                items[sheet].add(item)
        sheets = cache[item] = tuple(sheets)
        cls._queried_items.add(item)
        return sheets

    @classmethod
    def styles(cls, item):
        """ Get the styles which apply to the given item.

        Parameters
        ----------
        item : Stylable
            The stylable item of interest.

        Returns
        -------
        result : tuple
            A tuple of Style objects which apply to the item, in order
            of ascending precedence.

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
        items = cls._style_items
        for style in styles:
            items[style].add(item)
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
        setter : Setter
            The style setter of interest.

        translate : callable
            A callable which accepts a single Setter argument and
            returns a toolkit representation of the setter. The
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
    # Framework API
    #--------------------------------------------------------------------------
    @classmethod
    def setter_destroyed(cls, setter):
        pass

    @classmethod
    def style_destroyed(cls, style):
        pass

    @classmethod
    def style_sheet_destroyed(cls, sheet):
        pass

    @classmethod
    def item_destroyed(cls, item):
        pass

    @classmethod
    def setter_invalidated(cls, setter):
        """ Notify the cache that the setter is invalid.

        Parameters
        ----------
        setter : Setter
            The setter object of interest.

        """
        cls._toolkit_setters.pop(setter, None)
        items = cls._style_items.get(setter.parent)
        if items is not None:
            cls._request_restyle(items)

    @classmethod
    def style_match_invalidated(cls, style):
        """ Notify the cache that the style match is invalid.

        Parameters
        ----------
        style : Style
            The style object of interest.

        """
        cls._style_items.pop(style, None)
        items = cls._style_sheet_items.get(style.parent)
        if items is not None:
            cache = cls._item_styles
            for item in items:
                cache.pop(item, None)
            cls._request_restyle(items)

    @classmethod
    def style_pseudo_invalidated(cls, style):
        """ Notify the cache that the style pseudo data is invalid.

        Parameters
        ----------
        style : Style
            The style object of interest.

        """
        items = cls._style_items.get(style)
        if items is not None:
            cls._request_restyle(items)

    @classmethod
    def item_style_class_invalidated(cls, item):
        """ Notify the cache that the item style class is invalid.

        Parameters
        ----------
        item : Stylable
            The item of interest.

        """
        styles = cls._item_styles.pop(item, None)
        if styles is not None:
            items = cls._style_items
            for style in styles:
                items[style].discard(item)
        cls._request_restyle((item,))

    @classmethod
    def style_setters_changed(cls, style):
        """ Notify the cache that the style setters have changed.

        Parameters
        ----------
        style : Style
            The style object of interest.

        """
        items = cls._style_items.get(style)
        if items is not None:
            cls._request_restyle(items)

    @classmethod
    def style_sheet_styles_changed(cls, sheet):
        """ Notify the cache that the sheet styles have changed.

        Parameters
        ----------
        sheet : StyleSheet
            The style sheet object of interest.

        """
        items = cls._style_sheet_items.get(sheet, None)
        if items is not None:
            styles = cls._item_styles
            for item in items:
                styles.pop(item, None)
            cls._request_restyle(items)

    @classmethod
    def app_sheet_changed(cls):
        """ Notify the cache that the app style sheet has changed.

        """
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
            task = cls._restyle_task = _RestyleTask()
            deferred_call(task)
        task.dirty.update(items)
