import re

from setuptools import setup, find_packages

with open("readme.md", "r") as fh:
    long_description = fh.read()

_version_regex = (
    r"^__version__ = ('|\")((?:[0-9]+\.)*[0-9]+(?:\.?([a-z]+)(?:\.?[0-9])?)?)\1$"
)

try:
    with open("alaric/__init__.py") as stream:
        match = re.search(_version_regex, stream.read(), re.MULTILINE)
        version = match.group(2)
except FileNotFoundError:
    version = "0.0.0"


def parse_requirements_file(path):
    with open(path) as fp:
        dependencies = (d.strip() for d in fp.read().split("\n") if d.strip())
        return [d for d in dependencies if not d.startswith("#")]


setup(
    name="alaric",
    version=version,
    author="Skelmis",
    author_email="ethan@koldfusion.xyz",
    description="A simplistic yet powerful asynchronous MongoDB query engine.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={
        "Issue tracker": "https://github.com/Skelmis/Alaric/issues",
        "Documentation": "https://alaric.rtfd.io/",
        "Homepage": "https://github.com/Skelmis/Alaric",
    },
    packages=find_packages(include=("alaric", "alaric.*")),
    install_requires=parse_requirements_file("requirements.txt"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
