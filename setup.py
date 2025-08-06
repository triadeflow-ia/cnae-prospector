#!/usr/bin/env python3
"""
Setup script for CNAE Prospector
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="cnae-prospector",
    version="1.0.0",
    author="Alex Campos",
    author_email="alex@cnaeprospector.com",
    description="B2B Lead Generation Tool based on CNAE classification",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alexcampos/cnae-prospector",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "cnae-prospector=src.main:main",
        ],
    },
    keywords="cnae, b2b, leads, prospecting, crm, business",
    project_urls={
        "Bug Reports": "https://github.com/alexcampos/cnae-prospector/issues",
        "Source": "https://github.com/alexcampos/cnae-prospector",
        "Documentation": "https://docs.cnaeprospector.com",
    },
)