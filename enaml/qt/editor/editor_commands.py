"""
Editor commands so far:
  set-text
  set-mode
  set-theme

"""
#------------------------------------------------------------------------------
# Enaml -> Qt -> JS
#------------------------------------------------------------------------------

# Enaml sends a message like this to the client
enaml_msg = {
    'action' : 'set-text',
    'payload' : {
	'text' : 'hello world'
    }
}

# Qt client receives this message
def on_message_set_text(self, payload):
    self.set_text(payload['text'])

# Qt client's set_? method changes its values, then
# emits a signal which tells the JS editor to update
def set_text(self, text):
    self._text = text
    self.text_changed.emit(text)

# The JS client responds to the signal and updates the editor
"""
JavaScript code:

// Bind signal to JS handler. py_ace_editor is the Python object that was
// injected into the JS. ace_editor is the JS text editor object.
py_ace_editor.text_changed.connect(ace_editor.getSession().doc, "setValue")

"""

#------------------------------------------------------------------------------
# JS -> Qt
#------------------------------------------------------------------------------

# The JS client binds its events to handlers on the injected Python object
"""
JavaScript code:

// Bind a JS editor event to a Python handler. py_ace_editor is the Python
// object that was injected into the JS. ace_editor is the JS text editor
// object.
py_set_text = function() {
    py_ace_editor.set_text_from_js(ace_editor.getSession().getDocument().getValue())
}

ace_editor.getSession().on("change", py_set_text)

"""

# Python handler
def set_text_from_js(self, text):
    self._text = text

# NOTE: We cannot use set_text here, because if the signal were emitted the text
# would be set twice, so we have to have a method that sets the text but doesn't
# emit the signal.
# XXX: better way to do this so that we avoid having two methods for essentially
# the same operation?
