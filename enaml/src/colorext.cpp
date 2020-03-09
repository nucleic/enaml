/*-----------------------------------------------------------------------------
| Copyright (c) 2013-2018, Nucleic Development Team.
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

// POD struct - all member fields are considered private
struct Color
{
	PyObject_HEAD
    PyObject* tkdata;   // Toolkit specific color representation.
    uint32_t argb;      // Stored using Qt's #AARRGGBB byte order.

	static PyType_Spec TypeObject_Spec;

    static PyTypeObject* TypeObject;

	static bool Ready();

};


namespace
{

PyObject*
Color_new( PyTypeObject* type, PyObject* args, PyObject* kwargs )
{
    int32_t r = -1;
    int32_t g = -1;
    int32_t b = -1;
    int32_t a = 255;
    static char* kwlist[] = { "red", "green", "blue", "alpha", 0 };
    if( !PyArg_ParseTupleAndKeywords( args, kwargs, "|iiii", kwlist, &r, &g, &b, &a ) )
        return 0;
    cppy::ptr colorptr( PyType_GenericNew( type, args, kwargs ) );
    if( !colorptr )
        return 0;
    Color* color = reinterpret_cast<Color*>( colorptr.get() );
    if( r < 0 || g < 0 || b < 0 || a < 0 )
        color->argb = 0;
    else
    {
        r = std::max( 0, std::min( r, 255 ) );
        g = std::max( 0, std::min( g, 255 ) );
        b = std::max( 0, std::min( b, 255 ) );
        a = std::max( 0, std::min( a, 255 ) );
        color->argb = static_cast<uint32_t>( ( a << 24 ) | ( r << 16 ) | ( g << 8 ) | b );
    }
    return colorptr.release();
}


void
Color_dealloc( Color* self )
{
    Py_CLEAR( self->tkdata );
    Py_TYPE(self)->tp_free( reinterpret_cast<PyObject*>( self ) );
}


PyObject*
Color_repr( Color* self )
{
    uint32_t a = ( self->argb >> 24 ) & 255;
    uint32_t r = ( self->argb >> 16 ) & 255;
    uint32_t g = ( self->argb >> 8 ) & 255;
    uint32_t b = self->argb & 255;
    std::ostringstream ostr;
    ostr << "Color(red=" << r << ", green=" << g << ", blue=" << b << ", alpha=" << a << ")";
    return PyUnicode_FromString(ostr.str().c_str());
}


PyObject*
Color_get_alpha( Color* self, void* context )
{
    uint32_t a = ( self->argb >> 24 ) & 255;
    return PyLong_FromLong( a );
}


PyObject*
Color_get_red( Color* self, void* context )
{
    uint32_t r = ( self->argb >> 16 ) & 255;
    return PyLong_FromLong( r );
}


PyObject*
Color_get_green( Color* self, void* context )
{
    uint32_t g = ( self->argb >> 8 ) & 255;
    return PyLong_FromLong( g );
}


PyObject*
Color_get_blue( Color* self, void* context )
{
    uint32_t b = self->argb & 255;
    return PyLong_FromLong( b );
}


PyObject*
Color_get_argb( Color* self, void* context )
{
    return PyLong_FromUnsignedLong( self->argb );
}


PyObject*
Color_get_tkdata( Color* self, void* context )
{
    if( !self->tkdata )
        Py_RETURN_NONE;
    Py_INCREF( self->tkdata );
    return self->tkdata;
}


int
Color_set_tkdata( Color* self, PyObject* value, void* context )
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
Color_getset[] = {
    { "alpha", ( getter )Color_get_alpha, 0,
      "Get the alpha value for the color." },
    { "red", ( getter )Color_get_red, 0,
      "Get the red value for the color." },
    { "green", ( getter )Color_get_green, 0,
      "Get the green value for the color." },
    { "blue", ( getter )Color_get_blue, 0,
      "Get the blue value for the color." },
    { "argb", ( getter )Color_get_argb, 0,
      "Get the color as an #AARRGGBB unsigned long." },
    { "_tkdata", ( getter )Color_get_tkdata, ( setter )Color_set_tkdata,
      "Get and set the toolkit specific color representation." },
    { 0 } // sentinel
};


PyObject*
Color__reduce__( Color* self, void* context )
{
    PyObject* obj = reinterpret_cast<PyObject*>( self );
    uint32_t a = ( self->argb >> 24 ) & 0xFF;
    uint32_t r = ( self->argb >> 16 ) & 0xFF;
    uint32_t g = ( self->argb >> 8 ) & 0xFF;
    uint32_t b = self->argb & 0xFF;
    return Py_BuildValue( "O (iiii)", obj->ob_type, r, g, b, a );
}


static PyMethodDef
Color_methods[] = {
    { "__reduce__", ( PyCFunction )Color__reduce__, METH_NOARGS, "" },
    { 0 } // Sentinel
};

static PyType_Slot Color_Type_slots[] = {
    { Py_tp_dealloc, void_cast( Color_dealloc ) },          /* tp_dealloc */
    { Py_tp_repr, void_cast( Color_repr ) },                /* tp_repr */
    { Py_tp_getset, void_cast( Color_getset ) },            /* tp_getset */
    { Py_tp_methods, void_cast( Color_methods ) },          /* tp_methods */
    { Py_tp_new, void_cast( Color_new ) },                  /* tp_new */
    { Py_tp_alloc, void_cast( PyType_GenericAlloc ) },      /* tp_alloc */
    { 0, 0 },
};


}  // namespace


// Initialize static variables (otherwise the compiler eliminates them)
PyTypeObject* Color::TypeObject = NULL;


PyType_Spec Color::TypeObject_Spec = {
	"enaml.colorext.Color",              /* tp_name */
	sizeof( Color ),                     /* tp_basicsize */
	0,                                   /* tp_itemsize */
	Py_TPFLAGS_DEFAULT,                  /* tp_flags */
    Color_Type_slots               /* slots */
};


bool Color::Ready()
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


int
colorext_modexec( PyObject *mod )
{
    if( !Color::Ready() )
    {
        return -1;
    }

    // callableref
    cppy::ptr color( pyobject_cast( Color::TypeObject ) );
	if( PyModule_AddObject( mod, "Color", color.get() ) < 0 )
	{
		return -1;
	}
    color.release();

    return 0;
}


PyMethodDef
colorext_methods[] = {
    { 0 } // Sentinel
};


PyModuleDef_Slot colorext_slots[] = {
    {Py_mod_exec, reinterpret_cast<void*>( colorext_modexec ) },
    {0, NULL}
};


struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "colorext",
        "colorext extension module",
        0,
        colorext_methods,
        colorext_slots,
        NULL,
        NULL,
        NULL
};


}  // namespace


}  // namespace enaml


PyMODINIT_FUNC PyInit_colorext( void )
{
    return PyModuleDef_Init( &enaml::moduledef );
}
