" Vim indent file
" Language:	Enaml
" Maintainer:	Robert Kern <rkern@enthought.com>
" URL:		http://github.com/nucleic/enaml
" Last Change:	2012 Feb 16

" Only load this indent file when no other was loaded.
if exists("b:did_indent")
  finish
endif

" Read the Python indent file
if version < 600
  so <sfile>:p:h/python.vim
else
  runtime! indent/python.vim
  unlet b:did_indent
endif

let b:did_indent = 1

" vim:sw=2
