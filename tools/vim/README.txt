Vim Tools for Enaml Files
-------------------------

These are simple indent rules and syntax highlighting files for Vim. They
inherit most of their behavior from their Python counterparts in the standard
Vim runtime. Just place them in their appropriate directories under your .vim/
directory. Add the following line to ~/.vimrc to enable them for .enaml files:

    autocmd BufNewFile,BufRead,BufEnter *.enaml setfiletype enaml

