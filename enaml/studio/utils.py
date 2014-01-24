#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
def rank_sort(extensions):
    """ Sort a list of extensions according to their configuration rank.

    Parameters
    ----------
    extensions : list
        The list of Extension objects of interest.

    Returns
    -------
    result : list
        The extensions sorted from highest to lowest rank.

    """
    key = lambda ext: ext.configuration.get(u'rank', 0)
    return sorted(extensions, key=key, reverse=True)


def highest_ranked(extensions):
    """ Return the extension with the highest rank.

    Parameters
    ----------
    extensions : list
        The list of Extension objects of interest.

    Returns
    -------
    result : Extension
        The extensions with the highest rank.

    """
    key = lambda ext: ext.configuration.get(u'rank', 0)
    return max(extensions, key=key)
