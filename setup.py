from setuptools import find_packages, setup

setup(
    name = 'cdd-api',
    version  = '0.1.0',
    description= 'A python wrapper for all CDD Vault API function calls.',
    author = 'Workflow Informatics Corp.',
    author_email = 'chris.lowden@workflowinformatics.com',
    packages = find_packages(include=["cdd"]),
    include_package_data=True,
    install_requires = [
                        'numpy',
                        'gooey',
                        'pandas',
                        'requests'
                        ]
    )
