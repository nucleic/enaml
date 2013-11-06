/*-----------------------------------------------------------------------------
| Copyright (c) 2013, Nucleic Development Team.
|
| Distributed under the terms of the Modified BSD License.
|
| The full license is in the file COPYING.txt, distributed with this software.
|----------------------------------------------------------------------------*/
// Get access to the icon defines in Winuser.h
#ifndef OEMRESOURCE
#define OEMRESOURCE
#endif
#include <windows.h>
#include "pythonhelpersex.h"


using namespace PythonHelpers;


// Builtin Icons
static PyObject* Py_OIC_SAMPLE;
static PyObject* Py_OIC_HAND;
static PyObject* Py_OIC_QUES;
static PyObject* Py_OIC_BANG;
static PyObject* Py_OIC_NOTE;
static PyObject* Py_OIC_WINLOGO;
static PyObject* Py_OIC_WARNING;
static PyObject* Py_OIC_ERROR;
static PyObject* Py_OIC_INFORMATION;
#if(WINVER >= 0x0600)
static PyObject* Py_OIC_SHIELD;
#endif


typedef struct {
    PyObject_HEAD;
    UINT value;
} WinEnum;


static PyTypeObject
WinEnum_Type = {
    PyObject_HEAD_INIT( 0 )
    0,                                      /* ob_size */
    "winutil.WinEnum",                      /* tp_name */
    sizeof( WinEnum ),                      /* tp_basicsize */
    0,                                      /* tp_itemsize */
    (destructor)PyObject_Del,               /* tp_dealloc */
    (printfunc)0,                           /* tp_print */
    (getattrfunc)0,                         /* tp_getattr */
    (setattrfunc)0,                         /* tp_setattr */
    (cmpfunc)0,                             /* tp_compare */
    (reprfunc)0,                            /* tp_repr */
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
    0,                                      /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    (descrgetfunc)0,                        /* tp_descr_get */
    (descrsetfunc)0,                        /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)0,                            /* tp_init */
    (allocfunc)PyType_GenericAlloc,         /* tp_alloc */
    (newfunc)0,                             /* tp_new */
    (freefunc)0,                            /* tp_free */
    (inquiry)0,                             /* tp_is_gc */
    0,                                      /* tp_bases */
    0,                                      /* tp_mro */
    0,                                      /* tp_cache */
    0,                                      /* tp_subclasses */
    0,                                      /* tp_weaklist */
    (destructor)0                           /* tp_del */
};


static PyObject*
PyString_FromHICON( HICON icon, int& width_out, int& height_out )
{
    HDC screen_device = GetDC( 0 );
    HDC hdc = CreateCompatibleDC( screen_device );
    ReleaseDC( 0, screen_device );

    ICONINFO icon_info;
    GetIconInfo( icon, &icon_info );
    int w = icon_info.xHotspot * 2;
    int h = icon_info.yHotspot * 2;

    BITMAPINFO bmi;
    memset( &bmi, 0, sizeof( bmi ) );
    bmi.bmiHeader.biSize        = sizeof( BITMAPINFOHEADER );
    bmi.bmiHeader.biWidth       = w;
    bmi.bmiHeader.biHeight      = -h;  // flip the origin to top-left
    bmi.bmiHeader.biPlanes      = 1;
    bmi.bmiHeader.biBitCount    = 32;
    bmi.bmiHeader.biCompression = BI_RGB;
    VOID* bits;

    HBITMAP win_bitmap = CreateDIBSection( hdc, &bmi, DIB_RGB_COLORS, &bits, 0, 0 );
    HGDIOBJ old_hdc = ( HBITMAP )SelectObject( hdc, win_bitmap );
    DrawIconEx( hdc, 0, 0, icon, w, h, 0, 0, DI_NORMAL );

    PyObject* result = PyString_FromStringAndSize( ( const char* )bits, w * h * 4 );

    // dispose resources created by GetIconInfo
    DeleteObject( icon_info.hbmMask );
    DeleteObject( icon_info.hbmColor );

    SelectObject( hdc, old_hdc ); // restore state
    DeleteObject( win_bitmap );
    DeleteDC( hdc );

    width_out = w;
    height_out = h;
    return result;
}


static PyObject*
load_icon( PyObject* mod, PyObject* args )
{
    WinEnum* win_enum;
    if( !PyArg_ParseTuple( args, "O!", &WinEnum_Type, &win_enum ) )
        return 0;
    HANDLE hicon = LoadImage(
        0, MAKEINTRESOURCE( win_enum->value ), IMAGE_ICON, 0, 0, LR_SHARED
    );
    if( !hicon )
        return Py_BuildValue( "(s, (i, i))", "", -1, -1 );
    int width, height;
    PyObjectPtr result( PyString_FromHICON( ( HICON )hicon, width, height ) );
    if( !result )
        return 0;
    return Py_BuildValue( "(O, (i, i))", result.get(), width, height );
}


static PyMethodDef
winutil_methods[] = {
    { "load_icon", ( PyCFunction )load_icon, METH_VARARGS,
      "Load a builtin Windows icon" },
    { 0 } // Sentinel
};


#define MAKE_ENUM( TOKEN, VALUE ) \
    do { \
        TOKEN = PyType_GenericNew( &WinEnum_Type, 0, 0 ); \
        if( !TOKEN ) \
            return; \
        reinterpret_cast<WinEnum*>( TOKEN )->value = VALUE; \
        if( PyModule_AddObject( mod, #VALUE, newref( TOKEN ) ) < 0 ) \
            return; \
    } while( 0 )


PyMODINIT_FUNC
initwinutil( void )
{
    PyObject* mod = Py_InitModule( "winutil", winutil_methods );
    if( !mod )
        return;
    if( PyType_Ready( &WinEnum_Type ) )
        return;
    MAKE_ENUM( Py_OIC_SAMPLE, OIC_SAMPLE );
    MAKE_ENUM( Py_OIC_HAND, OIC_HAND );
    MAKE_ENUM( Py_OIC_QUES, OIC_QUES );
    MAKE_ENUM( Py_OIC_BANG, OIC_BANG );
    MAKE_ENUM( Py_OIC_NOTE, OIC_NOTE );
    MAKE_ENUM( Py_OIC_WINLOGO, OIC_WINLOGO );
    MAKE_ENUM( Py_OIC_WARNING, OIC_WARNING );
    MAKE_ENUM( Py_OIC_ERROR, OIC_ERROR );
    MAKE_ENUM( Py_OIC_INFORMATION, OIC_INFORMATION );
    #if(WINVER >= 0x0600)
    MAKE_ENUM( Py_OIC_SHIELD, OIC_SHIELD );
    #endif
}
