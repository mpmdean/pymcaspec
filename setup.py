from setuptools import setup

setup(name='pymcaspec',
      version='0.2',
      description='Parser for spec file',
      url='http://github.com/mpmdean/pymcaspec',
      author='Mark Dean',
      author_email='mdean@bnl.gov',
      packages=['pymcaspec'],
      license='MIT',
      requires=['numpy', 'matplotlib', 'PyMca5'],
      zip_safe=False)
