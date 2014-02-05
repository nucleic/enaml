Enaml Workbench Developer Crash Course
======================================
This document is a short introduction to the Enaml Workbench plugin framework.
It is intended for developers of plugin applications that need to get up and
running with the framework in a short amount of time. The Workbench framework
is not large, and a good developer can be comfortable with it in an afternoon.

This document covers the core concepts, terminology, and classes of the
framework. The accompanying example pulls everything together with a
simple plugin application which allows toggling between various views.

Concepts
--------
Writing large applications is hard. Writing large UI applications is even
worse. Writing large UI applications which can be *extended at runtime* by
other developers in arbitrary ways is a recipe for hair loss. There are several
difficult problems which must be addressed when developing such applications,
some of the most notable are:

Registration
	How does user code get dynamically registered at runtime?

Life Cyle
	When and how should user code be loaded and run? How and when can
	it be unloaded and stopped?

Dependencies
	How does the application get started without requiring all user
	inputs at startup? How does the application avoid loading external
	dependencies until they are actually required?

Notifications
	How can various parts of the application be notified when user
	code is registered and unregistered?

User Interfaces
	How can the application be flexible enough to allow user code to add
	user interface elements to the window at runtime, without clobbering
	existing user interface elements?

Flexibility
	How can an application be designed in such a way where it may be
	extended to support future use cases which are not yet conceived?

Ease of Use
	How can all of these difficult problems be solved in such a way that
	a good developer can be comfortable developing for the application
	in an afternoon?

The Enaml Workbench framework attempts to solve these problems by providing
a set of low-level components which can be used to develop high-level plugin
applications. Think of it as a mini-Eclipse framework for Enaml.

Unlike Eclipse however, the Enaml Workbench framework strives to be compact
and efficient. Following the "less is more" mantra, it seeks to provide only
the core low-level features required for generic plugin applications. It is
intended that the core development team for a large application will build
domain specific abstractions on top of the core workbench pieces which will
then used to assemble the final application.

Terminology
-----------
Before continuuing with the crash course, the following terminology is
introduced and used throughout the rest of the document.

Workbench
	The core framework object which manages the registration of plugin
	manifests and the creation of plugin objects. It acts as the central
	registry and primary communication hub for a plugin application.

Plugin Manifest
	An object which declares a plugin and its public behavior. It does
	not provide an implementation of that behavior.

Plugin
	An object which can be dynamically loaded and unloaded from a
	workbench. It is the implementation of the behavior defined by
	its plugin manifest. This term is often overload to indicate the
	collection of manifest, plugin, extension points, and extensions.
	That is 'plugin' can refer to the actual instance object, or the
	entire package of related objects written by the developer.

Extension Point
	A declaration in a plugin manifest which advertises that other plugins
	may contribute functionality to this plugin through extensions. It
	defines the interface to which an extension must conform in order to
	be useful to the plugin which declares the extension point.

Extension
	A contribution to the extension point of a plugin. An extension adds
	functionality and behavior to an existing application by implementing
	the interface required of a given extension point.

Classes
-------
This section covers the core classes of the framework. The goal is provide
a high level understanding of how the framework is architected and how the
various pieces fit together.

Workbench
~~~~~~~~~
The Workbench class acts as the fundamental registry and manager object for
all the other parts of the plugin framework. As a central hub, it's usually
possible to access any object of interest in the application by starting with
a reference to the workbench object.

The core `Workbench` class can be imported from `enaml.workbench.api`.

The core `Workbench` class may be used directly, though application developers
will typically create a subclass to register default plugins on startup. A
perfect example of this is the `UIWorkbench` subclass which registers the
`enaml.workbench.core` and `enaml.workbench.ui` plugins when started.

The following methods on Workbench are of particular interest:

register
	This method is used to register a `PluginManifest` instance with the
	workbench. This is the one-and-only way to contribute plugins to an
	application, whether during initialization or later at runtime.

