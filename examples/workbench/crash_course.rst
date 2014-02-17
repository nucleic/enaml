Enaml Workbench Developer Crash Course
======================================
This document is a short introduction to the Enaml Workbench plugin framework.
It is intended for developers of plugin applications that need to get up and
running with the framework in a short amount of time. The Workbench framework
is not large, and a good developer can be comfortable with it in an afternoon.

This document covers the concepts, terminology, workflow, and the core plugins
and classes of the framework. The accompanying example demonstrates the various
parts of the framework with a simple plugin application which allows the user
to toggle between a handful of sample views.

Concepts
--------
Writing large applications is hard. Writing large UI applications is harder.
Writing large UI applications which can be *safetly extended at runtime* by
other developers is a recipe for hair loss. There are several difficult issues
which  must be addressed when developing such applications, some of the most
notable are:

Registration
	How does user code get dynamically registered and unregistered at runtime?

Life Cyle
	When and how should user code be loaded and run? How and when and how
	should it be unloaded and stopped?

Dependencies
	How does the application get started without requiring all user code to
	be available at startup? How does the application avoid loading external
	dependencies until they are actually required to do work?

Notifications
	How can various parts of the application be notified when user code is
	registered and unregistered?

User Interfaces
	How can the application be flexible enough to allow user code to add
	user interface elements to the window at runtime, without clobbering
	or interfering with the existing user interface elements?

Flexibility
	How can an application be designed in a way where it may be extended
	to support future use cases which have not yet been conceived?

Ease of Use
	How can all of these difficult problems be solved in such a way that
	a good developer can be comfortable developing with the application
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
	registry and primary communication hub for the various parts of a
	plugin application.

Plugin Manifest
	An object which declares a plugin and its public behavior. It does
	not provide an implementation of that behavior.

Plugin
	An object which can be dynamically loaded and unloaded from a workbench.
	It is the implementation of the behavior defined by its plugin manifest.
	This term is often overload to also indicate the collection of manifest,
	plugin, extension points, and extensions. That is, 'plugin' can refer to
	the actual plugin instance, or the entire package of related objects
	written by the developer.

Extension Point
	A declaration in a plugin manifest which advertises that other plugins
	may contribute functionality to this plugin through extensions. It
	defines the interface to which an extension must conform in order to
	be useful to the plugin which declares the extension point.

Extension
	A contribution to the extension point of a plugin. An extension adds
	functionality and behavior to an existing application by implementing
	the interface required by a given extension point.

Workflow
--------
Using the workbench framework is relatively straightforward and has only
a few conceptual steps.

0. Define the classes which implement your application business logic.
1. If your application will create a plugin which contribute extensions
   to an extension point, define the extension classes and ensure that
   they implement the interface required by the extension point. The
   extension classes should interact with the business logic classes to
   expose their functionality to the rest of the application.
2. If your application will create a plugin which defines new extension
   points, define a Plugin subclasses which will implement the extension
   point behavior by interacting with the extensions contributed to the
   extension point by other plugins.
3. Create a PluginManifest for each plugin defined by your application.
   The manifest will declare the extension points provided by the plugin
   as well as the extensions it contributes to other extension points. If
   needed, it will supply a factory to create the custom Plugin object.
4. Create an instance of Workbench or one of its subclasses.
5. Register the plugin manifests required by your application with the
   workbench. Only the plugins required for startup need to be registered.
   Additional manifest can be added and removed dynamically at runtime.
6. Start the application. How this is done is application dependent.

Points 0 - 3 require the most mental effort. The framework provides a few pre-
defined plugins and Workbench subclasses (described later) which make the last
few steps of the process more-or-less trivial.

The important takeaway here is that the application business logic should be
defined first, and then be bundled up as extensions and extension points to
expose that logic to various other parts of the application. This design
pattern forces a strong separation between logical components. And while it
requires a bit more up-front work, it results in better code reuse and a more
maintainable and extensible code base.

Core Classes
------------
This section covers the core classes of the workbench framework.

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
'enaml.workbench.core' and 'enaml.workbench.ui' plugins when started.

The following methods on a Workbench are of particular interest:

register
	This method is used to register a `PluginManifest` instance with the
	workbench. This is the one-and-only way to contribute plugins to an
	application, whether during initialization or later at runtime.

