#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod
from collections import defaultdict, namedtuple
import imp
import marshal
import os
import struct
import sys
import types

from .enaml_compiler import EnamlCompiler, COMPILER_VERSION
from .parser import parse


# The magic number as symbols for the current Python interpreter. These
# define the naming scheme used when create cached files and directories.
MAGIC = imp.get_magic()
try:
    MAGIC_TAG = 'enaml-py%s%s-cv%s' % (
        sys.version_info.major, sys.version_info.minor, COMPILER_VERSION,
    )
except AttributeError:
    # Python 2.6 compatibility
    MAGIC_TAG = 'enaml-py%s%s-cv%s' % (
        sys.version_info[0], sys.version_info[1], COMPILER_VERSION,
    )
CACHEDIR = '__enamlcache__'


#------------------------------------------------------------------------------
# Import Helpers
#------------------------------------------------------------------------------
EnamlFileInfo = namedtuple('EnamlFileInfo', 'src_path, cache_path, cache_dir')


def make_file_info(src_path):
    """ Create an EnamlFileInfo object for the given src_path.

    Parameters
    ----------
    src_path : string
        The full path to the .enaml file.

    Returns
    -------
    result : FileInfo
        A properly populated EnamlFileInfo object.

    """
    root, tail = os.path.split(src_path)
    fnroot, _ = os.path.splitext(tail)
    cache_dir = os.path.join(root, CACHEDIR)
    fn = ''.join((fnroot, '.', MAGIC_TAG, os.path.extsep, 'enamlc'))
    cache_path = os.path.join(cache_dir, fn)
    return EnamlFileInfo(src_path, cache_path, cache_dir)


class abstractclassmethod(classmethod):
    """ A backport of the Python 3's abc.abstractclassmethod.

    """
    __isabstractmethod__ = True

    def __init__(self, func):
        func.__isabstractmethod__ = True
        super(abstractclassmethod, self).__init__(func)


#------------------------------------------------------------------------------
# Abstract Enaml Importer
#------------------------------------------------------------------------------
class AbstractEnamlImporter(object):
    """ An abstract base class which defines the api required to
    implement an Enaml importer.

    """
    __metaclass__ = ABCMeta

    # Count the number of times an importer has been installed.
    # Only uninstall it when the count hits 0 again. This permits
    # proper nesting of import contexts.
    _install_count = defaultdict(int)

    @classmethod
    def install(cls):
        """ Appends this importer into sys.meta_path.

        """
        cls._install_count[cls] += 1
        if cls not in sys.meta_path:
            sys.meta_path.append(cls)

    @classmethod
    def uninstall(cls):
        """ Removes this importer from sys.meta_path.

        """
        cls._install_count[cls] -= 1
        if cls._install_count[cls] <= 0 and cls in sys.meta_path:
            sys.meta_path.remove(cls)

    #--------------------------------------------------------------------------
    # Python Import API
    #--------------------------------------------------------------------------
    @classmethod
    def find_module(cls, fullname, path=None):
        """ Finds the given Enaml module and returns an importer, or
        None if the module is not found.

        """
        loader = cls.locate_module(fullname, path)
        if loader is not None:
            if not isinstance(loader, AbstractEnamlImporter):
                msg = 'Enaml imports received invalid loader object %s'
                raise ImportError(msg % loader)
            return loader

    def load_module(self, fullname):
        """ Loads and returns the Python module for the given enaml path.
        If a module already exisist in sys.path, the existing module is
        reused, otherwise a new one is created.

        """
        code, path = self.get_code()
        if fullname in sys.modules:
            mod = sys.modules[fullname]
        else:
            mod = sys.modules[fullname] = types.ModuleType(fullname)
        mod.__loader__ = self
        mod.__file__ = path
        # Even though the import hook is already installed, this is a
        # safety net to avoid potentially hard to find bugs if code has
        # manually installed and removed a hook. The contract here is
        # that the import hooks are always installed when executing the
        # module code of an Enaml file.
        with imports():
            exec code in mod.__dict__
        return mod

    #--------------------------------------------------------------------------
    # Abstract API
    #--------------------------------------------------------------------------
    @abstractclassmethod
    def locate_module(cls, fullname, path=None):
        """ Searches for the given Enaml module and returns an instance
        of AbstractEnamlImporter on success.

        Paramters
        ---------
        fullname : string
            The fully qualified name of the module.

        path : string or None
            The subpackage __path__ for submodules and subpackages
            or None if a top-level module.

        Returns
        -------
        result : Instance(AbstractEnamlImporter) or None
            If the Enaml module is located an instance of the importer
            that will perform the rest of the operations is returned.
            Otherwise, returns None.

        """
        raise NotImplementedError

    @abstractmethod
    def get_code(self):
        """ Loads and returns the code object for the Enaml module and
        the full path to the module for use as the __file__ attribute
        of the module.

        Returns
        -------
        result : (code, path)
            The Python code object for the .enaml module, and the full
            path to the module as a string.

        """
        raise NotImplementedError


