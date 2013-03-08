#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from collections import defaultdict
import operator


STRENGTHS = set(['required', 'strong', 'medium', 'weak'])


def almost_equal(a, b, eps=1e-8):
    return abs(a - b) < eps


class LinearSymbolic(object):

    __slots__ = ()

    def nonlinear(self, msg):
        raise TypeError('Non-linear expression: %s' % msg)

    def nonlinear_op(self, op):
        raise TypeError('Non-linear operator: `%s`' % op)

    def as_dict(self):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError

    def __add__(self, other):
        raise NotImplementedError

    def __mul__(self, other):
        raise NotImplementedError

    def __div__(self, other):
        raise NotImplementedError

    def __str__(self):
        return self.__repr__()

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self + (-1.0 * other)

    def __rsub__(self, other):
        return other + (-1.0 * self)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __rdiv__(self, other):
        self.nonlinear_op('/')

    def __floordiv__(self, other):
        self.nonlinear_op('//')

    def __rfloordiv__(self, other):
        self.nonlinear_op('//')

    def __mod__(self, other):
        self.nonlinear_op('%')

    def __divmod__(self, other):
        self.nonlinear_op('divmod')

    def __rdivmod__(self, other):
        self.nonlinear_op('divmod')

    def __pow__(self, other, mod):
        self.nonlinear_op('**')

    def __rpow__(self, other, mod):
        self.nonlinear_op('**')

    def __lshift__(self, other):
        self.nonlinear_op('<<')

    def __rlshift__(self, other):
        self.nonlinear_op('<<')

    def __rshift__(self, other):
        self.nonlinear_op('>>')

    def __rrshift__(self, other):
        self.nonlinear_op('>>')

    def __and__(self, other):
        self.nonlinear_op('&')

    def __rand__(self, other):
        self.nonlinear_op('&')

    def __or__(self, other):
        self.nonlinear_op('|')

    def __ror__(self, other):
        self.nonlinear_op('|')

    def __xor__(self, other):
        self.nonlinear_op('^')

    def __rxor__(self, other):
        self.nonlinear_op('^')

    def __eq__(self, other):
        if isinstance(other, (float, int, long)):
            rhs = LinearExpression([], float(other))
        elif isinstance(other, LinearSymbolic):
            rhs = other
        else:
            msg = 'Invalid type for constraint operation %s' % type(other)
            raise TypeError(msg)
        return EQConstraint(self, rhs)

    def __le__(self, other):
        if isinstance(other, (float, int, long)):
            rhs = LinearExpression([], float(other))
        elif isinstance(other, LinearSymbolic):
            rhs = other
        else:
            msg = 'Invalid type for constraint operation %s' % type(other)
            raise TypeError(msg)
        return LEConstraint(self, rhs)

    def __ge__(self, other):
        if isinstance(other, (float, int, long)):
            rhs = LinearExpression([], float(other))
        elif isinstance(other, LinearSymbolic):
            rhs = other
        else:
            msg = 'Invalid type for constraint operation %s' % type(other)
            raise TypeError(msg)
        return GEConstraint(self, rhs)

    def __ne__(self, other):
        raise ValueError('Invalid constraint operation.')

    def __lt__(self, other):
        raise ValueError('Invalid constraint operation.')

    def __gt__(self, other):
        raise ValueError('Invalid constraint operation.')


