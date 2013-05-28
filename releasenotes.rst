Enaml Release Notes
===================
0.7.11 - 05/28/2013
-------------------
- Claw back the direct exposure of the Qt stylesheets. 947760ebcd_

.. _947760ebcd: https://github.com/nucleic/enaml/commit/947760ebcd68f351f268913ebbd396a6da24f06d

0.7.10 - 05/26/2013
-------------------
- Expose the Qt stylesheet directly for the dock area. 5877335bcf_
- Add the ability to style the various dock area buttons. 5877335bcf_

.. _5877335bcf: https://github.com/nucleic/enaml/commit/5877335bcf8fd09c9d066a17905b4d92ca24de8d

0.7.9 - 05/24/2013
------------------
- Make the close button on dock items configurable. d839fb0c2b_
- Expose a public api for manipulating the dock layout. e269adbdb2_
- Expose user configurable dock area styles. 4c05d5953f_

.. _4c05d5953f: https://github.com/nucleic/enaml/commit/4c05d5953fd0cbefdb66ca502ff662d259955ee1
.. _e269adbdb2: https://github.com/nucleic/enaml/commit/e269adbdb23ecfd6c6728af3ca8857e20d40415f
.. _d839fb0c2b: https://github.com/nucleic/enaml/commit/d839fb0c2bd096a6580d8ab887dfc6787928bcd5

0.7.8 - 05/20/2013
------------------
- Add support for maximizing a docked item within a DockArea. a051862ce5_
- Update the popup view to use a 45 degree angled arrow. f3edc88fe1_
- Miscellaneous updates and bug fixes to the DockArea.

.. _a051862ce5: https://github.com/nucleic/enaml/commit/a051862ce5dbe2240295c4ae9fc19187554a928f
.. _f3edc88fe1: : https://github.com/nucleic/enaml/commit/f3edc88fe163cbe02b08b5215f78de0fbd1ac61b

0.7.7 - 05/09/2013
------------------
- Add support for floating "dock rafts" in the DockArea. 402330dcaf_
- Add a PopupView widget to support transparent popups and growl-style notifications. a5117121bf_

.. _402330dcaf: https://github.com/nucleic/enaml/commit/402330dcafefaf8470db74bf632d58f039fc4a4f
.. _a5117121bf: https://github.com/nucleic/enaml/commit/a5117121bf5e553a6d5953685605494d676d1661

0.7.6 - 04/25/2013
------------------
- Add an advanced DockArea widget. 3ed122b110_
- Add popup() functionality to the Menu widget. 5363a56f33_

.. _3ed122b110: https://github.com/nucleic/enaml/commit/3ed122b11050ee72383aa0ef08ca2537ec7eb841
.. _5363a56f33: https://github.com/nucleic/enaml/commit/5363a56f336e7302d6c2876e0b630794b9f751ae

0.7.5 - 04/09/2013
------------------
- Fix a bug in the Wx main window implementation. 39f6baee49_

.. _39f6baee49: https://github.com/nucleic/enaml/commit/39f6baee49ddb601f8fde5b222fadf4053075a73

0.7.4 - 04/04/2013
------------------
- Add border support for Container on the Qt backend. 505662d5f1_
- Workaround a logic bug in Wx's handling of modal windows. 56a1e00112_
- Workaround a Wx segfault during window destruction. a8525788c9_

.. _505662d5f1: https://github.com/nucleic/enaml/commit/505662d5f1ad0bdf50a4439873a252c2367dc418
.. _56a1e00112: https://github.com/nucleic/enaml/commit/56a1e001127f12ea971b11343e58711466af1895
.. _a8525788c9: https://github.com/nucleic/enaml/commit/a8525788c9a8ccf50c657fefc85db66d0a78abf9

0.7.3 - 04/03/2013
------------------
- Added support for adding/removing models in a ViewTable. 5bc1809340_
- Added an ObjectCombo control which is a more flexible combo box. 51f3a3c6d3_
- Emit useful error messages when a backend does not implement a control. b264b3b927_

.. _5bc1809340: https://github.com/nucleic/enaml/commit/5bc1809340543aa7184a96cd7a1da3daa37c19dd
.. _51f3a3c6d3: https://github.com/nucleic/enaml/commit/51f3a3c6d3e6fe8c076a8baa26c33ada895beb18
.. _b264b3b927: https://github.com/nucleic/enaml/commit/b264b3b927b979fb83766e82656f70d0023c6a48

