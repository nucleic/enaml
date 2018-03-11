/*-----------------------------------------------------------------------------
| Copyright (c) 2013, Nucleic Development Team.
|
| Distributed under the terms of the Modified BSD License.
|
| The full license is in the file COPYING.txt, distributed with this software.
|----------------------------------------------------------------------------*/
#include "inttypes.h"
#include <algorithm>
#include <iostream>
#include <sstream>
#include "pythonhelpers.h"
#include "py23compat.h"

#ifdef __clang__
#pragma clang diagnostic ignored "-Wdeprecated-writable-strings"
#endif

#ifdef __GNUC__
#pragma GCC diagnostic ignored "-Wwrite-strings"
#endif

using namespace PythonHelpers;


enum FontStyle
{
    Normal,
    Italic,
    Oblique
};


enum FontStretch
{
    UltraCondensed,
    ExtraCondensed,
    Condensed,
    SemiCondensed,
    Unstretched,
    SemiExpanded,
    Expanded,
    ExtraExpanded,
    UltraExpanded
};


enum FontCaps
{
    MixedCase,
    AllUppercase,
    AllLowercase,
    SmallCaps,
    Capitalize
};


typedef struct {
    PyObject_HEAD
    PyObject* tkdata;   // Toolkit specific font representation
    PyObject* family;   // Font family name as a string
    int32_t pointsize;
    int32_t weight;
    FontStyle style;
    FontCaps caps;
    FontStretch stretch;
} Font;


static PyObject*
Font_new( PyTypeObject* type, PyObject* args, PyObject* kwargs )
{
    PyObject* family;
    int32_t pointsize = -1;
    int32_t weight = -1;
    FontStyle style = Normal;
    FontCaps caps = MixedCase;
    FontStretch stretch = Unstretched;
    static char* kwlist[] = { "family", "size", "weight", "style", "caps", "stretch", 0 };
#if PY_MAJOR_VERSION >= 3
    if( !PyArg_ParseTupleAndKeywords(
        args, kwargs, "U|iiiii", kwlist, &family, &pointsize, &weight, &style, &caps, &stretch ) )
        return 0;
#else
    if( !PyArg_ParseTupleAndKeywords(
        args, kwargs, "S|iiiii", kwlist, &family, &pointsize, &weight, &style, &caps, &stretch ) )
        return 0;
#endif
    PyObjectPtr fontptr( PyType_GenericNew( type, args, kwargs ) );
    if( !fontptr )
        return 0;
    Font* font = reinterpret_cast<Font*>( fontptr.get() );
    Py_INCREF(family);
    font->family = family;
    font->pointsize = std::max( -1, pointsize );
    font->weight = std::max( -1, std::min( weight, 99 ) );
    font->style = ( style < Normal || style > Oblique ) ? Normal : style;
    font->caps = ( caps < MixedCase || caps > Capitalize ) ? MixedCase : caps;
    font->stretch = ( stretch < UltraCondensed || stretch > UltraExpanded ) ? Unstretched : stretch;
    return fontptr.release();
}


static void
Font_dealloc( Font* self )
{
    Py_CLEAR( self->tkdata );
    Py_CLEAR( self->family );
    Py_TYPE(self)->tp_free( reinterpret_cast<PyObject*>( self ) );
}


static PyObject*
Font_repr( Font* self )
{
    static const char* style_reprs[] = {
        "style=Normal, ",
        "style=Italic, ",
        "style=Oblique, "
    };
    static const char* caps_reprs[] = {
        "caps=MixedCase",
        "caps=AllUppercase",
        "caps=AllLowercase",
        "caps=SmallCaps",
        "caps=Capitalize"
    };
    static const char* stretch_reprs[] = {
        "stretch=UltraCondensed)",
        "stretch=ExtraCondensed)",
        "stretch=Condensed)",
        "stretch=SemiCondensed)",
        "stretch=Unstretched)",
        "stretch=SemiExpanded)",
        "stretch=Expanded)",
        "stretch=ExtraExpanded)",
        "stretch=UltraExpanded)"
    };
    std::ostringstream ostr;
    ostr << "Font(family=\"" << Py23Str_AS_STRING( self->family ) << "\", ";
    ostr << "pointsize=" << self->pointsize << ", ";
    ostr << "weight=" << self->weight << ", ";
    ostr << style_reprs[self->style] << caps_reprs[self->caps] << stretch_reprs[self->stretch];
    return Py23Str_FromString(ostr.str().c_str());
};


