# -*- coding: utf-8 -*-
from enaml.qt.q_dock_guides import *
from PyQt4.QtGui import *

app = QApplication([])
w = QWidget()
d = QDockGuides(w)
t = QTextEdit(w)
t.setReadOnly(True)
t.setHtml("""
<!DOCTYPE html>
<html>
<body>

<h2>The &lt;blockquote&gt; tag</h2>
<p>The &lt;blockquote&gt; tag specifies a section that is quoted from another source.</p>
<p>Here is a quote from WWF's website:</p>
<blockquote cite="http://www.worldwildlife.org/who/index.html">
For 50 years, WWF has been protecting the future of nature. The world’s leading conservation organization, WWF works in 100 countries and is supported by 1.2 million members in the United States and close to 5 million globally.
</blockquote>
<p><b>Note:</b> Browsers usually indent &lt;blockquote&gt; elements.</p>

<h2>The &lt;q&gt; tag</h2>
<p>The &lt;q&gt; tag defines a short quotation.</p>

<p>WWF's goal is to:
<q>Build a future where people live in harmony with nature.</q>
We hope they succeed.</p>
<p><b>Note:</b> Browsers insert quotation marks around the &lt;q&gt; tag.</p>

</body>
</html>""")
l = QStackedLayout()
l.setStackingMode(QStackedLayout.StackAll)
l.addWidget(t)
l.addWidget(d)
l.setCurrentIndex(1)
w.setLayout(l)
w.show()
app.exec_()
