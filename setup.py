from setuptools import setup, find_packages

setup(
    name="mgp",
    version="0.1.0",
    packages=find_packages(),
    author="Твоё имя",
    description="Простая библиотека, которая говорит Hello, world!",
    python_requires=">=3.6",
    package={
        "mgp": ["mgp"],
    },
    package_data={
        "mgp": ["t_oop.txt"],
    },
    include_package_data=True,
)