static PyObject*
Font_get_family( Font* self, void* context )
{
    Py_INCREF( self->family );
    return self->family;
}


static PyObject*
Font_get_pointsize( Font* self, void* context )
{
    return PyLong_FromLong( self->pointsize );
}


static PyObject*
Font_get_weight( Font* self, void* context )
{
    return PyLong_FromLong( self->weight );
}


static PyObject*
Font_get_style( Font* self, void* context )
{
    return PyLong_FromLong( static_cast<long>( self->style ) );
}


static PyObject*
Font_get_caps( Font* self, void* context )
{
    return PyLong_FromLong( static_cast<long>( self->caps ) );
}

static PyObject*
Font_get_stretch( Font* self, void* context )
{
    return PyLong_FromLong( static_cast<long>( self->stretch ) );
}


static PyObject*
Font_get_tkdata( Font* self, void* context )
{
    if( !self->tkdata )
        Py_RETURN_NONE;
    Py_INCREF( self->tkdata );
    return self->tkdata;
}


static int
Font_set_tkdata( Font* self, PyObject* value, void* context )
{
    // don't let users do something silly which would require GC
    if( reinterpret_cast<PyObject*>( self ) == value )
        return 0;
    PyObject* old = self->tkdata;
    self->tkdata = value;
    Py_XINCREF( value );
    Py_XDECREF( old );
    return 0;
}


static PyGetSetDef
Font_getset[] = {
    { "family", ( getter )Font_get_family, 0,
      "Get the family name for the font." },
    { "pointsize", ( getter )Font_get_pointsize, 0,
      "Get the point size for the font." },
    { "weight", ( getter )Font_get_weight, 0,
      "Get the weight for the font." },
    { "style", ( getter )Font_get_style, 0,
      "Get the style enum for the font." },
    { "caps", ( getter )Font_get_caps, 0,
      "Get the caps enum for the font." },
    { "stretch", ( getter )Font_get_stretch, 0,
      "Get the stretch enum for the font." },
    { "_tkdata", ( getter )Font_get_tkdata, ( setter )Font_set_tkdata,
      "Get and set the toolkit specific font representation." },
    { 0 } // sentinel
};


PyTypeObject Font_Type = {
    PyVarObject_HEAD_INIT( &PyType_Type, 0 )
    "fontext.Font",                         /* tp_name */
    sizeof( Font ),                         /* tp_basicsize */
    0,                                      /* tp_itemsize */
    (destructor)Font_dealloc,               /* tp_dealloc */
    (printfunc)0,                           /* tp_print */
    (getattrfunc)0,                         /* tp_getattr */
    (setattrfunc)0,                         /* tp_setattr */
#if PY_VERSION_HEX >= 0x03050000
	( PyAsyncMethods* )0,                   /* tp_as_async */
#elif PY_VERSION_HEX >= 0x03000000
	( void* ) 0,                            /* tp_reserved */
#else
	( cmpfunc )0,                           /* tp_compare */
#endif
    (reprfunc)Font_repr,                    /* tp_repr */
    (PyNumberMethods*)0,                    /* tp_as_number */
    (PySequenceMethods*)0,                  /* tp_as_sequence */
    (PyMappingMethods*)0,                   /* tp_as_mapping */
    (hashfunc)0,                            /* tp_hash */
    (ternaryfunc)0,                         /* tp_call */
    (reprfunc)0,                            /* tp_str */
    (getattrofunc)0,                        /* tp_getattro */
    (setattrofunc)0,                        /* tp_setattro */
    (PyBufferProcs*)0,                      /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,                     /* tp_flags */
    0,                                      /* Documentation string */
    (traverseproc)0,                        /* tp_traverse */
    (inquiry)0,                             /* tp_clear */
    (richcmpfunc)0,                         /* tp_richcompare */
    0,                                      /* tp_weaklistoffset */
    (getiterfunc)0,                         /* tp_iter */
    (iternextfunc)0,                        /* tp_iternext */
    (struct PyMethodDef*)0,                 /* tp_methods */
    (struct PyMemberDef*)0,                 /* tp_members */
    Font_getset,                            /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    (descrgetfunc)0,                        /* tp_descr_get */
    (descrsetfunc)0,                        /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)0,                            /* tp_init */
    (allocfunc)PyType_GenericAlloc,         /* tp_alloc */
    (newfunc)Font_new,                      /* tp_new */
    (freefunc)0,                            /* tp_free */
    (inquiry)0,                             /* tp_is_gc */
    0,                                      /* tp_bases */
    0,                                      /* tp_mro */
    0,                                      /* tp_cache */
    0,                                      /* tp_subclasses */
    0,                                      /* tp_weaklist */
    (destructor)0                           /* tp_del */
};


