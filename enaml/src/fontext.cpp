/*-----------------------------------------------------------------------------
| Copyright (c) 2013-2019, Nucleic Development Team.
|
| Distributed under the terms of the Modified BSD License.
|
| The full license is in the file LICENSE, distributed with this software.
|----------------------------------------------------------------------------*/
#include <algorithm>
#include <iostream>
#include <sstream>
#include <cppy/cppy.h>
#include "platstdint.h"

#ifdef __clang__
#pragma clang diagnostic ignored "-Wdeprecated-writable-strings"
#endif

#ifdef __GNUC__
#pragma GCC diagnostic ignored "-Wwrite-strings"
#endif


namespace enaml
{

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


// POD struct - all member fields are considered private
struct Font
{
	PyObject_HEAD
    PyObject* tkdata;   // Toolkit specific font representation
    PyObject* family;   // Font family name as a string
    int32_t pointsize;
    int32_t weight;
    FontStyle style;
    FontCaps caps;
    FontStretch stretch;

	static PyType_Spec TypeObject_Spec;

    static PyTypeObject* TypeObject;

	static bool Ready();

};


namespace
{


PyObject*
Font_new( PyTypeObject* type, PyObject* args, PyObject* kwargs )
{
    PyObject* family;
    int32_t pointsize = -1;
    int32_t weight = -1;
    FontStyle style = Normal;
    FontCaps caps = MixedCase;
    FontStretch stretch = Unstretched;
    static char* kwlist[] = { "family", "size", "weight", "style", "caps", "stretch", 0 };
    if( !PyArg_ParseTupleAndKeywords(
        args, kwargs, "U|iiiii", kwlist, &family, &pointsize, &weight, &style, &caps, &stretch ) )
        return 0;
    cppy::ptr fontptr( PyType_GenericNew( type, args, kwargs ) );
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


void
Font_dealloc( Font* self )
{
    Py_CLEAR( self->tkdata );
    Py_CLEAR( self->family );
    Py_TYPE( self )->tp_free( pyobject_cast( self ) );
}


PyObject*
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
    ostr << "Font(family=\"" << PyUnicode_AsUTF8( self->family ) << "\", ";
    ostr << "pointsize=" << self->pointsize << ", ";
    ostr << "weight=" << self->weight << ", ";
    ostr << style_reprs[self->style] << caps_reprs[self->caps] << stretch_reprs[self->stretch];
    return PyUnicode_FromString( ostr.str().c_str() );
};


PyObject*
Font_get_family( Font* self, void* context )
{
    return cppy::incref( self->family );
}


PyObject*
Font_get_pointsize( Font* self, void* context )
{
    return PyLong_FromLong( self->pointsize );
}


PyObject*
Font_get_weight( Font* self, void* context )
{
    return PyLong_FromLong( self->weight );
}


PyObject*
Font_get_style( Font* self, void* context )
{
    return PyLong_FromLong( static_cast<long>( self->style ) );
}


PyObject*
Font_get_caps( Font* self, void* context )
{
    return PyLong_FromLong( static_cast<long>( self->caps ) );
}

PyObject*
Font_get_stretch( Font* self, void* context )
{
    return PyLong_FromLong( static_cast<long>( self->stretch ) );
}


PyObject*
Font_get_tkdata( Font* self, void* context )
{
    if( !self->tkdata )
        Py_RETURN_NONE;
    return cppy::incref( self->tkdata );
}


int
Font_set_tkdata( Font* self, PyObject* value, void* context )
{
    // don't let users do something silly which would require GC
    if( pyobject_cast( self ) == value )
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


static PyType_Slot Nonlocals_Type_slots[] = {
    { Py_tp_dealloc, void_cast( Font_dealloc ) },        /* tp_dealloc */
    { Py_tp_repr, void_cast( Font_repr ) },              /* tp_repr */
    { Py_tp_getset, void_cast( Font_getset ) },          /* tp_getset */
    { Py_tp_new, void_cast( Font_new ) },                /* tp_new */
    { Py_tp_alloc, void_cast( PyType_GenericAlloc ) },   /* tp_alloc */
    { 0, 0 },
};


}  // namespace


// Initialize static variables (otherwise the compiler eliminates them)
PyTypeObject* Font::TypeObject = NULL;


PyType_Spec Font::TypeObject_Spec = {
	"enaml.fontext.Font",              /* tp_name */
	sizeof( Font ),               /* tp_basicsize */
	0,                                 /* tp_itemsize */
	Py_TPFLAGS_DEFAULT,                /* tp_flags */
    Nonlocals_Type_slots               /* slots */
};


bool Font::Ready()
{
    // The reference will be handled by the module to which we will add the type
	TypeObject = pytype_cast( PyType_FromSpec( &TypeObject_Spec ) );
    if( !TypeObject )
    {
        return false;
    }
    return true;
}


// Module definition
namespace
{


PyObject*
new_enum_class( const char* name )
{
    cppy::ptr pyname( PyUnicode_FromString( name ) );
    if( !pyname )
        return 0;
    cppy::ptr args( PyTuple_New( 0 ) );
    if( !args )
        return 0;
    cppy::ptr kwargs( PyDict_New() );
    if( !kwargs )
        return 0;
    cppy::ptr modname( PyUnicode_FromString( "fontext" ) );
    if( !modname )
        return 0;
    if( PyDict_SetItemString( kwargs.get(), "__module__", modname.get() ) != 0 )
        return 0;
    cppy::ptr callargs( PyTuple_Pack( 3, pyname.get(), args.get(), kwargs.get() ) );
    if( !callargs )
        return 0;
    cppy::ptr newclass( PyObject_CallObject( pyobject_cast( &PyType_Type ), callargs.get() ) );
    if( !newclass )
        return 0;
    // TODO make these enums more flexible
    pytype_cast( newclass.get() )->tp_new = 0;
    return newclass.release();
}


int
add_enum( PyObject* cls, const char* name, long value )
{
    cppy::ptr pyint( PyLong_FromLong( value ) );
    if( !pyint )
    {
        return -1;
    }
    return PyObject_SetAttrString( cls, name, pyint.get() );
}


int
fontext_modexec( PyObject *mod )
{
    if( !Font::Ready() )
    {
        return -1;
    }
    cppy::ptr PyFontStyle( new_enum_class( "FontStyle" ) );
    if( !PyFontStyle )
    {
        return -1;
    }
    cppy::ptr PyFontCaps( new_enum_class( "FontCaps" ) );
    if( !PyFontCaps )
    {
        return -1;
    }
    cppy::ptr PyFontStretch( new_enum_class( "FontStretch" ) );
    if( !PyFontCaps )
    {
        return -1;
    }

#define AddEnum( cls, e ) \
    do { \
        if( add_enum( cls.get(), #e, e ) < 0 ) \
            return -1; \
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


    // Font
    cppy::ptr font( pyobject_cast( Font::TypeObject ) );
	if( PyModule_AddObject( mod, "Font", font.get() ) < 0 )
	{
		return -1;
	}
    font.release();

    if( PyModule_AddObject( mod, "FontStyle", PyFontStyle.get() ) < 0 )
    {
        return -1;
    }
    PyFontStyle.release();

    if( PyModule_AddObject( mod, "FontCaps", PyFontCaps.get() ) < 0 )
    {
        return -1;
    }
    PyFontCaps.release();

    if( PyModule_AddObject( mod, "FontStretch", PyFontStretch.get() ) < 0 )
    {
        return -1;
    }
    PyFontStretch.release();

    return 0;
}

static PyMethodDef
fontext_methods[] = {
    { 0 }  // Sentinel
};


PyModuleDef_Slot fontext_slots[] = {
    {Py_mod_exec, reinterpret_cast<void*>( fontext_modexec ) },
    {0, NULL}
};


struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "fontext",
        "fontext extension module",
        0,
        fontext_methods,
        fontext_slots,
        NULL,
        NULL,
        NULL
};

}  // namespace


}  // namespace enaml


PyMODINIT_FUNC PyInit_fontext( void )
{
    return PyModuleDef_Init( &enaml::moduledef );
}
