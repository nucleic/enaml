
Plugin Schema
=============
A workbench plugin is specified in the form of a json manifest. The manifest
contains information about the plugin, its extension points, extensions. This
document describes in more detail the JSON plugin schema. The schema itself
is provided in the 'schema.json' file in the same directory as this document.

The following terminology is used in this document.

manifest
	The json document which describes a plugin, its extension points, and
	extensions.

plugin
	A runtime object which is instantiated when its behaviors or extensions
	or required by another part of the framework.

extension point
	A declaration by a plugin that it supports behavior contributions by
	user code. These contributions come in the form of extensions.

extension
	A declaration by a plugin that it can contribute behavior to extension

	points of plugins registered with the workbench.

Plugin Manifest
---------------
The plugin manifest declares various metadata for the plugin as well as
its extension points and extensions. The manifest is a json document with
a single root object. The properties of that object are defined below.

id
	The globally unique identifier of the plugin. This identifier is used
	as the root namespace for all extension points defined by the plugin
	which do not provide a fully-qualified id. This value must be a string
	and should be in dot-separated form. e.g. "company.module.plugin".

name
	An optional human readable name for the plugin. This value is not used
	directly by the framework, but external tools (e.g. a plugin browser)
	may find it useful for presenting information to the user. If this is
	provided, it must be a string.

description
	An optional human readable description for the plugin. This value is not
	used directly by the framework, but external tools (e.g. a plugin browser)
	may find it useful for presenting information to the user. If this is
	provided, it must be a string.

class
	An optional path to the class which implements the plugin. An instance
	of this class will be instantiated the first time the plugin requested.
	If this is provided, it must be a string of the form "pkg.module.Class"
	which points to a subclass of `enaml.workbench.plugin.Plugin`. If this
	is not provided, a generic Plugin instance will be created.

extensionPoints
	An optional array of extension points definitions for this plugin. See
	the section on `Extension Points`_ for more information.

extensions
	An optional array of extension definitions contributed by this plugin.
	See the section on `Extensions`_ for more information.


Extension Points
----------------
An extension point is declared as an element in the 'extension_points' array
of the plugin manifest. It is an object which contains the properties defined
below.

id
	The globally unique identifier of the plugin. This value must be a string
	and can be provided in one of two forms:

	 	- A simple string with no dots. With this form, the extension point is
		  assumed to belong to the namespace defined by the plugin id.

		- A dot separated string. With this form, the extension point is
		  assumed to be fully qualified and may belong to a namespace other
		  than that defined by the plugin id.

	In both cases, the plugin id must be unique in the namespace to which it
	belongs. For all but the most advanced use-cases, the first form of id
	specification is recommended.

name
	An optional human readable name for the extension point. This value is not
	used directly by the framework, but external tools (e.g. a plugin browser)
	may find it useful for presenting information to the user. If this is
	provided, it must be a string.

description
	An optional human readable description for the extension point. This value
	is not used directly by the framework, but external tools (e.g. a plugin
	browser) may find it useful for presenting information to the user. If
	this is provided, it must be a string.


Extensions
----------
An extension is declared as an element in the 'extensions' array of the plugin
manifest. It is an object which container the properties defined below.

point
	The fully qualified identifier of the extension point to which the
	extension contributes. This value must be a string.

class
	An optional path to the class which implements the extension. The
	class will be loaded by the writer of the extension point as required.
	If this is provided, it must be a string of the form "pkg.module.Class"
	which points to a class implementing the interface required by the
	extension point.

configuration
	An optional object which provides configuration data for the extension.
	The can be used by e.g. a menu action extension to provide icon and
	action title data without requiring the action handler to be instantiated.
	The configuration specification for an extension will be defined by the
	extension point to which the extension contributes.

id
	An optional identifier for the extension. If this is provided, it must be
	a string in one of two forms:

		- A simple string with no dots. With this form, the extension is
		  assumed to belong to the namespace defined by the plugin id.

		- A dot separated string. With this form, the extension is assumed
		  to be fully qualified and may belong to a namespace other than that
		  defined by the plugin id.

	In both cases, the extension id must be unique in the namespace to which
	it belongs. For all but the most advanced use-cases, the first form of id
	specification is recommended.

name
	An optional human readable name for the extension. This value is not used
	directly by the framework, but external tools (e.g. a plugin browser) may
	find it useful for presenting information to the user. If this is provided,
	it must be a string.

description
	An optional human readable description for the extension. This value is not
	used directly by the framework, but external tools (e.g. a plugin browser)
	may find it useful for presenting information to the user. If this is
	provided, it must be a string.
