Emacs major mode for editing Enaml files
========================================

This file creates a new mode (based on python-mode) to highlight keywords
specific to Enaml files.  Just copy the file enaml.el to a location in your
load-path (typically "~/.emacs.d" for an individual user).  Then add the
following lines to your .emacs file::

(require 'enaml)
(setq auto-mode-alist (cons '("\\.enaml$" . enaml-mode) auto-mode-alist))

Inline python code should still be highlighted as in python-mode.