unregister
	This method is used to unregister a plugin manifest which was previously
	added to the workbench with a call to `register`. This is the one-and-
	only way to remove plugins from the workbench application.

get_plugin
	This method is used to query for, and lazily create, the plugin object
	for a given manifest. The plugin object will be created the *first* time
 	this method is called. Future calls will return the cached plugin object.

get_extension_point
	This method will return the extension point declared by a plugin. The
	extension point can be queried for contributed extensions at runtime.

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
	dot-separated form, typically 'org.pkg.module.name'. It also serves as
	the enclosing namespace for the identifiers of its extension points and
	extensions. The global uniqueness of this identifier is enforced.

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
properly and in accordance with interface defined by the extension point.

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
	will be formed by dot-joining the id of the parent plugin manifest
	with this id.

Declarative children of an extension point do not have any meaning as
far as the workbench framework is concerned.

Extension
~~~~~~~~~
The Extension class is used to pubclicly declare the contribution a plugin
provides to the extension point of another plugin. It is declared as the
child of a PluginManifest.

The `Extension` class can be imported from `enaml.workbench.api`.

The Extension class is a declarative class and defines the following
attributes of interest:

id
	The unique identifier for the extension. It should be simple string
	with no dots. The fully qualified id of the extension will be formed
	by dot-joining the id of the parent plugin manifest with this id.

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

Declarative children of an Extension are allowed, and their semantic meaning
are defined by a given extension point. For example, the extension point
'enaml.workbench.core.commands' allows extension commands to be defined as
declarative children of the extension.

Core Plugin
-----------
The section covers the workbench core plugin.

The core plugin is a pre-defined plugin supplied by the workbench framework.
It provides non-ui related functionality that is useful across a wide variety
of applications. It must be explicitly registered with a workbench in order
to be used.

The `CoreManifest` class can be imported from `enaml.workbench.core.api`. It
is a declarative enamldef and so must be imported from within an Enaml imports
context.

The id for the core plugin is 'enaml.workbench.core' and it declares the
following extension points:

'commands'
	Extensions to this point may contribute `Command` objects which can
	be invoked via the `invoke_command` method of the CorePlugin instance.
	Commands can be provided by declaring them as children of the Extension
	and/or by declaring a factory function which takes the workbench as an
	argument and returns a list of Command instances.

Command
~~~~~~~
A Command object is used to declare that a plugin can take some action when
invoked by a user. It is declared as the child of an Extension which
contributes to the 'enaml.workbench.core.commands' extension point.

The `Command` class can be imported from `enaml.workbench.core.api`.

The Command class is a declarative class and defines the following
attributes of interest:

id
	The globally unique identifier for the command. This should be a
	dot-separated string. The global uniqueness is enforced.

handler
	A callable object which implements the command behavior. It must
	accept a single argument which is an instance of `ExecutionEvent`.

ExecutionEvent
~~~~~~~~~~~~~~
An ExecutionEvent is an object which is passed to a Command handler when
it is invoked by the framework. User code will never directly create an
ExecutionEvent.

An ExecutionEvent has the following attributes of interest:

command
	The Command object which is being invoked.

workbench
	A reference to the workbench which owns the command.

parameters
	A dictionary of user-supplied parameters to the command.

trigger
	The user object which triggered the command.

UI Plugin
---------
This section covers the workbench ui plugin.

The ui plugin is a pre-defined plugin supplied by the workbench framework.
It provides ui-related functionality which is common to a large swath of
UI applications. It must be explicity registered with a workbench in order
to be used.

The `UIManifest` class can be imported from `enaml.workbench.ui.api`. It is
a declarative enamldef and so must be imported from within an Enaml imports
context.

The id of the ui plugin is 'enaml.workbench.ui' and it declares the following
extension points:

'application_factory'
	An Extension to this point can be used to provide a custom
	application object for the workbench. The extension factory should
	accept no arguments and return an Application instance. The highest
	ranking extension will be chosen to create the application.

'window_factory'
	An Extension to this point can be used to provide a custom main
	window for the workbench. The extension factory should accept the
	workbench as an argument and return a WorkbenchWindow instance. The
	highest ranking extension will be chosen to create the window.

'branding'
	An Extension to this point can be used to provide a custom window
	title and icon to the primary workbench window. A Branding object can
	be declared as the child of the extension, or created by the extension
	factory function which accepts the workbench as an argument. The
	highest ranking extension will be chosen to provide the branding.