0.7.2 - 04/02/2013
------------------
- Added first real cut at a model-viewer grid-based control. de0d8e35ae_
- Fix a bug in size hinting during complex relayouts. 963cee88d0_
- Added hooks for proxy-specific customization. 3e045dfb18_

.. _de0d8e35ae: https://github.com/nucleic/enaml/commit/de0d8e35aee42d5eda63ad0bef0b8eb0adf299f5
.. _963cee88d0: https://github.com/nucleic/enaml/commit/963cee88d09e2e0ff0c9c4d41b2ac2e8ee6f4ab6
.. _3e045dfb18: https://github.com/nucleic/enaml/commit/3e045dfb18ee74000106c7559626449102930010

0.7.1 - 03/28/2013
------------------
- Updated compiler infrastructure to produce more extensible parse trees.
- Various bug fixes.

0.7.0 - 03/20/2013
------------------
- First release under new nucleic org.
- Rewrite of entire framework to sit on top of Atom instead of Traits.
- Vastly improved backend architecture.
- Improved compile-time operator binding.

0.6.8 - 02/14/2013
------------------
- Added ability to change the Z order of a window and a flag to make it stay on top. d6f618101f_
- Added a multiline text entry widget. dde4bd3409_
- Bugfix when ImageView is used in a ScrollArea. 67133d3fec_

.. _d6f618101f: https://github.com/enthought/enaml/commit/d6f618101f281aec8fd124fc5d7faf51066ffc99
.. _dde4bd3409: https://github.com/enthought/enaml/commit/dde4bd34097c59d982ebf5121e0a111b88c1a3f8
.. _67133d3fec: https://github.com/enthought/enaml/commit/67133d3fec03c567dab38aa9123002cab4f6215b


0.6.7 - 01/23/2013
------------------
- Added a `root_object()` method on the `Object` class which returns the root of the object tree. d9b4830963_
- Properly handle window modality on the Qt backend. 28f2433814_
- Add a `destroy_on_close` flag to the `Window` class. 2a63e8cefd_
- Prevent Wx from destroying top-level windows by default. 8e298e768e_
- Add support for adding windows to a session at run-time. c090c0fad6_
- Fix the lifetime bug with the `FileDialog`. 8e354de858_

.. _d9b4830963: https://github.com/enthought/enaml/commit/d9b48309631ed315b67ddf9c4222a2efcf4858ee
.. _28f2433814: https://github.com/enthought/enaml/commit/28f243381439ce1ce263cad2672b62a96bc87a0c
.. _2a63e8cefd: https://github.com/enthought/enaml/commit/2a63e8cefde29416291536ec6c02a05b612e11b1
.. _8e298e768e: https://github.com/enthought/enaml/commit/8e298e768eb45248cc98f682c9cc3b3f473b2a29
.. _c090c0fad6: https://github.com/enthought/enaml/commit/c090c0fad64a30936fc79774f8e851dca46076b6
.. _8e354de858: https://github.com/enthought/enaml/commit/8e354de858a6ee5deeda96dafa6322579c5514a6


0.6.6 - 01/10/2013
------------------
- Fix the broken unittests and make them Python 2.6 safe. 2c1d7f01d_

.. _22c1d7f01d: https://github.com/enthought/enaml/commit/22c1d7f01d844979c166e2f156d18a553f2c0152


0.6.5 - 01/10/2013
------------------
- Add a stretch factor to the Splitter widget. c2272cf1ef_
- Fix bugs in the Wx splitter implementation. dfa542ba3d_

.. _c2272cf1ef: https://github.com/enthought/enaml/commit/c2272cf1eff3e667c6ea1d255cc9c13c14745872
.. _dfa542ba3d: https://github.com/enthought/enaml/commit/dfa542ba3d36d6b968bffb1dcd1e0ed96ddbcf3b


0.6.4 - 01/07/2013
------------------
- Add support for icons on notebook pages on the Qt backend. b6426b7ae9_
- Add support for popup menus in the Wx backend (Qt is already supported). 153f3124b2_
- Add simpler way of building the optional C++ extensions. 4eebd59ae5_
- Update enaml-run to play nice with ETS_TOOLKIT. f864975a87_

.. _f864975a87: https://github.com/enthought/enaml/commit/f864975a872189a76dc8a2cf9e2469a78320a906
.. _4eebd59ae5: https://github.com/enthought/enaml/commit/4eebd59ae51df08d255ffe3860db821781f40579
.. _153f3124b2: https://github.com/enthought/enaml/commit/153f3124b2c62f2a5e7695e7ea1a8dff067f2fc5
.. _b6426b7ae9: https://github.com/enthought/enaml/commit/b6426b7ae9bcab9f8549fa635216c6cfd39ee29b


