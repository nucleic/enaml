/*-----------------------------------------------------------------------------
| Copyright (c) 2013, Nucleic Development Team.
|
| Distributed under the terms of the Modified BSD License.
|
| The full license is in the file COPYING.txt, distributed with this software.
|----------------------------------------------------------------------------*/
#include "inttypes.h"
#include <iostream>
#include <sstream>
#include "pythonhelpers.h"

using namespace PythonHelpers;


// The fact that this needs to be an extension module is depressing.
typedef struct {
    PyObject_HEAD
    uint32_t color;  // Store using Qt's #AARRGGBB byte order.
} Color;


static PyObject*
Color_new( PyTypeObject* type, PyObject* args, PyObject* kwargs )
{
    uint32_t r = 0;
    uint32_t g = 0;
    uint32_t b = 0;
    uint32_t a = 255;
    static char* kwlist[] = { "red", "green", "blue", "alpha", 0 };
    if( !PyArg_ParseTupleAndKeywords( args, kwargs, "|kkkk", kwlist, &r, &g, &b, &a ) )
        return 0;
    PyObjectPtr colorptr( PyType_GenericNew( type, args, kwargs ) );
    if( !colorptr )
        return 0;
    Color* color = reinterpret_cast<Color*>( colorptr.get() );
    r = r > 255 ? 255 : r;
    g = g > 255 ? 255 : g;
    b = b > 255 ? 255 : b;
    a = a > 255 ? 255 : a;
    color->color = (a << 24) | (r << 16) | (g << 8) | b;
    return colorptr.release();
}


static PyObject*
Color_repr( Color* self )
{
    uint32_t a = ( self->color >> 24 ) & 255;
    uint32_t r = ( self->color >> 16 ) & 255;
    uint32_t g = ( self->color >> 8 ) & 255;
    uint32_t b = self->color & 255;
    std::ostringstream ostr;
    ostr << "Color(red=" << r << ", green=" << g << ", blue=" << b << ", alpha=" << a << ")";
    return PyString_FromString(ostr.str().c_str());
}


static PyObject*
Color_get_alpha( Color* self, void* context )
{
    uint32_t a = ( self->color >> 24 ) & 255;
    return PyInt_FromLong( a );
}


static PyObject*
Color_get_red( Color* self, void* context )
{
    uint32_t r = ( self->color >> 16 ) & 255;
    return PyInt_FromLong( r );
}


static PyObject*
Color_get_green( Color* self, void* context )
{
    uint32_t g = ( self->color >> 8 ) & 255;
    return PyInt_FromLong( g );
}


static PyObject*
Color_get_blue( Color* self, void* context )
{
    uint32_t b = self->color & 255;
    return PyInt_FromLong( b );
}


static PyObject*
Color_get_color( Color* self, void* context )
{
    return PyLong_FromUnsignedLong( self->color );
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
    { "color", ( getter )Color_get_color, 0,
      "Get the color as an #AARRGGBB unsigned long." },
    { 0 } // sentinel
};


PyTypeObject Color_Type = {
    PyObject_HEAD_INIT( 0 )
    0,                                      /* ob_size */
    "color.Color",                          /* tp_name */
    sizeof( Color ),                        /* tp_basicsize */
    0,                                      /* tp_itemsize */
    (destructor)PyObject_Del,               /* tp_dealloc */
    (printfunc)0,                           /* tp_print */
    (getattrfunc)0,                         /* tp_getattr */
    (setattrfunc)0,                         /* tp_setattr */
    (cmpfunc)0,                             /* tp_compare */
    (reprfunc)Color_repr,                   /* tp_repr */
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
    Color_getset,                           /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    (descrgetfunc)0,                        /* tp_descr_get */
    (descrsetfunc)0,                        /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)0,                            /* tp_init */
    (allocfunc)PyType_GenericAlloc,         /* tp_alloc */
    (newfunc)Color_new,                     /* tp_new */
    (freefunc)0,                            /* tp_free */
    (inquiry)0,                             /* tp_is_gc */
    0,                                      /* tp_bases */
    0,                                      /* tp_mro */
    0,                                      /* tp_cache */
    0,                                      /* tp_subclasses */
    0,                                      /* tp_weaklist */
    (destructor)0                           /* tp_del */
};


static PyMethodDef
color_methods[] = {
    { 0 } // Sentinel
};


PyMODINIT_FUNC
initcolor( void )
{
    PyObject* mod = Py_InitModule( "color", color_methods );
    if( !mod )
        return;

    if( PyType_Ready( &Color_Type ) )
        return;

    Py_INCREF( ( PyObject* )( &Color_Type ) );
    PyModule_AddObject( mod, "Color", ( PyObject* )( &Color_Type ) );
}
