{{ objname }}
{{ underline }}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}


Backends
--------

Qt
^^

.. inheritance-diagram::
    {{ module|replace('widgets.', 'qt.qt_') }}.Qt{{ objname }}
    :parts: 1

.. autoclass:: {{ module|replace('widgets.', 'qt.qt_') }}.Qt{{ objname }}


Wx
^^

.. inheritance-diagram::
    {{ module|replace('widgets.', 'wx.wx_') }}.Wx{{ objname }}
    :parts: 1

.. autoclass:: {{ module|replace('widgets.', 'wx.wx_') }}.Wx{{ objname }}

