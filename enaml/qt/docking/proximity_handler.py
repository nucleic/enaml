#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Typed, Value

from enaml.qt.QtCore import QObject

from .q_dock_frame import QDockFrame


class ProximityHandler(QObject):
    """ A class which manages movement of free floating dock frames.

    This class handles the movement of frames, taking into account the
    state of their link button and their proximity to other frames.

    """
    class GraphNode(Atom):
        """ An internal graph node class for the proximity handler.

        """
        #: The dock frame associated with the node.
        frame = Typed(QDockFrame)

        #: The set of bi-direction vertices linked to this node.
        vertices = Typed(set, ())

        #: The tag value used for marking a node during a traversal.
        tag = Value()

        def link(self, node):
            """ Link this node with another vertex.

            Parameters
            ----------
            node : GraphNode
                The node to link with this vertex.

            """
            if node is not self:
                self.vertices.add(node)
                node.vertices.add(self)

        def unlink(self):
            """ Unlink this node from the connected vertices.

            """
            for vertex in self.vertices:
                vertex.vertices.discard(self)
            del self.vertices

    def __init__(self):
        """ Initialize a ProximityHandler.

        """
        super(ProximityHandler, self).__init__()
        self._nodes = {}

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _onLinkToggled(self):
        """ Handle the 'linkButtonToggled' signal on a dock frame.

        """
        self.updateLinks(self.sender())

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def addFrame(self, frame):
        """ Add a dock frame to the proximity handler.

        Parameters
        ----------
        frame : QDockFrame
            The frame to add to the handler. If the frame has already
            been added, this is a no-op.

        """
        nodes = self._nodes
        if frame in nodes:
            return
        nodes[frame] = self.GraphNode(frame=frame)
        frame.linkButtonToggled.connect(self._onLinkToggled)

    def removeFrame(self, frame):
        """ Remove a dock frame from the proximity handler.

        Parameters
        ----------
        frame : QDockFrame
            The frame to remove from the handler. If the frame does not
            exist in the handler, this is a no-op.

        """
        nodes = self._nodes
        if frame not in nodes:
            return
        nodes.pop(frame).unlink()
        frame.linkButtonToggled.disconnect(self._onLinkToggled)

    def hasLinkedFrames(self, frame):
        """ Get whether or not the frame has linked proximal frames.

        Parameters
        ----------
        frame : QDockFrame
            The frame of interest.

        Returns
        -------
        result : bool
            True if the frame has linked proximal frames, False
            otherwise.

        """
        nodes = self._nodes
        if frame in nodes:
            return len(nodes[frame].vertices) > 0
        return False

    def linkedFrames(self, frame):
        """ Get an iterable of linked proximal frames.

        Parameters
        ----------
        frame : QDockFrame
            The frame of interest.

        Returns
        -------
        result : generator
            A generator which yields the linked proximal frames.

        """
        nodes = self._nodes
        if frame in nodes:
            node = nodes[frame]
            vertices = node.vertices
            if len(vertices) > 0:
                tag = object()
                node.tag = tag
                stack = list(vertices)
                while stack:
                    node = stack.pop()
                    if node.tag is tag:
                        continue
                    node.tag = tag
                    yield node.frame
                    stack.extend(node.vertices)

    def updateLinks(self, frame):
        """ Update the proximal linked frames for the given frame.

        Parameters
        ----------
        frame : QDockFrame
            The frame of interest.

        """
        nodes = self._nodes
        if frame in nodes:
            node = nodes[frame]
            node.unlink()
            if frame.isLinked():
                rect = frame.frameGeometry()
                for proximal in self.proximalFrames(rect, 1):
                    if proximal is not frame and proximal.isLinked():
                        node.link(nodes[proximal])

    def proximalFrames(self, rect, distance):
        """ Get an iterable of proximal frames for a gap distance.

        Parameters
        ----------
        rect : QRect
            The rectangle of interest.

        distance : int
            The gap distance to consider a frame proximal. This
            should be greater than or equal to zero.

        Returns
        -------
        result : generator
            A generator which yields the frames in proximity to
            the given rect.

        """
        d = max(0, distance)
        for frame in self._nodes:
            f_rect = frame.frameGeometry().adjusted(-d, -d, d, d)
            if rect.intersects(f_rect):
                yield frame
