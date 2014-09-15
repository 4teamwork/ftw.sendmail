from setuptools import setup, find_packages
import os

version = '0.6.dev0'


tests_require = [
    'zope.testing',
    'Products.PloneTestCase',
    'Zope2',
    ]


setup(name='ftw.sendmail',
      version=version,
      description='A utility for sending multipart emails in Plone.',
      long_description=open("README.rst").read() + "\n" + \
          open(os.path.join("docs", "HISTORY.txt")).read(),

      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers

      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.1',
        'Framework :: Plone :: 4.2',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

      keywords='ftw sendmail',
      author='4teamwork GmbH',
      author_email='mailto:info@4teamwork.ch',
      url='https://github.com/4teamwork/ftw.sendmail',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw'],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'setuptools',
        'stoneagehtml',
        'Products.CMFPlone',
        'ZODB3',
        'zope.app.pagetemplate',
        'zope.component',
        'zope.interface',
        'zope.sendmail',
        ],

      tests_require=tests_require,
      extras_require=dict(tests=tests_require),

      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
