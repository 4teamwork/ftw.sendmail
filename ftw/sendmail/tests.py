import unittest

from zope.testing import doctest
from Testing import ZopeTestCase as ztc

from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
ptc.setupPloneSite()

import ftw.sendmail

class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            ztc.installPackage(ftw.sendmail)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass


def test_suite():
    return unittest.TestSuite([

        doctest.DocTestSuite('ftw.sendmail.composer'),

        ztc.ZopeDocFileSuite(
            'composer.txt',
            test_class=ptc.PloneTestCase,
            ),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
