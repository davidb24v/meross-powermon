from setuptools import setup, find_packages

from meross_powermon.version import VERSION

setup(name='meross-powermon',
      version=VERSION,
      description='Tools for managing local Meross energy monitoring plugs',
      url='http://server/',
      author='Dave Boulton',
      author_email='email addy',
      license='',
      packages=find_packages(),
      install_requires=[
          'meross-iot',
          'argcomplete'
      ],
      scripts=["meross"],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: ?',
        'License :: ???',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
      ],
      zip_safe=False)
