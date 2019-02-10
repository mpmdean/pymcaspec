from setuptools import setup

setup(name='pymcaspec',
      version='0.1',
      description='Parser for spec file',
      url='http://github.com/mpmdean/pymcaspec',
      author='Mark Dean',
      author_email='mdean@bnl.gov',
      license='MIT',
      py_modules=["six"],
      requires=['numpy', 'matplotlib', 'PyMca5'],
      zip_safe=False)
