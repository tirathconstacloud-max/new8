from setuptools import setup, find_packages

setup(
    name="commercium",
    version="0.0.1",
    description="Commercium ERPNext Integration",
    author="Commercium",
    author_email="help@mycommercium.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=["frappe"]
)