from setuptools import setup, find_packages

setup(
    name="mgp",
    version="0.1.3",
    packages=find_packages(),
    author="Твоё имя",
    description="Простая библиотека, которая говорит Hello, world!",
    python_requires=">=3.6",
    package={
        "mgp": ["mgp"],
    },
    package_data={
        "mgp": ["*.docx"],
    },
    install_requires = [
        "python-docx",
    ],
    include_package_data=True,
)
