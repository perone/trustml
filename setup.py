from typing import List

import setuptools

development_requires: List[str] = [
    "pytest>=7.4.0",
    "mypy>=1.4.1",
    "flake8>=6.0.0",
    "pytest-cov>=4.1.0",
    "sphinx>=7.0.1",
    "isort>=5.12.0",
    "twine>=4.0.2",
    "sphinx-autobuild>=2021.3.14",
    "furo==2023.5.20",
]

setuptools.setup(
    name="trustml",
    version="0.1.0",
    author="Christian S. Perone",
    author_email="christian.perone@gmail.com",
    description="A trust framework for Machine Learning based on sigstore and transparency.",
    long_description="A trust framework for Machine Learning based on sigstore and transparency.",
    long_description_content_type="text/markdown",
    url="https://github.com/perone/trustml",
    install_requires=[
        "sigstore>=1.1.2",
    ],
    extras_require={
        'dev': development_requires,
    },
    project_urls={
        "Bug Tracker": "https://github.com/perone/trustml/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.8",
    include_package_data=True,
)
