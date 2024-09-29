from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='skribble-sdk',
    version='0.4',
    packages=find_packages(),
    install_requires=[
        'requests',
        'pydantic',
    ],
    extras_require={
        'test': [
            'unittest',
            'coverage',
        ],
    },
    author="Eric Campos",
    author_email="ec@webix.ch",
    description="A Python SDK for the Skribble API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LeEricCH/skribble-sdk",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires='>=3.7',
)