#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from . import compiler_common as cmn


class BaseBlockCompiler(cmn.CompilerBase):
    """ The base class of the block compilers.

    """
    #: The set of local names for the compiler.
    local_names = Typed(set, ())

    #: A mapping of ast node -> compiler node index for the block.
    index_map = Typed(dict, ())

    def parent_index(self):
        """ Get the node index for the parent node.

        Returns
        -------
        result : int
            The compiler node index for the node represented by the
            current parent ast node.

        """
        return self.index_map[self.ancestor()]


class FirstPassBlockCompiler(BaseBlockCompiler):
    """ The first pass block compiler.

    This is a base class for the first pass compilers for the enamldef
    and template block definitions.

    """
    #: A mapping of auxiliary ast node -> compiler node index.
    aux_index_map = Typed(dict, ())

    def visit_ChildDef(self, node):
        # Claim the index for the compiler node.
        index = len(self.index_map)
        self.index_map[node] = index

        # Setup the line number for the child def.
        cg = self.code_generator
        cg.set_lineno(node.lineno)

        # Generate the child def compiler node.
        cmn.gen_child_def_node(cg, node, self.local_names)

        # Store the compiler node in the node list.
        cmn.store_node(cg, index)

        # Append the compiler node to the parent node.
        cmn.append_node(cg, self.parent_index(), index)

        # Visit the body of the child def.
        for item in node.body:
            self.visit(item)

    def visit_TemplateInst(self, node):
        # No pragmas are supported yet for template inst nodes.
        cmn.warn_pragmas(node, self.filename)

        # Claim the index for the compiler node.
        index = len(self.index_map)
        self.index_map[node] = index

        # Setup the line number for the template inst.
        cg = self.code_generator
        cg.set_lineno(node.lineno)

        # Generate the template inst compiler node.
        cmn.gen_template_inst_node(cg, node, self.local_names)

        # Store the compiler node in the node list.
        cmn.store_node(cg, index)

        # Append the compiler node to the parent node.
        cmn.append_node(cg, self.parent_index(), index)

        # Visit the body of the template inst.
        for item in node.body:
            self.visit(item)

    def visit_TemplateInstBinding(self, node):
        # Grab the index of the parent node for later use.
        self.aux_index_map[node] = self.parent_index()

    def visit_Binding(self, node):
        # Grab the index of the parent node for later use.
        self.aux_index_map[node] = self.parent_index()

    def visit_ExBinding(self, node):
        # Grab the index of the parent node for later use.
        self.aux_index_map[node] = self.parent_index()

    def visit_AliasExpr(self, node):
        # Grab the index of the parent node for later use.
        self.aux_index_map[node] = self.parent_index()

    def visit_StorageExpr(self, node):
        # Grab the index of the parent node for later use.
        self.aux_index_map[node] = self.parent_index()

    def visit_FuncDef(self, node):
        # Grab the index of the parent node for later use.
        self.aux_index_map[node] = self.parent_index()


class SecondPassBlockCompiler(BaseBlockCompiler):
    """ The second pass block compiler.

    This is a base class for the second pass compilers for the enamldef
    and template block definitions.

    """
    def visit_ChildDef(self, node):
        # Visit the body of the child def.
        for item in node.body:
            self.visit(item)

    def visit_TemplateInst(self, node):
        if node.body:
            # Create the unpack map.
            cg = self.code_generator
            index = self.index_map[node]
            cmn.load_helper(cg, 'make_unpack_map')
            cmn.load_node(cg, index)
            cg.call_function(1)
            cg.store_fast(cmn.UNPACK_MAP)

            # Visit the body of the template inst.
            for item in node.body:
                self.visit(item)

    def visit_TemplateInstBinding(self, node):
        # Generate the code for the template inst binding.
        cg = self.code_generator
        index = self.parent_index()
        cmn.gen_template_inst_binding(cg, node, index)

    def visit_Binding(self, node):
        # Generate the code for the operator binding.
        cg = self.code_generator
        index = self.parent_index()
        cmn.gen_operator_binding(cg, node.expr, index, node.name)

    def visit_ExBinding(self, node):
        # Generate the code for the operator binding.
        cg = self.code_generator
        index = self.parent_index()
        cmn.gen_operator_binding(cg, node.expr, index, node.chain)

    def visit_AliasExpr(self, node):
        # Generate the code for the alias expression.
        cg = self.code_generator
        index = self.parent_index()
        cmn.gen_alias_expr(cg, node, index)

    def visit_StorageExpr(self, node):
        # Generate the code for the storage expression.
        cg = self.code_generator
        index = self.parent_index()
        cmn.gen_storage_expr(cg, node, index, self.local_names)
        if node.expr is not None:
            cmn.gen_operator_binding(cg, node.expr, index, node.name)

    def visit_FuncDef(self, node):
        # Generate the code for the function declaration.
        cg = self.code_generator
        index = self.parent_index()
        cmn.gen_decl_funcdef(cg, node, index)