'actions'
	Extensions to this point can be used to provide menu items and
	action items to be added to the primary workbench window menu bar. The
	extension can declare child MenuItem and ActionItem instances as well
	as provide a factory function which returns a list of the same.

'workspaces'
	Extensions to this point can be used to provide workspaces which
	can be readily swapped to provide the main content for the workbench
	window. The extension factory function should accep the workbench as
	an argument and return an instance of Workspace.

'autostart'
	Extensions to this point can be used to provide the id of a plugin
	which should be started preemptively on application startup. The
	extension should declare children of type Autostart. The plugins will
	be started in order of extension rank. Warning - abusing this facility
	can cause drastic slowdowns in application startup time. Only use it
	if you are *absolutely* sure your plugin must be loaded on startup.

The plugin declares the following extensions:

'default_application_factory'
	This contributes to the 'enaml.workbench.ui.application_factory'
	extension point and provides a default instance of a QtApplication.

'default_window_factory'
	This contributes to the 'enaml.workbench.ui.window_factory' extension
	point and provides a default instance of a WorkbenchWindow.

'default_commands'
	This contributes to the 'enaml.workbench.core.commands' extension point
	and provides the default command for the plugin (described later).

The plugin provides the following commands:

'enaml.workbench.ui.close_window'
	This command will close the primary application window. It takes
	no parameters.

'enaml.workbench.ui.close_workspace'
	This command will close the currently active workspace. It takes
	no parameters.

'enaml.workbench.ui.select_workspace'
	This command will select and activate a new workspace. It takes
	a single 'workspace' parameter which is the fully qualified id of
	the extension point which contributes the workspace of interest.

WorkbenchWindow
~~~~~~~~~~~~~~~
The WorkbenchWindow is an enamldef subclass of the Enaml MainWindow widget.
It is used by the ui plugin to bind to the internal ui window model which
drives the runtime dynamism of the window.

The will be cases where a developer wishes to create a custom workbench
window for one reason or another. This can be done subclassing the plain
WorkbenchWindow and writing a plugin which contributes a factory to the
'enaml.workbench.ui.window_factory' class.

The WorkbenchWindow class can be imported from `enaml.workbench.ui.api`.

Branding
~~~~~~~~
The Branding class is a declarative class which can be used to apply a
custom window title and window icon to the primary application window. This
is a declarative class which can be defined as the child of an extension, or
returned from the factory of an extension which contributes to the
'enaml.workbench.ui.branding' extension point.

The Branding class can be imported from `enaml.workbench.ui.api`.

It has the following attributes of interest:

title
	The string to use as the primary title of the main window.

icon
	The icon to use for the icon of the main window and taskbar.

MenuItem
~~~~~~~~
The MenuItem class is a declarative class which can be used to declare a
menu in the primary window menu bar.

The MenuItem class can be imported from `enaml.workbench.ui.api`.

It has the following attributes of interest:

path
	A "/" separated path to the location of this item in the menu bar.
	This path must be unique for the menu bar, and the parent path must
	exist in the menu bar. The last token in the path is the id of this
	menu item with respect to its siblings. For example, if the path for
	the item is '/foo/bar/baz', then '/foo/bar' is the path for the parent
	menu, and 'baz' is the id of the menu with respect to its siblings.
	*The parent menu need not be defined by the same extension which
	defines the menu. That is, one plugin can contribute a sub-menu to
	a menu defined by another plugin.*

group
	The name of the item group defined by the parent menu to which this
	menu item should be added. For a top-level menu item, the empty group
	is automatically implied.

before
	The id of the sibling item before which this menu item should appear.
	The sibling must exist in the same group as this menu item.

after
	The id of the sibling item after which this menu item should appear.
	This sibling must exist in the same group as this menu item.

label
	The text to diplay as the label for the menu.

visible
	Whether or not the menu is visible.

enabled
	Whether or not the menu is enabled.

A MenuItem can define conceptual groups in which other plugins may contribute
other menu items and action items. A group is defined by declaring a child
ItemGroup object on the menu item. The group will appear on screen in the
order in which they were declared. There is an implicit group with an empty
identifier into which all unclassified items are added. The implicit group
will always appear visually last on the screen.

