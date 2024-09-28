from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='skribble-sdk',
    version='0.1',
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
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python SDK for the Skribble API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/skribble-sdk",
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