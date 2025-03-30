from setuptools import setup, find_packages

setup(
    name="drucom",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "drucom=drucom.main:main",
        ],
    },
    author="Matthieu Scarset",
    author_email="m@matthieuscarset..com",
    description="A Python package for Drucom",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/MatthieuScarset/drucom",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
