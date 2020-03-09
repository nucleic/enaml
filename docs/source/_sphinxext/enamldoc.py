#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
import  re

from atom.api import Member


#------------------------------------------------------------------------------
# AST Nodes
#------------------------------------------------------------------------------
class Docstring(object):

    def __init__(self, body):
        self.body = body

    def render(self):
        lines = []
        for item in self.body:
            lines.extend(item.render())
        return lines


class NormalLine(object):

    def __init__(self, text):
        self.text = text

    def render(self):
        return [self.text]


class Parameters(object):

    def __init__(self, body):
        self.body = body

    def render(self):
        lines = []
        for item in self.body:
            lines.extend(item.render())
        return lines


class ParameterSpec(object):

    def __init__(self, pname, ptype, description):
        self.pname = pname
        self.ptype = ptype
        self.description = description

    def render(self):
        lines = []
        lines.append(':param %s: %s' % (self.pname, self.description))
        if self.ptype:
            lines.append(':type %s: %s' % (self.pname, self.ptype))
        return lines


class Returns(object):

    def __init__(self, body):
        self.body = body

    def render(self):
        lines = []
        for item in self.body:
            lines.extend(item.render())
        return lines


class ReturnSpec(object):

    def __init__(self, rtype, description):
        self.rtype = rtype
        self.description = description

    def render(self):
        lines = []
        lines.append(':rtype: %s' % self.rtype)
        lines.append(':returns: %s' % self.description)
        return lines


#------------------------------------------------------------------------------
# Lexer
#------------------------------------------------------------------------------
dashed_line = 'dashed_line'
empty_line = 'empty_line'
indented_line = 'indented_line'
normal_line = 'normal_line'
parameters_header = 'parameters_header'
parameter_spec = 'parameter_spec'
returns_header = 'returns_header'
star_args = 'star_args'
star_star_kwargs = 'star_star_kwargs'


line_regexes = (
    (parameters_header, re.compile(r'^Parameters$')),
    (returns_header, re.compile(r'^Returns$')),
    (star_args, re.compile(r'^\*([a-zA-Z_][a-zA-Z0-9_]*)$')),
    (star_star_kwargs, re.compile(r'^\*\*([a-zA-Z_][a-zA-Z0-9_]*)$')),
    (parameter_spec, re.compile(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(.*)$')),
    (dashed_line, re.compile(r'^-+$')),
    (indented_line, re.compile(r'^(\s+)[^\s].*$')),
    (normal_line, re.compile(r'^[^\s].*$')),
    (empty_line, re.compile(r'^\s*$')),
)


def lex_line(line):
    for token, rgx in line_regexes:
        match = rgx.match(line)
        if match is not None:
            return (token, line, match)
    raise ValueError('line "%s" failed to lex' % line)


#------------------------------------------------------------------------------
# Parser
#------------------------------------------------------------------------------
def peek(stack):
    if len(stack) == 0:
        return ''
    return stack[-1][0]


def consume_blank_lines(stack):
    while peek(stack) == empty_line:
        stack.pop()


def extract_description(stack):
    parts = []
    while peek(stack) == indented_line:
        token, line, match = stack.pop()
        parts.append(line.strip())
    return ' '.join(parts)


def p_normal(line, match, stack):
    return NormalLine(line)


def p_parameters(line, match, stack):
    if peek(stack) != dashed_line:
        return p_normal(line, match, stack)
    stack.pop()
    body = []
    consume_blank_lines(stack)
    while True:
        p = peek(stack)
        if p == parameter_spec:
            token, line, match = stack.pop()
            consume_blank_lines(stack)
            descr = extract_description(stack)
            pname = match.group(1)
            ptype = match.group(2)
            spec = ParameterSpec(pname, ptype, descr)
            body.append(spec)
            consume_blank_lines(stack)
        elif p == star_args or p == star_star_kwargs:
            token, line, match = stack.pop()
            consume_blank_lines(stack)
            descr = extract_description(stack)
            pname = match.group(1)
            spec = ParameterSpec(pname, '', descr)
            body.append(spec)
            consume_blank_lines(stack)
        else:
            break
    return Parameters(body)


def p_returns(line, match, stack):
    if peek(stack) != dashed_line:
        return p_normal(line, match, stack)
    stack.pop()
    body = []
    consume_blank_lines(stack)
    if peek(stack) == parameter_spec:
        token, line, match = stack.pop()
        consume_blank_lines(stack)
        descr = extract_description(stack)
        rtype = match.group(2)
        spec = ReturnSpec(rtype, descr)
        body.append(spec)
        consume_blank_lines(stack)
    return Returns(body)


DISPATCH_TABLE = {
    dashed_line: p_normal,
    empty_line: p_normal,
    indented_line: p_normal,
    normal_line: p_normal,
    parameters_header: p_parameters,
    parameter_spec: p_normal,
    returns_header: p_returns,
    star_args: p_normal,
    star_star_kwargs: p_normal,
}


def parse(classified):
    body = []
    stack = classified[::-1]
    while stack:
        token, line, match = stack.pop()
        item = DISPATCH_TABLE[token](line, match, stack)
        body.append(item)
    return Docstring(body)


#------------------------------------------------------------------------------
# Docstring Processors
#------------------------------------------------------------------------------
def process_function(app, name, obj, options, lines):
    classified = map(lex_line, lines)
    return parse(classified).render()


def process_attribute(app, name, obj, options, lines):
    # if isinstance(obj, Member):
    #     # indent = '    '
    #     # name = type(obj).__name__
    #     # new = [indent + name, u'']
    #     # for line in lines:
    #     #     new.append(indent + line)
    #     # lines = new
    #     pass
    return lines


HANDLERS = {
    'function': process_function,
    'method': process_function,
    'attribute': process_attribute,
}


def process_docstring(app, what, name, obj, options, lines):
    handler = HANDLERS.get(what)
    if handler is not None:
        modified_lines = handler(app, name, obj, options, lines[:])
        lines[:] = modified_lines


def setup(app):
    app.connect('autodoc-process-docstring', process_docstring)
