from enaml.workbench.ui.api import UIWorkbench
import enaml

with enaml.imports():
    from sample_plugin import SampleManifest

workbench = UIWorkbench()
workbench.register(SampleManifest())
workbench.run()
