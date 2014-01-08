""" Metaclass and class for validating instance APIs
"""
from __future__ import division, print_function, absolute_import

from ..externals.six import with_metaclass

from nose.tools import assert_equal


class validator2test(type):
    """ Wrap ``validator_*`` methods with test method testing instances

    * Find methods with names starting with 'validate_'
    * Create test method with same name
    * Test method iterates, running validate method over all obj, param pairs
    """
    def __new__(mcs, name, bases, dict):
        klass = type.__new__(mcs, name, bases, dict)
        def make_test(name, validator):
            def meth(self):
                for imaker, params in self.obj_params():
                    validator(self, imaker, params)
            meth.__name__ = 'test_' + name[len('validate_'):]
            meth.__doc__ = 'autogenerated test from ' + name
            return meth
        for name in dir(klass):
            if not name.startswith('validate_'):
                continue
            # Assume this is a validation method; make a test
            test_meth = make_test(name, getattr(klass, name))
            setattr(klass, test_meth.__name__, test_meth)
        return klass



class ValidateAPI(with_metaclass(validator2test)):
    """ A class to validate APIs

    Your job is twofold:

    * define an ``obj_params`` iteratable, where the iterator returns (``obj``,
      ``params``) pairs.  ``obj`` is something that you want to validate against
      an API.  ``params`` is a mapping giving parameters for this object to test
      against.
    * define ``validate_xxx`` methods, that accept ``obj`` and
      ``params`` as arguments, and check ``obj`` against ``params``

    The metaclass finds each ``validate_xxx`` method and makes a new
    ``test_xxx`` method that calls ``validate_xxx`` for each (``obj``,
    ``params``) pair returned from ``obj_params``

    See :class:`TextValidateSomething` for an example
    """
    pass


class TestValidateSomething(ValidateAPI):
    """ Example implementing an API validator test class """

    def obj_params(self):
        """ Iterator returning (obj, params) pairs

        ``obj`` is some instance for which we want to check the API.

        ``params`` is a mapping with parameters that you are going to check
        against ``obj``.  See the :meth:`validate_something` method for an
        example.
        """
        class C(object):
            def __init__(self, var):
                self.var = var

            def get_var(self):
                return self.var

        yield C(5), {'var': 5}
        yield C('easypeasy'), {'var': 'easypeasy'}


    def validate_something(self, obj, params):
        """ Do some checks of the `obj` API against `params`

        The metaclass sets up a ``test_something`` function that runs these
        checks on each (
        """
        assert_equal(obj.var, params['var'])
        assert_equal(obj.get_var(), params['var'])


class TestRunAllTests(ValidateAPI):
    """ Class to test that each validator test gets run

    We check this in the module teardown function
    """
    run_tests = []

    def obj_params(self):
        yield 1, 2

    def validate_first(self, obj, param):
        self.run_tests.append('first')

    def validate_second(self, obj, param):
        self.run_tests.append('second')


def teardown():
    # Check that both validate_xxx tests got run
    assert_equal(TestRunAllTests.run_tests, ['first', 'second'])
