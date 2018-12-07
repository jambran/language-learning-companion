# Natural Language Toolkit: Text Trees
#
# Copyright (C) 2001-2005 University of Pennsylvania
# Author: Edward Loper <edloper@gradient.cis.upenn.edu>
#         Steven Bird <sb@csse.unimelb.edu.au>
# URL: <http://nltk.sf.net>
# For license information, see LICENSE.TXT

"""
Class for representing hierarchical language structures, such as
syntax trees and morphological trees.
"""

import re, types

######################################################################
## Trees
######################################################################

class Tree(list):
    """
    A hierarchical structure.

    Each C{Tree} represents a single hierarchical grouping of
    leaves and subtrees.  For example, each constituent in a syntax
    tree is represented by a single C{Tree}.

    A tree's children are encoded as a C{list} of leaves and subtrees,
    where a X{leaf} is a basic (non-tree) value; and a X{subtree} is a
    nested C{Tree}.

    Any other properties that a C{Tree} defines are known as
    X{node properties}, and are used to add information about
    individual hierarchical groupings.  For example, syntax trees use a
    NODE property to label syntactic constituents with phrase tags,
    such as \"NP\" and\"VP\".

    Several C{Tree} methods use X{tree positions} to specify
    children or descendants of a tree.  Tree positions are defined as
    follows:

      - The tree position M{i} specifies a C{Tree}'s M{i}th child.
      - The tree position C{()} specifies the C{Tree} itself.
      - If C{M{p}} is the tree position of descendant M{d}, then
        C{M{p}+(M{i})} specifies the C{M{i}}th child of M{d}.
    
    I.e., every tree position is either a single index C{M{i}},
    specifying C{self[M{i}]}; or a sequence C{(M{i1}, M{i2}, ...,
    M{iN})}, specifying
    C{self[M{i1}][M{i2}]...[M{iN}]}.
    """
    def __init__(self, node, children):
        """
        Construct a new tree.
        """
        if isinstance(children, str):
            raise TypeError('children should be a list, not a string')
        list.__init__(self, children)
        self.node = node

    #////////////////////////////////////////////////////////////
    # Comparison operators
    #////////////////////////////////////////////////////////////

    def __cmp__(self, other):
        c = cmp(self.node, other.node)
        if c != 0: return c
        else: return list.__cmp__(self, other)
    def __eq__(self, other):
        if other == None: return False
        return self.node == other.node and list.__eq__(self, other)
    def __ne__(self, other):
        return not (self == other)
    def __lt__(self, other):
        return cmp(self, other) < 0
    def __le__(self, other):
        return cmp(self, other) <= 0
    def __gt__(self, other):
        return cmp(self, other) > 0
    def __ge__(self, other):
        return cmp(self, other) >= 0
    
    #////////////////////////////////////////////////////////////
    # Disabled list operations
    #////////////////////////////////////////////////////////////

    def __mul__(self, v):
        raise TypeError('Tree does not support multiplication')
    def __rmul__(self, v):
        raise TypeError('Tree does not support multiplication')
    def __add__(self, v):
        raise TypeError('Tree does not support addition')
    def __radd__(self, v):
        raise TypeError('Tree does not support addition')

    #////////////////////////////////////////////////////////////
    # Indexing (with support for tree positions)
    #////////////////////////////////////////////////////////////

    def __getitem__(self, index):
        if isinstance(index, int):
            return list.__getitem__(self, index)
        else:
            if len(index) == 0:
                return self
            elif len(index) == 1:
                return self[int(index[0])]
            else:
                return self[int(index[0])][index[1:]]
    
    def __setitem__(self, index, value):
        if isinstance(index, int):
            return list.__setitem__(self, index, value)
        else:
            if len(index) == 0:
                raise IndexError('The tree position () may not be '
                                 'assigned to.')
            elif len(index) == 1:
                self[index[0]] = value
            else:
                self[index[0]][index[1:]] = value
    
    def __detitem__(self, index):
        if isinstance(index, int):
            return list.__delitem__(self, index)
        else:
            if len(index) == 0:
                raise IndexError('The tree position () may not be deleted.')
            elif len(index) == 1:
                del self[index[0]]
            else:
                del self[index[0]][index[1:]]
    
    #////////////////////////////////////////////////////////////
    # Basic tree operations
    #////////////////////////////////////////////////////////////

    def leaves(self):
        """
        @return: a list containing this tree's leaves.  The
            order of leaves in the tuple reflects the order of the
            leaves in the tree's hierarchical structure.
        @rtype: C{list}
        """
        leaves = []
        for child in self:
            if isinstance(child, Tree):
                leaves.extend(child.leaves())
            else:
                leaves.append(child)
        return leaves

    def preterminals(self):
        preterms = []
        for child in self:
            if child.height() > 2:
                preterms.extend(child.preterminals())
            else:
                preterms.append(child.node)
        return preterms
    

    def height(self):
        """
        @return: The height of this tree.  The height of a tree
            containing no children is 1; the height of a tree
            containing only leaves is 2; and the height of any other
            tree is one plus the maximum of its children's
            heights.
        @rtype: C{int}
        """
        max_child_height = 0
        for child in self:
            if isinstance(child, Tree):
                max_child_height = max(max_child_height, child.height())
            else:
                max_child_height = max(max_child_height, 1)
        return 1 + max_child_height

    def treepositions(self, order='preorder'):
        """
        @param order: One of: C{preorder}, C{postorder}, C{bothorder},
            C{leaves}.
        """
        positions = []
        if order in ('preorder', 'bothorder'): positions.append( () )
        for i, child in enumerate(self):
            if isinstance(child, Tree):
                childpos = child.treepositions(order)
                positions.extend([(i,)+p for p in childpos])
            else:
                positions.append( (i,) )
        if order in ('postorder', 'bothorder'): positions.append( () )
        return positions

    def subtrees(self, filter=None):
        """
        Generate all the subtrees of this tree, optionally restricted
        to trees matching the filter function.
        @type: filter: C{function}
        @param: filter: the function to filter all local trees
        """
        if not filter or filter(self):
            yield self
        for child in self:
            if isinstance(child, Tree):
                for subtree in child.subtrees(filter):
                    yield subtree

    #////////////////////////////////////////////////////////////
    # Convert, copy
    #////////////////////////////////////////////////////////////

    # [classmethod]
    def convert(cls, val):
        """
        Convert a tree between different types.  C{cls} determines
        which class will be used to encode the new tree.  E.g.:

           >>> # Convert tree into a Tree:
           >>> tree = Tree.convert(tree)
           >>> # Convert tree into a ParentedTree:
           >>> tree = ParentedTree.convert(tree)
           >>> # Convert tree into a MultiParentedTree:
           >>> tree = MultiParentedTree.convert(tree)

        @type val: L{Tree}
        @param val: The tree that should be converted.
        @return: The new C{Tree}.
        """
        if isinstance(val, Tree):
            children = [cls.convert(child) for child in val]
            return cls(val.node, children)
        else:
            return val
    convert = classmethod(convert)

    def copy(self, deep=False):
        if not deep: return self.__class__(self.node, self)
        else: return self.__class__.convert(self)

    def _frozen_class(self): return ImmutableTree
    def freeze(self, leaf_freezer=None):
        frozen_class = self._frozen_class()
        if leaf_freezer is None:
            newcopy = frozen_class.convert(self)
        else:
            newcopy = self.copy(deep=True)
            for pos in newcopy.treepositions('leaves'):
                newcopy[pos] = leaf_freezer(newcopy[pos])
            newcopy = frozen_class.convert(newcopy)
        hash(newcopy) # Make sure the leaves are hashable.
        return newcopy

    #////////////////////////////////////////////////////////////
    # Visualization & String Representation
    #////////////////////////////////////////////////////////////

    def __repr__(self):
        childstr = ' '.join([repr(c) for c in self])
        return '(%s: %s)' % (self.node, childstr)

    def __str__(self):
        return self.pp()

    def _ppflat(self, nodesep, parens):
        childstrs = []
        for child in self:
            if isinstance(child, Tree):
                childstrs.append(child._ppflat(nodesep, parens))
            else:
                childstrs.append('%s' % child.__repr__())
        return '%s%s%s %s%s' % (parens[0], self.node, nodesep, 
                                ' '.join(childstrs), parens[1])

    def pp(self, margin=70, indent=0, nodesep=':', parens='()'):
        """
        @return: A pretty-printed string representation of this tree.
        @rtype: C{string}
        @param margin: The right margin at which to do line-wrapping.
        @type margin: C{int}
        @param indent: The indentation level at which printing
            begins.  This number is used to decide how far to indent
            subsequent lines.
        @type indent: C{int}
        @param nodesep: A string that is used to separate the node
            from the children.  E.g., the default value C{':'} gives
            trees like C{(S: (NP: I) (VP: (V: saw) (NP: it)))}.
        """

        # Try writing it on one line.
        s = self._ppflat(nodesep, parens)
        if len(s)+indent < margin:
            return s

        # If it doesn't fit on one line, then write it on multi-lines.
        s = '%s%s%s' % (parens[0], self.node, nodesep)
        for child in self:
            if isinstance(child, Tree):
                s += '\n'+' '*(indent+2)+child.pp(margin, indent+2,
                                                  nodesep, parens)
            else:
                s += '\n'+' '*(indent+2)+repr(child)
        return s+parens[1]

    def pp_treebank(self, margin=70, indent=0):
        return self.pp(margin, indent, '')

    def pp_latex_qtree(self):
        r"""
        Returns a representation of the tree compatible with the
        LaTeX qtree package. This consists of the string C{\Tree}
        followed by the parse tree represented in bracketed notation.

        For example, the following result was generated from a parse tree of
        the sentence C{The announcement astounded us}::

          \Tree [.I'' [.N'' [.D The ] [.N' [.N announcement ] ] ]
              [.I' [.V'' [.V' [.V astounded ] [.N'' [.N' [.N us ] ] ] ] ] ] ]

        See U{http://www.ling.upenn.edu/advice/latex.html} for the LaTeX
        style file for the qtree package.

        @return: A latex qtree representation of this tree.
        @rtype: C{string}
        """
        return r'\Tree ' + self.pp(indent=6, nodesep='', parens=('[.', ' ]'))
    

