import pathlib

from setuptools import find_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="porter2",
    version="0.1.1",
    author="Patrick Shechet",
    author_email="patrick.shechet@gmail.com",
    description=("A python wrapper around surgebase's Go implimentation of the Porter2 stemmer"),
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/kajuberdut/porter2",
    license="Apache License 2.0",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Natural Language :: English",
        "Topic :: Text Processing :: Linguistic",
    ],
)