class ConstraintVariable(LinearSymbolic):

    __slots__ = ('name', 'owner')

    def __init__(self, name, owner):
        self.name = name
        self.owner = owner

    def as_dict(self):
        dct = {
            'type': 'linear_symbolic',
            'name': self.name,
            'owner': self.owner,
        }
        return dct

    def __repr__(self):
        template = 'ConstraintVariable({0!r}, {1!r})'
        return template.format(self.name, self.owner)

    def __str__(self):
        template = '{0}:{1}'
        return template.format(self.name, self.owner)

    def __add__(self, other):
        if not isinstance(self, LinearSymbolic):
            self, other = other, self
        if isinstance(other, (float, int, long)):
            terms = [Term(self)]
            const = float(other)
            expr = LinearExpression(terms, const)
        elif isinstance(other, Term):
            terms = [Term(self), other]
            expr = LinearExpression(terms)
        elif isinstance(other, ConstraintVariable):
            terms = [Term(self), Term(other)]
            expr = LinearExpression(terms)
        elif isinstance(other, LinearExpression):
            expr = other + self
        else:
            return NotImplemented
        return expr

    def __mul__(self, other):
        if not isinstance(self, LinearSymbolic):
            self, other = other, self
        if isinstance(other, (float, int, long)):
            res = Term(self, float(other))
        elif isinstance(other, (Term, ConstraintVariable, LinearExpression)):
            self.nonlinear('[ %s ] * [ %s ]' % (self, other))
        else:
            return NotImplemented
        return res

    def __div__(self, other):
        if not isinstance(self, LinearSymbolic):
            other.nonlinear('[ %s ] / [ %s ]' % (self, other))
        if isinstance(other, (float, int)):
            res = (1.0 / float(other)) * self
        elif isinstance(other, (Term, ConstraintVariable, LinearExpression)):
            self.nonlinear('[ %s ] / [ %s ]' % (self, other))
        else:
            return NotImplemented
        return res


class Term(LinearSymbolic):

    __slots__ = ('var', 'coeff')

    def __init__(self, var, coeff=1.0):
        self.var = var
        self.coeff = coeff

    def as_dict(self):
        dct = {
            'type': 'term',
            'var': self.var.as_dict(),
            'coeff': self.coeff,
        }
        return dct

    def __repr__(self):
        template = 'Term({0!r}, {1!r})'
        return template.format(self.var, self.coeff)

    def __str__(self):
        if self.coeff == 1.0:
            template = '{name}'
        elif self.coeff == -1.0:
            template = '-{name}'
        else:
            template = '{coeff} * {name}'
        kwargs = {
            'coeff': self.coeff,
            'name': self.var.name,
        }
        return template.format(**kwargs)

    def __add__(self, other):
        if not isinstance(self, LinearSymbolic):
            self, other = other, self
        if isinstance(other, (float, int, long)):
            terms = [self]
            const = float(other)
            expr = LinearExpression(terms, const)
        elif isinstance(other, Term):
            terms = [self, other]
            expr = LinearExpression(terms)
        elif isinstance(other, ConstraintVariable):
            terms = [self, Term(other)]
            expr = LinearExpression(terms)
        elif isinstance(other, LinearExpression):
            expr = other + self
        else:
            return NotImplemented
        return expr

    def __mul__(self, other):
        if not isinstance(self, LinearSymbolic):
            self, other = other, self
        if isinstance(other, (float, int, long)):
            res = Term(self.var, float(other) * self.coeff)
        elif isinstance(other, (Term, ConstraintVariable, LinearExpression)):
            self.nonlinear('[ %s ] * [ %s ]' % (self, other))
        else:
            return NotImplemented
        return res

    def __div__(self, other):
        if not isinstance(self, LinearSymbolic):
            other.nonlinear('[ %s ] / [ %s ]' % (self, other))
        if isinstance(other, (float, int, long)):
            res = (1.0 / float(other)) * self
        elif isinstance(other, (Term, ConstraintVariable, LinearExpression)):
            self.nonlinear('[ %s ] / [ %s ]' % (self, other))
        else:
            return NotImplemented
        return res


