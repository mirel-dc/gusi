from setuptools import setup, find_packages

setup(
    name="mgp",
    version="0.1.6",
    packages=find_packages(),
    author="Твоё имя",
    description="Сборник мегагигаприколов",
    python_requires=">=3.6",
    package={
        "mgp": ["mgp"],
    },
    package_data={
        "mgp": ["*.docx"],
    },
    install_requires = [
        "python-docx",
        "requests"
    ],
    include_package_data=True,
)
