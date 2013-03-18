#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Int, List, Enum, Typed, observe

from enaml.core.declarative import Declarative, d_

from .abstractitemmodel import AbstractItemModel
from .baseitem import BaseItem


Orientation = Enum('horizontal', 'vertical')


class GridModel(AbstractItemModel):

    _orientation = Orientation()

    _series = List()

    _headers = List()

    def __init__(self, orientation):
        self._orientation = orientation

    def add_series(self, series):
        self._series.append(series)

    def remove_series(self, series):
        pass

    def series_changed(self, series):
        pass

    #--------------------------------------------------------------------------
    # AbstractItemModel API
    #--------------------------------------------------------------------------
    def row_count(self):
        if self._orientation == 'horizontal':
            return len(self._series)
        return len(self._headers)

    def column_count(self):
        if self._orientation == 'horizontal':
            return len(self._headers)
        return len(self._series)

    def data(self, row, column):
        if self._orientation == 'horizontal':
            s = self._series[row]
            i = s.items[column]
        else:
            s = self._series[column]
            i = s.items[row]
        return i.get_data(s.model)

    def background(self, row, column):
        if self._orientation == 'horizontal':
            s = self._series[row]
            i = s.items[column]
        else:
            s = self._series[column]
            i = s.items[row]
        return i.get_background(s.model)


class Grid(Declarative):

    orientation = d_(Orientation())

    headers = d_(List())

    grid_model = Typed(GridModel)

    def _default_grid_model(self):
        g = GridModel(self.orientation)
        g._headers = self.headers
        return g

    def child_added(self, child):
        if isinstance(child, GridSeries):
            self.grid_model.add_series(child)

    def child_removed(self, child):
        if isinstance(child, GridSeries):
            self.grid_model.remove_series(child)


class GridSeries(Declarative):

    header = d_(Typed(BaseItem))

    model = d_(Typed(object))

    items = d_(List(BaseItem))

    _index = Int()

    @observe(('header', 'items'))
    def _update_grid_model(self, change):
        parent = self.parent
        if isinstance(parent, Grid):
            parent.grid_model.series_changed(self)
