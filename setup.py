
import os
import sys

from setuptools import find_packages, setup

helpDir = os.path.join("cdd", "help_docs")
helpFiles = [os.path.join(helpDir, f) for f in os.listdir(helpDir)]

setup(
    name = 'cdd-api',
    version  = '0.1.0',
    description= 'A python wrapper for all CDD Vault API function calls.',
    author = 'Workflow Informatics Corp.',
    author_email = 'chris.lowden@workflowinformatics.com',
    packages = find_packages(include=["cdd"]),
    include_package_data=True,
    data_files=[("help_docs", helpFiles)],
    install_requires = [
                        'numpy',
                        'gooey',
                        'pandas',
                        'requests'
                        ]
    )