ItemGroup
~~~~~~~~~
The ItemGroup class is a declarative class used to form a logical and
visual group of items in a menu. It is declared as a child of a MenuItem
and provides a concrete advertisement by the author of a MenuItem that it
expects other MenuItem and ActionItem instances to be added to that point
in the Menu.

The ItemGroup class can be imported from `enaml.workbench.ui.api`.

It has the following attributes of interest:

id
	The identifier of the group within the menu. It must be unique among
	all other group siblings defined for the menu item.

visible
	Whether or not the items in the group are visible.

enabled
	Whether or not the items in the group are enabled.

exclusive
	Whether or not neighboring checkable action items in the group
	should behave as exclusive checkable items.

ActionItem
~~~~~~~~~~
The ActionItem class is used to declare a triggerable item in a menu. It
is declared as a child of a plugin Extension object.

The ActionItem class can be imported from `enaml.workbench.ui.api`.

It has the following attributes of interest:

path
	A "/" separated path to the location of this item in the menu bar.
	This path must be unique for the menu bar, and the parent path must
	exist in the menu bar. The last token in the path is the id of this
	action item with respect to its siblings. For example, if the path for
	the item is '/foo/bar/baz', then '/foo/bar' is the path for the parent
	menu, and 'baz' is the id of the action with respect to its siblings.
	*The parent menu need not be defined by the same extension which
	defines the action. That is, one plugin can contribute an action to a
	menu defined by another plugin.*

group
	The name of the item group defined by the parent menu to which this
	action item should be added.

before
	The id of the sibling item before which this action item should appear.
	The sibling must exist in the same group as this action item.

after
	The id of the sibling item after which this action item should appear.
	This sibling must exist in the same group as this action item.

command
	The identifier of the Command object which should be invoked when
	this action item is triggered by the user.

parameters
	The dictionary of parameters which should be passed to the command
	when it is invoked.

label
	The text to diplay as the label for the action.

shortcut
	The keyboard shortcut which should be bound to trigger action item.

visible
	Whether or not the action is visible.

enabled
	Whether or not the action is enabled.

checkable
	Whether or not the action is checkable.

checked
	Whether or not the action is checked.

icon
	The icon to display next to the action.

tool_tip
	The tool tip text to display when the user hovers over the action.

status_tip
	The text to display in the status bar when the user hovers over the
	action.

Workspace
~~~~~~~~~
The Workspace class is a declarative class which is used to supply the
central window content for a ui workbench application. It contains the
attributes and method which are necessary for the ui plugin to be able
to dynamically switch workspaces at runtime. The application developer
will typically create a custom workspace class for each one of the views
that will be shown in the workbench.

The Workspace class is declarative to allow the developer to fully
leverage the Enaml language in the course of defining their workspace.
It will typically be declared as the child of any object.

The Workspace class can be imported from `enaml.workbench.ui.api`.

It has the following attributes of interest:

window_title
	This is text which will be added to the window title *in addition*
	to the title text which is supplied by a branding extension.

content
	This is an Enaml Container widget which will be used as the primary
	window content. It should be created during the workspace 'start'
	method and will be destroyed by the framework automatically when
	the workspace is stopped.

It has the following methods of interest:

start
    This method is called when the UI plugin starts the workspace. This
    can be used to load content or any other resource which should exist
    for the life of the workspace.

stop
    This method is called when the UI plugin closes the workspace. This
    should be used to release any resources acquired during the lifetime
    of the workspace. The content Container will be destroyed automatically
    after this method returns.

Autostart
~~~~~~~~~
The Autostart class is a declarative class which is used to supply the
plugin id for a plugin which should be automatically started on application
startup.

The Autostart class can be imported from `enaml.workbench.ui.api`.

It has the following attributes of interest.

plugin_id
	This is the id of the plugin to start on application startup. The
	manifest for the plugin must be registered before the ui plugin is
	started.

UI Workbench
------------
The UIWorkbench class is a simple sublass of Workbench for creating ui
applications. This class will automatically register the pre-defined
'core' and 'ui' workbench plugins when it is started.

The UIWorkbench class can be imported from `enaml.workbench.ui.api`.

It has the following methods of interest:

run
    This method will load the core and ui plugins and start the
    main application event loop. This is a blocking call which
    will return when the application event loop exits.
