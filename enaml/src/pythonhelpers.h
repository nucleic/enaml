/*-----------------------------------------------------------------------------
| Copyright (c) 2013, Nucleic Development Team.
|
| Distributed under the terms of the Modified BSD License.
|
| The full license is in the file COPYING.txt, distributed with this software.
|----------------------------------------------------------------------------*/
#pragma once
#include <Python.h>
#include <structmember.h>


// XXX Use Atom's pythonhelpers header

#ifndef Py_RETURN_NOTIMPLEMENTED
#define Py_RETURN_NOTIMPLEMENTED \
    return Py_INCREF(Py_NotImplemented), Py_NotImplemented
#endif


namespace PythonHelpers
{

/*-----------------------------------------------------------------------------
| Exception Handling
|----------------------------------------------------------------------------*/
PyObject*
py_type_fail( const char* message )
{
    PyErr_SetString( PyExc_TypeError, message );
    return 0;
}


PyObject*
py_expected_type_fail( PyObject* pyobj, const char* expected_type )
{
    PyErr_Format(
        PyExc_TypeError,
        "Expected object of type `%s`. Got object of type `%s` instead.",
        expected_type, pyobj->ob_type->tp_name
    );
    return 0;
}


PyObject*
py_attr_fail( const char* message )
{
    PyErr_SetString( PyExc_AttributeError, message );
    return 0;
}


PyObject*
py_no_attr_fail( PyObject* pyobj, const char* attr )
{
    PyErr_Format(
        PyExc_AttributeError,
        "'%s' object has no attribute '%s'",
        pyobj->ob_type->tp_name, attr
    );
    return 0;
}


/*-----------------------------------------------------------------------------
| Object Ptr
|----------------------------------------------------------------------------*/
class PyObjectPtr {

public:

    PyObjectPtr() : m_pyobj( 0 ) { }

    PyObjectPtr( const PyObjectPtr& objptr ) : m_pyobj( objptr.m_pyobj )
    {
        incref();
    }

    PyObjectPtr( PyObject* pyobj, bool takeref=false ) : m_pyobj( pyobj )
    {
        if( takeref )
            incref();
    }

    ~PyObjectPtr()
    {
        release( true );
    }

    PyObject* get() const
    {
        return m_pyobj;
    }

    PyObject* release( bool giveref=false )
    {
        PyObject* pyobj = m_pyobj;
        m_pyobj = 0;
        if( giveref )
            Py_XDECREF( pyobj );
        return pyobj;
    }

    void incref() const
    {
        Py_XINCREF( m_pyobj );
    }

    void decref() const
    {
        Py_XDECREF( m_pyobj );
    }

    size_t refcount() const
    {
        if( m_pyobj )
            return m_pyobj->ob_refcnt;
        return 0;
    }

    bool is_None() const
    {
        return m_pyobj == Py_None;
    }

    bool is_True() const
    {
        return m_pyobj == Py_True;
    }

    bool is_False() const
    {
        return m_pyobj == Py_False;
    }

    bool load_dict( PyObjectPtr& out, bool forcecreate=false )
    {
        PyObject** dict = _PyObject_GetDictPtr( m_pyobj );
        if( !dict )
            return false;
        if( forcecreate && !*dict )
            *dict = PyDict_New();
        out = PyObjectPtr( *dict, true );
        return true;
    }

    int richcompare( PyObjectPtr& other, int opid, bool clear_err=true )
    {
        int r = PyObject_RichCompareBool( m_pyobj, other.m_pyobj, opid );
        if( r == 1 )
            return true;
        if( r == 0 )
            return false;
        if( clear_err && PyErr_Occurred() )
            PyErr_Clear();
        return false;
    }

    bool has_attr( PyObjectPtr& attr )
    {
        return PyObject_HasAttr( m_pyobj, attr.get() );
    }

    bool has_attr( const char* attr )
    {
        return PyObject_HasAttrString( m_pyobj, attr );
    }

    bool has_attr( std::string& attr )
    {
        return has_attr( attr.c_str() );
    }

    PyObjectPtr get_attr( PyObjectPtr& attr )
    {
        return PyObjectPtr( PyObject_GetAttr( m_pyobj, attr.get() ) );
    }