unregister
	This method is used to unregister a plugin manifest which was previous
	added to the workbench with a call to `register`. This is the one-and-
	only way to remove plugins from the workbench.

get_plugin
	This method is used to query for and lazily create the plugin object
	for a manifest added by a call to `register`. The plugin object will
	only be created the *first* time this method is called. Future calls
	will return the cached plugin object.

get_extension_point
	This method will return the extension point declared by a given
	plugin. The extension point can be queried for contributed extensions
	at runtime.

PluginManifest
~~~~~~~~~~~~~~
The PluginManifest class is used to describe a plugin in terms of its
extension points and extensions. It also defines a globally unique
identifier for the plugin along with an optional factory function which
can be used to create the underlying plugin instance when needed.

The `PluginManifest` class can be imported from `enaml.workbench.api`.

The PluginManifest class is a declarative class and defines the following
attributes of interest:

id
	This is a globally unique identifier which identifies both the manifest
	and the plugin which will be created for it. It should be a string in
	dot separated form, typically 'org.pkg.module.name'. It also servers as
	the enclosing namespace for the identifiers of its extension points and
	extensions. The Global uniqueness of this identifier is enfored.

factory
	A callable which takes no arguments and returns an instance of Plugin.
	For most use-cases, this factory can be ignored. The default factory
	will create an instance of the default Plugin class which is suitable
	for the frequent case of a plugin providing nothing but extensions to
	the extension points of other plugins.

Since this class is declarative, children may be defined on it. In particular,
a plugin's extension points and extensions are defined by declaring children
of type `ExtensionPoint` and `Extension` on the plugin manifest.


Plugin
~~~~~~
The Plugin class is what does the actual work for implementing the behaviors
defined by extension points. It acts as a sort of manager, ensuring that the
extensions which were contributed to a given extension point are invoked
properly and in accordance with their interface.

Well-behaved plugins also react appropriately when extensions are added or
removed from one of their extension points at runtime.

The `Plugin` class can be imported from `enaml.workbench.api`.

It will be uncommon for most end-user developers to ever need to create a
custom plugin class. That job is reserved for core application developers
which actually define how the application can be extened. That said, there
are two methods on a plugin which will be of interest to developers:

start
    This method will be called by the workbench after it creates the
    plugin. The default implementation does nothing and can be ignored
    by subclasses which do not need life-cycle behavior.

stop
	This method will be called by the workbench when the plugin is
	removed. The default implementation does nothing and can be
	ignored by subclasses which do not need life-cycle behavior.

ExtensionPoint
~~~~~~~~~~~~~~
The ExtensionPoint class is used to publicly declare a point to which
extensions can be contributed to the plugin. Is is declared as the
child of a PluginManifest.

The `ExtensionPoint` class can be imported from `enaml.workbench.api`.

The ExtensionPoint class is a declarative class and defines the following
attributes of interest:

id
	The unique identifier for the extension point. It should be simple
	string with no dots. The fully qualified id of the extension point
	will be formed by combining the id of the parent plugin manifest
	with this id.

Declarative children of an extension point to not have any meaning as
far as the workbench framework is concerned.

Extension
~~~~~~~~~
The Extension class is used to pubclicly declare the contribution a plugin
provided to the extension point of another plugin (including itself!). It
is declared as the child of a PluginManifest.

The `Extension` class can be imported from `enaml.workbench.api`.

The Extension class is a declarative class and defines the following
attributes of interest:

id
	The unique identifier for the extension. It should be simple string
	with no dots. The fully qualified id of the extension will be formed
	by combining the id of the parent plugin manifest with this id.

point
	The fully qualified id of the extension point to which the extension
	is contributing.

rank
	An optional integer to rank the extension among other extensions
	contributed to the same extension point. The semantics of how the
	rank value is used is specified by a given extension point.

factory
	An optional callable which is used to create the implementation
	object for an extension. The semantics of the call signature and
	return value are specified by a given extension point.
