/*-----------------------------------------------------------------------------
| Copyright (c) 2013-2019, Nucleic Development Team.
|
| Distributed under the terms of the Modified BSD License.
|
| The full license is in the file LICENSE, distributed with this software.
|----------------------------------------------------------------------------*/
// Get access to the icon defines in Winuser.h
#ifndef OEMRESOURCE
#define OEMRESOURCE
#endif
#include <windows.h>
#include <cppy/cppy.h>


namespace enaml
{

// POD struct - all member fields are considered private
struct WinEnum
{
	PyObject_HEAD;
    UINT value;

	static PyType_Spec TypeObject_Spec;

    static PyTypeObject* TypeObject;

	static bool Ready();

};

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

namespace
{

static PyType_Slot WinEnum_Type_slots[] = {
    { Py_tp_dealloc, void_cast( PyObject_Del ) },          /* tp_dealloc */
    { Py_tp_alloc, void_cast( PyType_GenericAlloc ) },     /* tp_alloc */
    { 0, 0 },
};


}  // namespace


// Initialize static variables (otherwise the compiler eliminates them)
PyTypeObject* WinEnum::TypeObject = NULL;


PyType_Spec WinEnum::TypeObject_Spec = {
	"enaml.winutil.WinEnum",              /* tp_name */
	sizeof( WinEnum ),                     /* tp_basicsize */
	0,                                          /* tp_itemsize */
	Py_TPFLAGS_DEFAULT,                         /* tp_flags */
    WinEnum_Type_slots                           /* slots */
};


bool WinEnum::Ready()
{
    // The reference will be handled by the module to which we will add the type
	TypeObject = pytype_cast( PyType_FromSpec( &TypeObject_Spec ) );
    if( !TypeObject )
    {
        return false;
    }
    return true;
}

namespace
{

PyObject*
PyBytes_FromHICON( HICON icon, int& width_out, int& height_out )
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

    PyObject* result = PyBytes_FromStringAndSize( ( const char* )bits, w * h * 4 );

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


PyObject*
load_icon( PyObject* mod, PyObject* args )
{
    WinEnum* win_enum;
    if( !PyArg_ParseTuple( args, "O!", WinEnum::TypeObject, &win_enum ) )
        return 0;
    HANDLE hicon = LoadImage(
        0, MAKEINTRESOURCE( win_enum->value ), IMAGE_ICON, 0, 0, LR_SHARED
    );
    if( !hicon )
        return Py_BuildValue( "(s, (i, i))", "", -1, -1 );
    int width, height;
    cppy::ptr result( PyBytes_FromHICON( ( HICON )hicon, width, height ) );
    if( !result )
        return 0;
    return Py_BuildValue( "(O, (i, i))", result.get(), width, height );
}


int
winutil_modexec( PyObject *mod )
{

#define MAKE_ENUM( TOKEN, VALUE ) \
    do { \
        TOKEN = PyType_GenericNew( WinEnum::TypeObject, 0, 0 ); \
        if( !TOKEN ) \
            return NULL; \
        reinterpret_cast<WinEnum*>( TOKEN )->value = VALUE; \
        if( PyModule_AddObject( mod, #VALUE, cppy::incref( TOKEN ) ) < 0 ) \
            return NULL; \
    } while( 0 )

    if( !WinEnum::Ready() )
    {
        return -1;
    }
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

    return 0;
}

static PyMethodDef
winutil_methods[] = {
    { "load_icon", ( PyCFunction )load_icon, METH_VARARGS,
      "Load a builtin Windows icon" },
    { 0 } // Sentinel
};


PyModuleDef_Slot winutil_slots[] = {
    {Py_mod_exec, reinterpret_cast<void*>( winutil_modexec ) },
    {0, NULL}
};


struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "winutil",
        "winutil extension module",
        0,
        winutil_methods,
        winutil_slots,
        NULL,
        NULL,
        NULL
};


}  // namespace


}  // namespace enaml


PyMODINIT_FUNC PyInit_winutil( void )
{
    return PyModuleDef_Init( &enaml::moduledef );
}