struct module_state {
    PyObject *error;
};


static PyMethodDef
fontext_methods[] = {
    { 0 } // Sentinel
};


static PyObject*
new_enum_class( const char* name )
{
    PyObjectPtr pyname( Py23Str_FromString( name ) );
    if( !pyname )
        return 0;
    PyObjectPtr args( PyTuple_New( 0 ) );
    if( !args )
        return 0;
    PyDictPtr kwargs( PyDict_New() );
    if( !kwargs )
        return 0;
    PyObjectPtr modname( Py23Str_FromString( "fontext" ) );
    if( !modname )
        return 0;
    if( !kwargs.set_item( "__module__", modname ) )
        return 0;
    PyObjectPtr callargs( PyTuple_Pack( 3, pyname.get(), args.get(), kwargs.get() ) );
    if( !callargs )
        return 0;
    PyObjectPtr newclass( PyObject_CallObject( reinterpret_cast<PyObject*>( &PyType_Type ), callargs.get() ) );
    if( !newclass )
        return 0;
    // TODO make these enums more flexible
    reinterpret_cast<PyTypeObject*>( newclass.get() )->tp_new = 0;
    return newclass.release();
}


static int
add_enum( PyObject* cls, const char* name, long value )
{
    PyObjectPtr pyint( PyLong_FromLong( value ) );
    if( !pyint )
        return -1;
    return PyObject_SetAttrString( cls, name, pyint.get() );
}


#if PY_MAJOR_VERSION >= 3

#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))

static int fontext_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int fontext_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    return 0;
}


static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "fontext",
        NULL,
        sizeof(struct module_state),
        fontext_methods,
        NULL,
        fontext_traverse,
        fontext_clear,
        NULL
};

#else

#define GETSTATE(m) (&_state)
static struct module_state _state;

#endif
MOD_INIT_FUNC(fontext)
{
    if( PyType_Ready( &Font_Type ) )
        INITERROR;

#if PY_MAJOR_VERSION >= 3
    PyObject *mod = PyModule_Create(&moduledef);
#else
    PyObject* mod = Py_InitModule( "fontext", fontext_methods );
#endif
    if( !mod )
        INITERROR;
    PyObject* PyFontStyle = new_enum_class( "FontStyle" );
    if( !PyFontStyle )
        INITERROR;
    PyObject* PyFontCaps = new_enum_class( "FontCaps" );
    if( !PyFontCaps )
        INITERROR;
    PyObject* PyFontStretch = new_enum_class( "FontStretch" );
    if( !PyFontCaps )
        INITERROR;

#define AddEnum( cls, e ) \
    do { \
        if( add_enum( cls, #e, e ) < 0 ) \
            INITERROR; \
    } while( 0 )

    AddEnum( PyFontStyle, Normal );
    AddEnum( PyFontStyle, Italic );
    AddEnum( PyFontStyle, Oblique );

    AddEnum( PyFontCaps, MixedCase );
    AddEnum( PyFontCaps, AllUppercase );
    AddEnum( PyFontCaps, AllLowercase );
    AddEnum( PyFontCaps, SmallCaps );
    AddEnum( PyFontCaps, Capitalize );

    AddEnum( PyFontStretch, UltraCondensed );
    AddEnum( PyFontStretch, ExtraCondensed );
    AddEnum( PyFontStretch, Condensed );
    AddEnum( PyFontStretch, SemiCondensed );
    AddEnum( PyFontStretch, Unstretched );
    AddEnum( PyFontStretch, SemiExpanded );
    AddEnum( PyFontStretch, Expanded );
    AddEnum( PyFontStretch, ExtraExpanded );
    AddEnum( PyFontStretch, UltraExpanded );

    Py_INCREF( ( PyObject* )( &Font_Type ) );
    PyModule_AddObject( mod, "Font", ( PyObject* )( &Font_Type ) );
    PyModule_AddObject( mod, "FontStyle", PyFontStyle );
    PyModule_AddObject( mod, "FontCaps", PyFontCaps );
    PyModule_AddObject( mod, "FontStretch", PyFontStretch );

#if PY_MAJOR_VERSION >= 3
    return mod;
#endif
}
