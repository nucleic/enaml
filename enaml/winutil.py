#------------------------------------------------------------------------------
# Copyright (c) 2013-2025, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
"""Windows utility module - re-exports from Rust extension."""

from enaml._rust import (
    WinEnum,
    load_icon,
    create_oic_sample,
    create_oic_hand,
    create_oic_ques,
    create_oic_bang,
    create_oic_note,
    create_oic_winlogo,
    create_oic_warning,
    create_oic_error,
    create_oic_information,
    create_oic_shield,
)

# Create module-level WinEnum constants for common OIC values
OIC_SAMPLE = create_oic_sample()
OIC_HAND = create_oic_hand()
OIC_QUES = create_oic_ques()
OIC_BANG = create_oic_bang()
OIC_NOTE = create_oic_note()
OIC_WINLOGO = create_oic_winlogo()
OIC_WARNING = create_oic_warning()
OIC_ERROR = create_oic_error()
OIC_INFORMATION = create_oic_information()
OIC_SHIELD = create_oic_shield()

__all__ = [
    'WinEnum',
    'load_icon',
    'OIC_SAMPLE',
    'OIC_HAND',
    'OIC_QUES',
    'OIC_BANG',
    'OIC_NOTE',
    'OIC_WINLOGO',
    'OIC_WARNING',
    'OIC_ERROR',
    'OIC_INFORMATION',
    'OIC_SHIELD',
]