#------------------------------------------------------------------------------
# Default Enaml Importer
#------------------------------------------------------------------------------
class EnamlImporter(AbstractEnamlImporter):
    """ The standard Enaml importer which can import Enaml modules from
    standard locations on the python path and compile them appropriately
    to .enamlc files.

    This importer adopts the Python 3 conventions and scheme for creating
    the cached files and setting the __file__ attribute on the module.
    See this discussion thread for more info:
    http://www.mail-archive.com/python-dev@python.org/msg45203.html

    """
    @classmethod
    def locate_module(cls, fullname, path=None):
        """ Searches for the given Enaml module and returns an instance
        of this class on success.

        Paramters
        ---------
        fullname : string
            The fully qualified name of the module.

        path : list or None
            The subpackage __path__ for submodules and subpackages
            or None if a top-level module.

        Returns
        -------
        results : Instance(AbstractEnamlImporter) or None
            If the Enaml module is located an instance of the importer
            that will perform the rest of the operations is returned.
            Otherwise, returns None.

        """
        # We're looking inside a package and 'path' the package path
        if path is not None:
            modname = fullname.rsplit('.', 1)[-1]
            leaf = ''.join((modname, os.path.extsep, 'enaml'))
            for stem in path:
                enaml_path = os.path.join(stem, leaf)
                file_info = make_file_info(enaml_path)
                if (os.path.exists(file_info.src_path) or
                    os.path.exists(file_info.cache_path)):
                    return cls(file_info)

        # We're trying a load a package
        elif '.' in fullname:
            return

        # We're doing a direct import
        else:
            leaf = fullname + os.path.extsep + 'enaml'
            for stem in sys.path:
                enaml_path = os.path.join(stem, leaf)
                file_info = make_file_info(enaml_path)
                if (os.path.exists(file_info.src_path) or
                    os.path.exists(file_info.cache_path)):
                    return cls(file_info)

    def __init__(self, file_info):
        """ Initialize an importer object.

        Parameters
        ----------
        file_info : EnamlFileInfo
            An instance of EnamlFileInfo.

        """
        self.file_info = file_info

    def _load_cache(self, file_info):
        """ Loads and returns the code object for the given file info.

        Parameters
        ----------
        file_info : EnamlFileInfo
            The file info object for the file.

        Returns
        -------
        result : types.CodeType
            The code object for the file.

        """
        with open(file_info.cache_path, 'rb') as cache_file:
            cache_file.read(8)
            code = marshal.load(cache_file)
        return code

    def _write_cache(self, code, ts, file_info):
        """ Write the cached file for then given info, creating the
        cache directory if needed. This call will suppress any
        IOError or OSError exceptions.

        Parameters
        ----------
        code : types.CodeType
            The code object to write to the cache.

        ts : int
            The integer timestamp for the file.

        file_info : EnamlFileInfo
            The file info object for the file.

        """
        try:
            if not os.path.exists(file_info.cache_dir):
                os.mkdir(file_info.cache_dir)
            with open(file_info.cache_path, 'w+b') as cache_file:
                cache_file.write(MAGIC)
                cache_file.write(struct.pack('i', ts))
                marshal.dump(code, cache_file)
        except (OSError, IOError):
            pass

    def _get_magic_info(self, file_info):
        """ Loads and returns the magic info for the given path.

        Parameters
        ----------
        file_info : EnamlFileInfo
            The file info object for the file.

        Returns
        -------
        result : (magic, timestamp)
            The magic string and integer timestamp for the file.

        """
        with open(file_info.cache_path, 'rb') as cache_file:
            magic = cache_file.read(4)
            timestamp = struct.unpack('i', cache_file.read(4))[0]
        return (magic, timestamp)

    def get_code(self):
        """ Loads and returns the code object for the Enaml module and
        the full path to the module for use as the __file__ attribute
        of the module.

        Returns
        -------
        result : (code, path)
            The Python code object for the .enaml module, and the full
            path to the module as a string.

        """
        # If the .enaml file does not exists, just use the .enamlc file.
        # We can presume that the latter exists because it was already
        # checked by the loader. Should the situation ever arise that
        # it was deleted between then and now, an IOError is more
        # informative than an ImportError.
        file_info = self.file_info
        if not os.path.exists(file_info.src_path):
            code = self._load_cache(file_info)
            return (code, file_info.src_path)

        # Use the cached file if it exists and is current
        src_mod_time = int(os.path.getmtime(file_info.src_path))
        if os.path.exists(file_info.cache_path):
            magic, ts = self._get_magic_info(file_info)
            if magic == MAGIC and src_mod_time <= ts:
                code = self._load_cache(file_info)
                return (code, file_info.src_path)

        # Otherwise, compile from source and attempt to cache
        with open(file_info.src_path, 'rU') as src_file:
            src = src_file.read()
        ast = parse(src)
        code = EnamlCompiler.compile(ast, file_info.src_path)
        self._write_cache(code, src_mod_time, file_info)
        return (code, file_info.src_path)


