from distutils.core import setup
# Install TX Module
setup(
	name='tx',
	version='1.0',
	description='TxDOT Python Productivity Tools for TPP-GIS',
	author='TPP-GIS',
	author_email='TPP_GIS@txdot.gov',
	url='http://www.txdot.gov/',
	py_modules=['tx'],
	)

# Install Easy GUI Dependency
setup(
    name='easygui',
    version='0.96',
    py_modules=['easygui'],
    )