def bracket_parse(s):
    """
    Parse a treebank string and return a tree.  Trees are represented
    as nested brackettings, e.g. (S (NP (NNP John)) (VP (V runs))).

    @return: A tree corresponding to the string representation.
    @rtype: C{tree}
    @param s: The string to be converted
    @type s: C{string}
    """

    SPACE = re.compile(r'\s*')
    WORD = re.compile(r'\s*([^\s\(\)]*)\s*')

    # Skip any initial whitespace.
    pos = SPACE.match(s).end()

    stack = []
    while pos < len(s):
        # Beginning of a tree/subtree.
        if s[pos] == '(':
            match = WORD.match(s, pos+1)
            stack.append(Tree(match.group(1), []))
            pos = match.end()

        # End of a tree/subtree.
        elif s[pos] == ')':
            pos = SPACE.match(s, pos+1).end()
            if len(stack) == 1:
                if pos != len(s): raise ValueError
                tree = stack[0]
                # If the tree has an extra level with node='', then get
                # rid of it.  (E.g., "((S (NP ...) (VP ...)))")
                if tree.node == '':
                    tree = tree[0]
                else:
                    return tree
            stack[-2].append(stack[-1])
            stack.pop()

        # Leaf token.
        else:
            match = WORD.match(s, pos)
            leaf = match.group(1)
            stack[-1].append(leaf)
            pos = match.end()

    raise ValueError('mismatched parens')

def evaluate(trueTree, predTree):
    def getSpanLabels(tree, leftPos, all):
        if tree is None: return leftPos
        
        if type(tree) is str:
            all[ (leftPos, leftPos+1, tree) ] = 1
            return leftPos+1
        else:
            rightPos = leftPos
            for i,child in enumerate(tree):
                rightPos = getSpanLabels(child, rightPos, all)
            all[ (leftPos, rightPos, tree.node) ] = 1
            return rightPos

    trueSpans = {}
    getSpanLabels(trueTree, 0, trueSpans)

    predSpans = {}
    getSpanLabels(predTree, 0, predSpans)

    numCorrect = 0.0
    for span in predSpans:
        if trueSpans.has_key(span):
            numCorrect += 1.0

    if numCorrect <= 0.: return 0.
    return numCorrect / len(trueSpans)
    