#------------------------------------------------------------------------------
# Enaml Imports Context
#------------------------------------------------------------------------------
class imports(object):
    """ A context manager that hooks/unhooks the enaml meta path
    importer for the duration of the block. The helps user avoid
    unintended consequences of a having a meta path importer slow
    down all of their other imports.

    """
    #: The framework-wide importers in use. We always have the default
    #: importer available, unless it is explicitly removed.
    __importers = [EnamlImporter]

    @classmethod
    def get_importers(cls):
        """ Returns a tuple of currently active importers in use for the
        framework.

        """
        return tuple(cls.__importers)

    @classmethod
    def add_importer(cls, importer):
        """ Add an importer to the list of importers for use with the
        framework. It must be a subclass of AbstractEnamlImporter.
        The most recently appended importer is used first. If the
        importer has already been added, this is a no-op. To move
        an importer up in precedence, remove it and add it again.

        """
        if not issubclass(importer, AbstractEnamlImporter):
            msg = ('An Enaml importer must be a subclass of '
                   'AbstractEnamlImporter. Got %s instead.')
            raise TypeError(msg % importer)
        importers = cls.__importers
        if importer not in importers:
            importers.append(importer)

    @classmethod
    def remove_importer(cls, importer):
        """ Removes the importer from the list of active importers.
        If the importer is not in the list, this is a no-op.

        """
        importers = cls.__importers
        if importer in importers:
            importers.remove(importer)

    def __init__(self):
        """ Initializes an Enaml import context.

        """
        self.importers = self.get_importers()

    def __enter__(self):
        """ Installs the current importer upon entering the context.

        """
        # Install the importers reversed so that the newest ones
        # get first crack at the import on sys.meta_path.
        for importer in reversed(self.importers):
            importer.install()

    def __exit__(self, *args, **kwargs):
        """ Uninstalls the current importer when leaving the context.

        """
        # We removed in standard order since thats a more efficient
        # operation on sys.meta_path.
        for importer in self.importers:
            importer.uninstall()