class LinearExpression(LinearSymbolic):

    __slots__ = ('terms', 'constant')

    @staticmethod
    def reduce_terms(terms):
        mapping = defaultdict(float)
        for term in terms:
            mapping[term.var] += term.coeff
        terms = tuple(
            Term(var, coeff) for (var, coeff) in mapping.iteritems()
            if not almost_equal(coeff, 0.0)
        )
        return terms

    def __init__(self, terms, constant=0.0):
        self.terms = self.reduce_terms(terms)
        self.constant = constant

    def as_dict(self):
        dct = {
            'type': 'linear_expression',
            'terms': [term.as_dict() for term in self.terms],
            'constant': self.constant,
        }
        return dct

    def __repr__(self):
        if len(self.terms) > 0:
            s = sorted(self.terms, key=operator.attrgetter('var.name'))
            terms = ' + '.join(str(term) for term in s)
            if self.constant > 0.0:
                terms += ' + %s' % self.constant
            elif self.constant < 0.0:
                terms += ' - %s' % -self.constant
        else:
            terms = str(self.constant)
        return terms

    def __add__(self, other):
        if not isinstance(self, LinearSymbolic):
            self, other = other, self
        if isinstance(other, (float, int, long)):
            expr = LinearExpression(self.terms, self.constant + float(other))
        elif isinstance(other, Term):
            terms = list(self.terms) + [other]
            expr = LinearExpression(terms, self.constant)
        elif isinstance(other, ConstraintVariable):
            terms = list(self.terms) + [Term(other)]
            expr = LinearExpression(terms, self.constant)
        elif isinstance(other, LinearExpression):
            terms = list(self.terms) + list(other.terms)
            const = self.constant + other.constant
            expr = LinearExpression(terms, const)
        else:
            return NotImplemented
        return expr

    def __mul__(self, other):
        if not isinstance(self, LinearSymbolic):
            self, other = other, self
        if isinstance(other, (float, int, long)):
            terms = [other * term for term in self.terms]
            const = self.constant * other
            res = LinearExpression(terms, const)
        elif isinstance(other, (Term, ConstraintVariable, LinearExpression)):
            self.nonlinear('[ %s ] * [ %s ]' % (self, other))
        else:
            return NotImplemented
        return res

    def __div__(self, other):
        if not isinstance(self, LinearSymbolic):
            self, other = other, self
        if isinstance(other, (float, int, long)):
            res = (1.0 / float(other)) * self
        elif isinstance(other, (Term, ConstraintVariable, LinearExpression)):
            self.nonlinear('[ %s ] / [ %s ]' % (self, other))
        else:
            return NotImplemented
        return res


class LinearConstraint(object):

    __slots__ = ('lhs', 'rhs', 'strength', 'weight', 'op')

    def __init__(self, lhs, rhs, strength='required', weight=1.0):
        self.lhs = lhs
        self.rhs = rhs
        self.strength = strength
        self.weight = weight
        self.op = None

    def as_dict(self):
        dct = {
            'type': 'linear_constraint',
            'lhs': self.lhs.as_dict(),
            'op': self.op,
            'rhs': self.rhs.as_dict(),
            'strength': self.strength,
            'weight': self.weight,
        }
        return dct

    def __repr__(self):
        template = '<{name}: ({lhs} {op} {rhs}) | {strength} | {weight}>'
        kwargs = {
            'name': type(self).__name__,
            'lhs': self.lhs,
            'rhs': self.rhs,
            'op': self.op,
            'strength': self.strength,
            'weight': self.weight,
        }
        return template.format(**kwargs)

    def __str__(self):
        template = '{lhs} {op} {rhs}'
        kwargs = {
            'lhs': self.lhs,
            'rhs': self.rhs,
            'op': self.op,
        }
        return template.format(**kwargs)

    def __or__(self, other):
        strength = self.strength
        weight = self.weight
        if isinstance(other, (float, int, long)):
            weight = other
        elif isinstance(other, basestring):
            if other not in STRENGTHS:
                msg = 'Expected a known strength string. '
                msg +=  'Got {!r} instead.'
                raise ValueError(msg.format(other))
            else:
                strength = other
        else:
            msg = 'Expected a known strength string or a float weight. '
            msg += 'Got {!r} instead.'
            raise ValueError(msg.format(other))
        return type(self)(self.lhs, self.rhs, strength, weight)

    def __ror__(self, other):
        return self.__or__(other)

    def __hash__(self):
        return object.__hash__(self)


class LEConstraint(LinearConstraint):

    __slots__ = ()

    def __init__(self, lhs, rhs, strength='required', weight=1.0):
        super(LEConstraint, self).__init__(lhs, rhs, strength, weight)
        self.op = '<='


class GEConstraint(LinearConstraint):

    __slots__ = ()

    def __init__(self, lhs, rhs, strength='required', weight=1.0):
        super(GEConstraint, self).__init__(lhs, rhs, strength, weight)
        self.op = b'>='


class EQConstraint(LinearConstraint):

    __slots__ = ()

    def __init__(self, lhs, rhs, strength='required', weight=1.0):
        super(EQConstraint, self).__init__(lhs, rhs, strength, weight)
        self.op = b'=='

