from setuptools import setup, find_packages
import os

version = '0.5.dev0'
maintainer = 'Mathias Leimgruber'

setup(name='ftw.sendmail',
      version=version,
      description="Maintainer: %s" % maintainer,
      long_description=open("README.rst").read() + "\n" + \
          open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='%s, 4teamworkk GmbH' % maintainer,
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
        'BeautifulSoup'
        # -*- Extra requirements: -*-
        ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = ftw
      """,
      )
