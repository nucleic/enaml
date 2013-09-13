/*-----------------------------------------------------------------------------
| Copyright (c) 2013, Nucleic Development Team.
|
| Distributed under the terms of the Modified BSD License.
|
| The full license is in the file COPYING.txt, distributed with this software.
|----------------------------------------------------------------------------*/
#include "pythonhelpersex"

using namespace PythonHelpers;


// Static classes assigned during startup
static PyObject* Declarative;
static PyObject* DeclarativeNode;
static PyObject* EnamlDefMeta;
static PyObject* EnamlDefNode;
static PyObject* TemplateNode;
static PyObject* TemplateInstNode;

// Static utils assigned during startup
static PyObject* sortedmap;
static PyObject* empty_tuple;

// Statically attribute name strings
static PyObject* copy_attr;
static PyObject* engine_attr;
static PyObject* identifier_attr;
static PyObject* klass_attr;
static PyObject* names_attr;
static PyObject* scope_key_attr;
static PyObject* starname_attr;
static PyObject* store_locals_attr;
static PyObject* super_node_attr;
static PyObject* template_node_attr;
static PyObject* template_scope_str;
static PyObject* dunder_node_attr;


/* internal declarative node builder */
static PyObject*
_make_d_node_impl( PyObject* NodeType, PyObject* args, const char* name )
{
    PyObject* klass;
    PyObject* identifier;
    PyObject* scope_key;
    PyObject* store_locals;
    if( !PyArg_UnpackTuple( args, name, 4, 4,
        &klass, &identifier, &scope_key, &store_locals ) )
        return 0;
    PyObjectPtr node( PyObject_Call( NodeType, empty_tuple, 0 ) );
    if( !node )
        return 0;
    if( !node.setattr( klass_attr, klass ) )
        return 0;
    if( !node.setattr( identifier_attr, identifier ) )
        return 0;
    if( !node.setattr( scope_key_attr, scope_key ) )
        return 0;
    if( !node.setattr( store_locals_attr, store_locals ) )
        return 0;
    PyObjectPtr super_node( PyObject_GetAttr( klass, dunder_node_attr ) );
    if( super_node && super_node.get() != Py_None )
    {
        PyObjectPtr copy_method( super_node.getattr( copy_attr ) );
        if( !copy_method )
            return 0;
        super_node = PyObject_Call( copy_method.get(), empty_tuple, 0 );
        if( !super_node )
            return 0;
        if( !node.setattr( super_node_attr, super_node.get() ) )
            return 0;
        PyObjectPtr engine( super_node.getattr( engine_attr ) );
        if( !engine )
            return 0;
        if( !node.setattr( engine_attr, engine.get() ) )
            return 0;
    }
    else if( PyErr_Occurred() )
    {
        if( PyErr_ExceptionMatches( PyExc_AttributeError ) )
            PyErr_Clear();
        else
            return 0;
    }
    return node.release();
}


/* Create a DeclarativeNode for the given class.

Parameters
----------
klass : type
    The resolved declarative class for the node.

identifier : str
    The local string identifier to associate with instances.

scope_key : object
    The key for the local scope in the local storage maps.

store_locals : bool
    Whether instances of this node class should store the
    local scope in their storage map.

*/
static PyObject*
make_declarative_node( PyObject* mod, PyObject* args )
{
    return _make_d_node_impl( DeclarativeNode, args, "make_declarative_node" );
}


/* Create a new class using the EnamlDefMeta class.

Parameters
----------
name : str
    The name of the new enamldef.

bases : tuple
    The tuple of base classes.

dct : dict
    The class dictionary.

*/
static PyObject*
make_enamldef( PyObject* mod, PyObject* args )
{
    return PyObject_Call( EnamlDefMeta, args, 0 );
}


/* Create an Enamldef node for the given class.

Parameters
----------
klass : type
    The enamldef declarative class for the node.

identifier : str
    The local string identifier to associate with instances.

scope_key : object
    The key for the local scope in the local storage maps.

store_locals : bool
    Whether instances of this node class should store the
    local scope in their storage map.

*/
static PyObject*
make_enamldef_node( PyObject* mod, PyObject* args )
{
    return _make_d_node_impl( EnamlDefNode, args, "make_enamldef_node" );
}


/* Create a new object() for use as a mapping key.

*/
static PyObject*
make_object( PyObject* mod, PyObject* ignored )
{
    return PyType_GenericNew( &PyBaseOject_Type, 0, 0 );
}