0.6.3 - 12/11/2012
------------------
- Fix critical bug related to traits Disallow and the `attr` keyword. 25755e2bbd_

.. _25755e2bbd: https://github.com/enthought/enaml/commit/25755e2bbd5e2e38e42d30776e1864d52c992af3


0.6.2 - 12/11/2012
------------------
- Fix critical bug for broken dynamic scoping. a788869ab0_

.. _a788869ab0: https://github.com/enthought/enaml/commit/a788869ab0a410c478cbe4cc066fc8ee35b266b8


0.6.1 - 12/10/2012
------------------
- Fix critical bug in compiler and expression objects. dfb6f648a1_

.. _dfb6f648a1: https://github.com/enthought/enaml/commit/dfb6f648a15370249b0a57433b8839a4caba7d35


0.6.0 - 12/10/2012
------------------
- Add Icon and Image support using a lazy loading resource sub-framework. 77d5ca3b01_
- Add a traitsui support via the TraitsItem widget (care of Steven Silvester). 9cb9126da1_
- Add matplotlib support via the MPLCanvas widget (care of Steven Silvester). eaa6294566_
- Updated Session api which is more intuitive and easier to use.
- Updated Object api which is more intuitive and easier to use.
- Object lifecycle reflected in a `state` attribute.
- Huge reduction in memory usage when creating large numbers of objects.
- Huge reduction in time to create large numbers of objects.
- New widget registry make it easier to register custom widgets. cc791a52d7_
- Better and faster code analysis via code tracers. 4eceb09f70_
- Fix a parser bug related to relative imports. 3e43e73e90_
- Various other tweaks, bugfixes, and api cleanup.

.. _77d5ca3b01: https://github.com/enthought/enaml/commit/77d5ca3b0135fa982663d4ce9cf801119617c611
.. _eaa6294566: https://github.com/enthought/enaml/commit/eaa62945663fa9c96aee822c9f31ef966c88fd62
.. _9cb9126da1: https://github.com/enthought/enaml/commit/9cb9126da1e590814ad6dbee9a732c9add185ed6
.. _cc791a52d7: https://github.com/enthought/enaml/commit/cc791a52d772b07c7482427b5b60dcff9d5436c1
.. _4eceb09f70: https://github.com/enthought/enaml/commit/4eceb09f707e7795182013b9f874abf0afbaab41
.. _3e43e73e90: https://github.com/enthought/enaml/commit/3e43e73e90bd392a63a1faa53f821672fdb8c44f


0.5.1 - 11/19/2012
------------------
- Fix a method naming bug in QSingleWidgetLayout. 7a4c9de7e6_
- Fix a test height computation bug in QFlowLayout. a962d2ae78_
- Invalidate the QFlowLayout on layout request. 1e91a54245_
- Dispatch child events immediately when possible. e869f7124f_
- Destroy child widgets after the children change event is emitted. c695ae35ee_
- Add a preliminary WebView widget. 27faa381dc_

.. _27faa381dc: https://github.com/enthought/enaml/commit/27faa381dc5dd6c5cc41a0826df35b71339d3e7e
.. _c695ae35ee: https://github.com/enthought/enaml/commit/c695ae35ee9fcf35964df88831de0d3b30883f78
.. _e869f7124f: https://github.com/enthought/enaml/commit/e869f7124f0e13bea7f35d5f5a91bc89dc1dcd4e
.. _1e91a54245: https://github.com/enthought/enaml/commit/1e91a542452662ebd3dfe9d5a854ec2277f4415d
.. _a962d2ae78: https://github.com/enthought/enaml/commit/a962d2ae78488398cbe50d4ad16bd1cd90a1060b
.. _7a4c9de7e6: https://github.com/enthought/enaml/commit/7a4c9de7e6342b65efd6e3e841be0adfad286d99


0.5.0 - 11/16/2012
------------------
- Merge the feature-async branch into mainline. f86dad8f6e_
- First release with release notes. 8dbed4b9cd_

.. _8dbed4b9cd: https://github.com/enthought/enaml/commit/8dbed4b9cd16d8c9f71ea63dfd92494176fdf753
.. _f86dad8f6e: https://github.com/enthought/enaml/commit/f86dad8f6e3fe0bf07a2cf59765aaa3b934fa233

