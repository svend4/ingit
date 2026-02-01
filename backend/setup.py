"""
InGit Setup Script
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent.parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="ingit",
    version="0.1.0",
    author="InGit Development Team",
    author_email="dev@ingit.local",
    description="Offline-first система управления версиями, проектами и документацией",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ingit/ingit",
    project_urls={
        "Documentation": "https://ingit.readthedocs.io",
        "Source": "https://github.com/ingit/ingit",
        "Tracker": "https://github.com/ingit/ingit/issues",
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control",
        "Topic :: Software Development :: Project Management",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ingit=ingit.cli.main:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