    PyObjectPtr get_attr( const char* attr )
    {
        return PyObjectPtr( PyObject_GetAttrString( m_pyobj, attr ) );
    }

    PyObjectPtr get_attr( std::string& attr )
    {
        return get_attr( attr.c_str() );
    }

    PyObjectPtr operator()( PyObjectPtr& args ) const
    {
        return PyObjectPtr( PyObject_Call( m_pyobj, args.get(), 0 ) );
    }

    PyObjectPtr operator()( PyObjectPtr& args, PyObjectPtr& kwargs ) const
    {
        return PyObjectPtr( PyObject_Call( m_pyobj, args.get(), kwargs.get() ) );
    }

    operator void*() const
    {
        return static_cast<void*>( m_pyobj );
    }

    PyObjectPtr& operator=( const PyObjectPtr& rhs )
    {
        PyObject* old = m_pyobj;
        m_pyobj = rhs.m_pyobj;
        Py_XINCREF( m_pyobj );
        Py_XDECREF( old );
        return *this;
    }

protected:

    PyObject* m_pyobj;

};


/*-----------------------------------------------------------------------------
| Tuple Ptr
|----------------------------------------------------------------------------*/
class PyTuplePtr : public PyObjectPtr {

public:

    PyTuplePtr() : PyObjectPtr() { }

    PyTuplePtr( const PyObjectPtr& objptr ) : PyObjectPtr( objptr ) { }

    PyTuplePtr( PyObject* pytuple, bool takeref=false ) :
        PyObjectPtr( pytuple, takeref ) { }

    bool check()
    {
        return PyTuple_Check( m_pyobj );
    }

    bool check_exact()
    {
        return PyTuple_CheckExact( m_pyobj );
    }

    Py_ssize_t size() const
    {
        return PyTuple_GET_SIZE( m_pyobj );
    }

    PyObjectPtr get_item( Py_ssize_t index ) const
    {
        return PyObjectPtr( PyTuple_GET_ITEM( m_pyobj, index ), true );
    }

    void set_item( Py_ssize_t index, PyObjectPtr& item )
    {
        PyObject* new_item = item.get();
        PyObject* old_item = PyTuple_GET_ITEM( m_pyobj, index );
        PyTuple_SET_ITEM( m_pyobj, index, new_item );
        Py_XINCREF( new_item );
        Py_XDECREF( old_item );
    }

};


/*-----------------------------------------------------------------------------
| List Ptr
|----------------------------------------------------------------------------*/
class PyListPtr : public PyObjectPtr {

public:

    PyListPtr() : PyObjectPtr() { }

    PyListPtr( const PyObjectPtr& objptr ) : PyObjectPtr( objptr ) { }

    PyListPtr( PyObject* pylist, bool takeref=false ) :
        PyObjectPtr( pylist, takeref ) { }

    bool check()
    {
        return PyList_Check( m_pyobj );
    }

    bool check_exact()
    {
        return PyList_CheckExact( m_pyobj );
    }

    Py_ssize_t size() const
    {
        return PyList_GET_SIZE( m_pyobj );
    }

    PyObjectPtr get_item( Py_ssize_t index ) const
    {
        return PyObjectPtr( PyList_GET_ITEM( m_pyobj, index ), true );
    }

    void set_item( Py_ssize_t index, PyObjectPtr& item )
    {
        PyObject* new_item = item.get();
        PyObject* old_item = PyList_GET_ITEM( m_pyobj, index );
        PyList_SET_ITEM( m_pyobj, index, new_item );
        Py_XINCREF( new_item );
        Py_XDECREF( old_item );
    }

    bool del_item( Py_ssize_t index ) const
    {
        if( PySequence_DelItem( m_pyobj, index ) == -1 )
            return false;
        return true;
    }

    bool append( PyObjectPtr& pyobj ) const
    {
        if( PyList_Append( m_pyobj, pyobj.get() ) == 0 )
            return true;
        return false;
    }

