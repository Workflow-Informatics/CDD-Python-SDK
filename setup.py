from setuptools import setup

setup(
    name = 'CDD_Python_API',
    version  = '0.1.5',
    description= 'A python wrapper for all CDD Vault API function calls',
    author = 'Workflow Informatics Corp.',
    author_email = 'chris.lowden@workflowinformatics.com',
    packages = ['CDD_Python_API'],
    install_requires = ['numpy','pandas'])
