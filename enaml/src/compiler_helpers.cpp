/*-----------------------------------------------------------------------------
| Copyright (c) 2013, Nucleic Development Team.
|
| Distributed under the terms of the Modified BSD License.
|
| The full license is in the file LICENSE, distributed with this software.
|----------------------------------------------------------------------------*/
#include "pythonhelpersex"

using namespace PythonHelpers;


// Static classes assigned during startup
static PyObject* Alias
static PyObject* Declarative;
static PyObject* DeclarativeNode;
static PyObject* EnamlDefMeta;
static PyObject* EnamlDefNode;
static PyObject* Member;
static PyObject* Template;
static PyObject* TemplateNode;
static PyObject* TemplateInstNode;

// Static utils assigned during startup
static PyObject* sortedmap;
static PyObject* empty_tuple;

// Statically allocated strings
static PyObject* add_specialization_str
static PyObject* copy_str;
static PyObject* d_member_str;
static PyObject* dunder_name_str;
static PyObject* dunder_node_str;
static PyObject* engine_str;
static PyObject* identifier_str;
static PyObject* klass_str;
static PyObject* metadata_str;
static PyObject* name_str;
static PyObject* names_str;
static PyObject* scope_key_str;
static PyObject* starname_str;
static PyObject* store_locals_str;
static PyObject* super_node_str;
static PyObject* template_node_str;
static PyObject* template_scope_str;


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
    if( !node.setattr( klass_str, klass ) )
        return 0;
    if( !node.setattr( identifier_str, identifier ) )
        return 0;
    if( !node.setattr( scope_key_str, scope_key ) )
        return 0;
    if( !node.setattr( store_locals_str, store_locals ) )
        return 0;
    PyObjectPtr super_node( PyObject_GetAttr( klass, dunder_node_str ) );
    if( super_node && super_node.get() != Py_None )
    {
        PyObjectPtr copy_method( super_node.getattr( copy_str ) );
        if( !copy_method )
            return 0;
        super_node = PyObject_Call( copy_method.get(), empty_tuple, 0 );
        if( !super_node )
            return 0;
        if( !node.setattr( super_node_str, super_node.get() ) )
            return 0;
        PyObjectPtr engine( super_node.getattr( engine_str ) );
        if( !engine )
            return 0;
        if( !node.setattr( engine_str, engine.get() ) )
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


/* Make a new template if needed and add the specialization.

Parameters
----------
paramspec : tuple
    The tuple of the parameter specialization arguments.

func : FunctionType
    The function which implements the template.

name : str
    The name of the template.

f_globals : dict
    The globals dictionary for the module.

template_map : dict
    The mapping of templates already created for the module.

*/
static PyObject*
make_template( PyObject* mod, PyObject* args )
{
    PyObject* paramspec;
    PyObject* func;
    PyObject* name;
    PyObject* f_globals;
    PyObject* template_map;
    if( !PyArg_UnpackTuple( args, "make_template", 5, 5,
        &paramspec, &func, &name, &f_globals, &template_map ) )
        return 0;
    if( !PyString_CheckExact( name ) )
        return py_type_fail( "argument 3 must be a string" );
    if( !PyDict_CheckExact( f_globals ) )
        return py_type_fail( "argument 4 must be a dict" );
    if( !PyDict_CheckExact( template_map ) )
        return py_type_fail( "argument 5 must be a dict" );
    PyObjectPtr templ( PyDict_GetItem( template_map, name ) );
    if( templ )
    {
        if( PyDict_GetItem( f_globals, name ) != templ.get() )
        {
            PyErr_Format(
                PyExc_TypeError,
                "template '%s' was deleted before being specialized",
                PyString_AS_STRING( name )
            );
            return 0;
        }
    }
    else
    {
        templ = PyObject_Call( Template, empty_tuple, 0 );
        if( !templ )
            return 0;
        PyObject* modname = PyDict_GetItem( f_globals, dunder_name_str );
        if( modname && !templ.setattr( module_str, modname ) )
            return 0;
        if( !templ.setattr( name_str, name ) )
            return 0;
        PyDict_SetItem( template_map, name, templ.get() );
        PyDict_SetItem( f_globals, name, templ.get() );
    }
    PyObjectPtr method( templ.getattr( add_specialization_str ) );
    if( !method )
        return 0;
    PyObjectPtr args( PyTuple_Pack( 2, paramspec, func ) );
    if( !args )
        return 0;
    if( !method( args ) )
        return 0;
    Py_RETURN_NONE;
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
    PyObjectPtr temp_node( PyObject_GetAttr( inst, template_node_str ) );
    if( !tnode )
        return 0;
    if( !node.setattr( template_node_str, temp_node.get() ) )
        return 0;
    if( !node.setattr( names_str, names ) )
        return 0;
    if( !node.setattr( starname_str, starname ) )
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
        return py_type_fail( "argument 2 must be a tuple" );
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


/* Validate the value for a parameter specification.

Parameters
----------
index : int
    The integer index of the parameter being specialized.

spec : object
    The parameter specialization.

*/
static PyObject*
validate_spec( PyObject* mod, PyObject* args )
{
    PyObject* index;
    PyObject* spec;
    if( !PyArg_UnpackTuple( args, "validate_spec", 2, 2, &index, &spec ) )
        return 0;
    if( !PyInt_CheckExact( index ) )
        return py_type_fail( "argument 1 must be an int" );
    if( spec == Py_None )
    {
        PyErr_Format(
            PyExc_TypeError,
            "can't specialize template parameter %d with None",
            PyInt_AS_LONG( index )
        );
        return 0;
    }
    long hash = PyObject_Hash( spec );
    if( hash == -1 && PyErr_Occurred() )
    {
        PyErr_Clear();
        PyErr_Format(
            "template parameter %d has unhashable type: '%s'",
            PyInt_AS_LONG( index ),
            spec->ob_type->tp_name
        );
        return 0;
    }
    return newref( spec );
}


/* Validate that an object is a Template.

Parameters
----------
template : object
    The object to validate.

*/
static PyObject*
validate_template( PyObject* mod, PyObject* templ )
{
    if( !PyObject_TypeCheck( templ, Template ) )
    {
        PyObjectPtr pystr( PyObject_Str( templ ) );
        if( !pystr )
            return 0;
        PyErr_Format(
            PyExc_TypeError,
            "%s is not a template",
            PyString_AS_STRING( pystr )
        );
        return 0;
    }
    return newref( templ );
}


/* Validate the length of a template instantiation

Parameters
----------
template_inst : TemplateInstNode
    The template instantiation node.

n : int
    The number of positional parameters.

ex_unpack : bool
    Wether or not the unpacking accepts *args.

*/
static PyObject*
validate_unpack_size( PyObject* mod, PyObject* args )
{
    PyObject* template_inst;
    PyObject* n;
    PyObject* ex_unpack;
    if( !PyArg_UnpackTuple( args, "validate_unpack_size", 3, 3,
        &template_inst, &n, &ex_unpack ) )
        return 0;
    if( !PyInt_CheckExact( n ) )
        return py_type_fail( "argument 2 must be an int" );
    if( !PyBool_Check( ex_unpack ) )
        return py_type_fail( "argument 3 must be an int" );
    PyObjectPtr node( PyObject_GetAttr( template_inst, template_node_str ) );
    if( !node )
        return 0;
    PyObjectPtr method( node.getattr( size_str ) );
    if( !method )
        return 0;
    PyObjectPtr pysize( PyObject_Call( method.get(), empty_tuple, 0 ) );
    if( !pysize )
        return 0;
    if( !PyInt_CheckExact( pysize ) )
        return py_type_fail( "expected an int for template size" );
    long size = PyInt_AS_LONG( pysize );
    long nsize = PyInt_AS_LONG( n );
    if( size < nsize )
    {
        PyErr_Format(
            PyExc_ValueError,
            "need more that %d %s to unpack",
            size,
            size > 1 ? "values" : "value"
        );
        return 0;
    }
    if( ex_unpack == Py_False && size > nsize )
        return py_value_fail( "too many values to unpack" );
    return newref( template_inst );
}


/* Validate an alias declaration.

Parameters
----------
node_map : dict
    A dictionary which maps node id to node for the block.

target : str
    The identifier of the target object in the block.

attr : str
    The attribute name aliased on the target. This can be an
    empty string if an attribute is not aliased.

*/
static bool
validate_alias( PyObject* node_map, PyObject* target, PyObject* attr )
{
    PyObjectPtr target_node( xnewref( PyDict_GetItem( node_map, target ) ) );
    if( !target_node )
    {
        PyErr_Format(
            PyExc_TypeError,
            "'%s' is not a valid alias target",
            PyString_AS_STRING( target )
        );
        return false;
    }
    if( PyStr_GET_SIZE( attr ) > 0 )
    {
        PyObjectPtr klass( target_node.getattr( klass_str ) );
        if( !klass )
            return false;
        PyObjectPtr item( klass.getattr( attr ) );
        if( !item )
        {
            if( !PyErr_ExceptionMatches( PyExc_AttributeError ) )
                return false;
            PyErr_Clear()
            PyErr_Format(
                PyExc_TypeError,
                "'%s' is not a valid alias attribute",
                PyString_AS_STRING( attr )
            );
            return false;
        }
        PyObjectPtr types( PyTuple_Pack( 2, Alias, Member ) );
        if( !types )
            return false;
        int ok = PyObject_IsInstance( item.get(), types.get() );
        if( ok < 0 )
            return false;
        if( ok == 0 )
        {
            PyErr_Format(
                PyExc_TypeError,
                "'%s' is not a valid alias attribute",
                PyString_AS_STRING( attr )
            );
            return false;
        }
        if( PyObject_TypeCheck( item.get(), Member ) )
        {
            PyObjectPtr metadata( item.getattr( metatdata_str ) );
            if( !metadata )
                return false;
            if( metadata.get() == Py_None || PyDict_GetItem( metadata.get(), d_member_str ) != Py_True )
            {
                PyErr_Format(
                    PyExc_TypeError,
                    "alias '%s.%s' resolves to a non-declarative member",
                    target, attr
                );
                return false;
            }
        }
    }
    return true;
}


/* Add an alias to a Declarative subclass.

Parameters
----------
node_map : dict
    A dict mapping identifier to declarative child nodes for the
    entire enamldef block.

node : EnamlDefNode
    The enamldef node for which an alias should be added.

name : str
    The name of the alias.

target : str
    The target of the alias.

attr : str
    The attribute being accessed on the target. This should be
    an empty string for object aliases.

*/
static PyObject*
add_alias( PyObject* mod, PyObject* args )
{
    PyObject* node_map;
    PyObject* node;
    PyObject* name;
    PyObject* target;
    PyObject* attr;
    if( !PyArg_UnpackTuple( args, "add_alias", 5, 5,
        &node_map, &node, &name, &target, &attr ) )
        return 0;
    if( !PyDict_CheckExact( node_map ) )
        return py_type_fail( "argument 1 must be a dict" );
    if( !PyString_CheckExact( name ) )
        return py_type_fail( "argument 3 must be a string" );
    if( !PyString_CheckExact( target ) )
        return py_type_fail( "argument 4 must be a string" );
    if( !PyString_CheckExact( attr ) )
        return py_type_fail( "argument 5 must be a string" );
    if( !validate_alias( node_map, target, attr ) )
        return 0;
    PyObjectPtr klass( PyObject_GetAttr( node, klass_str ) );
    if( !klass )
        return 0;
    PyObjectPtr item( klass.getattr( name ) )
    if( !item )
    {
        if( PyErr_ExceptionMatches( PyExc_AttributeError ) )
            PyErr_Clear();
        else
            return 0;
    }
    if( item && PyObject_TypeCheck( item.get(), Alias ) )
    {

    }
    Py_RETURN_NONE;
}
/*
def add_alias(node_map, node, name, target, attr):
    validate_alias(node_map, target, attr)
    klass = node.klass
    item = getattr(klass, name, None)
    if isinstance(item, Alias):
        msg = "can't override alias '%s'"
        raise TypeError(msg % name)
    if name in klass.members():
        msg = "can't override member '%s' with an alias"
        raise TypeError(msg % name)
    alias = Alias(target, attr, node.scope_key)
    setattr(klass, name, alias)
    if node.aliased_nodes is None:
        node.aliased_nodes = sortedmap()
    node.aliased_nodes[target] = node_map[target]
*/
