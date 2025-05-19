from setuptools import setup, find_packages

with open("requirements.txt", "r") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="construction_contract_management",
    version="0.0.1",
    description="ERPNext Custom Application for Construction Contract Management",
    author="Manus",
    author_email="user@example.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires
)