    Py_ssize_t index( PyObjectPtr& item ) const
    {
        Py_ssize_t maxidx = size();
        for( Py_ssize_t idx = 0; idx < maxidx; idx++ )
        {
            PyObjectPtr other( get_item( idx ) );
            if( item.richcompare( other, Py_EQ ) )
                return idx;
        }
        return -1;
    }

};


/*-----------------------------------------------------------------------------
| Dict Ptr
|----------------------------------------------------------------------------*/
class PyDictPtr : public PyObjectPtr {

public:

    PyDictPtr() : PyObjectPtr() { }

    PyDictPtr( const PyObjectPtr& objptr ) : PyObjectPtr( objptr ) { }

    PyDictPtr( PyObject* pydict, bool takeref=false ) :
        PyObjectPtr( pydict, takeref ) { }

    bool check()
    {
        return PyDict_Check( m_pyobj );
    }

    bool check_exact()
    {
        return PyDict_CheckExact( m_pyobj );
    }

    Py_ssize_t size() const
    {
        return PyDict_Size( m_pyobj );
    }

    PyObjectPtr get_item( PyObjectPtr& key ) const
    {
        return PyObjectPtr( PyDict_GetItem( m_pyobj, key.get() ), true );
    }

    PyObjectPtr get_item( const char* key ) const
    {
        return PyObjectPtr( PyDict_GetItemString( m_pyobj, key ), true );
    }

    PyObjectPtr get_item( std::string& key ) const
    {
        return get_item( key.c_str() );
    }

    bool set_item( PyObjectPtr& key, PyObjectPtr& value ) const
    {
        if( PyDict_SetItem( m_pyobj, key.get(), value.get() ) == 0 )
            return true;
        return false;
    }

    bool set_item( const char* key, PyObjectPtr& value ) const
    {
        if( PyDict_SetItemString( m_pyobj, key, value.get() ) == 0 )
            return true;
        return false;
    }

    bool set_item( std::string& key, PyObjectPtr& value ) const
    {
        return set_item( key.c_str(), value );
    }

    bool del_item( PyObjectPtr& key ) const
    {
        if( PyDict_DelItem( m_pyobj, key.get() ) == 0 )
            return true;
        return false;
    }

    bool del_item( const char* key ) const
    {
        if( PyDict_DelItemString( m_pyobj, key ) == 0 )
            return true;
        return false;
    }

    bool del_item( std::string& key ) const
    {
        return del_item( key.c_str() );
    }

};


/*-----------------------------------------------------------------------------
| Method Ptr
|----------------------------------------------------------------------------*/
class PyMethodPtr : public PyObjectPtr {

public:

    PyMethodPtr() : PyObjectPtr() { }

    PyMethodPtr( const PyObjectPtr& objptr ) : PyObjectPtr( objptr ) { }

    PyMethodPtr( PyObject* pymethod, bool takeref=false ) :
        PyObjectPtr( pymethod, takeref ) { }

    bool check()
    {
        return PyMethod_Check( m_pyobj );
    }

    PyObjectPtr get_self() const
    {
        return PyObjectPtr( PyMethod_GET_SELF( m_pyobj ), true );
    }

    PyObjectPtr get_function() const
    {
        return PyObjectPtr( PyMethod_GET_FUNCTION( m_pyobj ), true );
    }

    PyObjectPtr get_class() const
    {
        return PyObjectPtr( PyMethod_GET_CLASS( m_pyobj ), true );
    }

};


/*-----------------------------------------------------------------------------
| Weakref Ptr
|----------------------------------------------------------------------------*/
class PyWeakrefPtr : public PyObjectPtr {

public:

    PyWeakrefPtr() : PyObjectPtr() { }

    PyWeakrefPtr( const PyObjectPtr& objptr ) : PyObjectPtr( objptr ) { }

    PyWeakrefPtr( PyObject* pyweakref, bool takeref=true ) :
        PyObjectPtr( pyweakref, takeref ) { }

    bool check()
    {
        return PyWeakref_CheckRef( m_pyobj );
    }

    bool check_exact()
    {
        return PyWeakref_CheckRefExact( m_pyobj );
    }

    PyObjectPtr get_object() const
    {
        return PyObjectPtr( PyWeakref_GET_OBJECT( m_pyobj ), true );
    }

};

} // namespace PythonHelpers

