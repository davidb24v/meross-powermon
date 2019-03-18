from setuptools import setup, find_packages

setup(name='meross-powermon',
      version='0.1',
      description='Tools for managing local Meross energy monitoring plugs',
      url='http://server/',
      author='Dave Boulton',
      author_email='email addy',
      license='',
      packages=find_packages(),
      install_requires=[
          'meross-iot'
      ],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: ?',
        'License :: ???',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
      ],
      zip_safe=False)
