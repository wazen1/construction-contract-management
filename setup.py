from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

# get version from __version__ variable in document_archiver/__init__.py
from document_archiver import __version__ as version

setup(
    name="document_archiver",
    version=version,
    description="Document Archiving App with Scanner Integration for ERPNext",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