/* Create a new empty TemplateNode.

*/
static PyObject*
make_template_node( PyObject* mod, PyObject* ignored )
{
    return PyObject_Call( TemplateNode, empty_tuple, 0 );
}


/* Create a new TemplateInstNode.

Parameters
----------
template_inst : TemplateInst
    The template instantiation object.

names : tuple
    The identifier names to associate with the instantiation items.
    This may be an empty tuple if there are no such identifiers.

starname : str
    The star name to associate with the extra instantiated items.
    This may be an empty string if there is no such item.

*/
static PyObject*
make_template_inst_node( PyObject* mod, PyObject* args )
{
    PyObject* inst;
    PyObject* names;
    PyObject* starname;
    if( !PyArg_UnpackTuple( args, "make_template_inst_node", 3, 3,
        &inst, &names, &starname ) )
        return 0;
    PyObjectPtr node( PyObject_Call( TemplateInstNode, empty_tuple, 0 ) );
    if( !node )
        return 0;
    PyObjectPtr temp_node( PyObject_GetAttr( inst, template_node_attr ) );
    if( !tnode )
        return 0;
    if( !node.setattr( template_node_attr, temp_node.get() ) )
        return 0;
    if( !node.setattr( names_attr, names ) )
        return 0;
    if( !node.setattr( starname_attr, starname ) )
        return 0;
    Py_RETURN_NONE;
}


/* Create a new template scope map from a scope tuple.

Parameters
----------
node : TemplateNode
    The template node for which to create the scope.

scope_tuple : tuple
    A tuple of alternating key, value pairs representing the
    scope of a template instantiation.

*/
static PyObject*
make_template_scope( PyObject* mod, PyObject* args )
{
    PyObject* node;
    PyObject* tuple;
    if( !PyArg_UnpackTuple( args, "make_template_scope", 2, 2,
        &node, &tuple ) )
        return 0;
    if( !PyTuple_CheckExact( tuple ) )
    {
        PyErr_SetString( PyExc_TypeError, "argument 2 must be a tuple" );
        return 0;
    }
    PyObjectPtr map( PyObject_Call( sortedmap, empty_tuple, 0 ) );
    if( !map )
        return 0;
    Py_ssize_t size = PyTuple_GET_SIZE( tuple );
    for( Py_ssize_t i = 0; i < size; i += 2; )
        PyObject_SetItem( map.get(),
            PyTuple_GET_ITEM( tuple, i ),
            PyTuple_GET_ITEM( tuple, i + 1 )
        );
    PyObjectPtr nodeptr( newref( node ) );
    if( !nodeptr.setattr( template_scope_str, map.get() ) )
        return 0;
    return nodeptr.release();
}


/* Type check the value of an expression.

Parameters
----------
value : object
    The value to type check.

kind : type
    The allowed type of the value.

*/
static PyObject*
type_check_expr( PyObject* mod, PyObject* args )
{
    PyObject* value;
    PyObject* kind;
    if( !PyArg_UnpackTuple( args, "type_check_expr", 2, 2, &value, &kind ) )
        return 0;
    if( !PyType_Check( kind ) )
    {
        PyObjectPtr pystr( PyObject_Str( kind ) );
        if( !pystr )
            return 0;
        PyErr_Format(
            PyExc_TypeError,
            "%s is not a type",
            PyString_AS_STRING( pystr.get() )
        );
        return 0;
    }
    int ok = PyObject_IsInstance( value, kind );
    if( ok < 0 )
        return 0;
    if( ok == 0 )
    {
        PyErr_Format(
            PyExc_TypeError,
            "expression value has invalid type '%s'",
            value->ob_type->tp_name
        );
        return 0;
    }
    return newref( value );
}


/* Validate that an object is a Declarative type.

Parameters
----------
klass : object
    The object to validate.

*/
static PyObject*
validate_declarative( PyObject* mod, PyObject* klass )
{
    if( !PyType_Check( klass ) )
    {
        PyObjectPtr pystr( PyObject_Str( klass ) );
        if( !pystr )
            return 0;
        PyErr_Format(
            PyExc_TypeError,
            "%s is not a type",
            PyString_AS_STRING( pystr.get() )
        );
        return 0;
    }
    int ok = PyObject_IsSubclass( klass, Declarative );
    if( ok < 0 )
        return 0;
    if( ok == 0 )
    {
        PyErr_Format(
            PyExc_TypeError,
            "'%s' is not a Declarative type",
            reinterpret_cast<PyTypeObject*>( klass )->tp_name
        );
        return 0;
    }
    Py_RETURN_NONE;
}

