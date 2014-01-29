#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
def rank_sort(extensions, reverse=False):
    """ Sort a list of extensions according to their rank.

    Parameters
    ----------
    extensions : list
        The list of Extension objects of interest. They should have
        an integer 'rank' property in order to be usefully sorted.

    reverse : bool, optional
        Wether to sort the extensions from highest to lowest rank
        instead of lowest to highest. The default is False.

    Returns
    -------
    result : list
        The extensions sorted from lowest to highest rank, or highest
        to lowest if 'reverse' is True.

    """
    key = lambda ext: ext.get_property(u'rank', 0)
    return sorted(extensions, key=key, reverse=reverse)


def highest_ranked(extensions):
    """ Return the extension with the highest rank.

    Parameters
    ----------
    extensions : list
        The list of Extension objects of interest. They should have
        an integer 'rank' property in order to be usefully compared.

    Returns
    -------
    result : Extension
        The extensions with the highest rank.

    """
    key = lambda ext: ext.get_property(u'rank', 0)
    return max(extensions, key=key)