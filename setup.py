from setuptools import setup

setup(
    name = 'CDD-Python-API',
    version  = '0.1.5',
    description= 'A python wrapper for all CDD Vault API function calls',
    author = 'Workflow Informatics Corp.',
    author_email = 'chris.lowden@workflowinformatics.com',
    packages = ['CDD-Python-API'],
    install_requires = ['base64','json','numpy','os','requests','pandas','sys','time','datetime'])
