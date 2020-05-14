import setuptools

with open("README.md", "r") as fp:
    long = fp.read()

setuptools.setup(
    name="font",
    version="0.1.0",
    author="shark-whale",
    author_email="shark.whale.dev@gmail.com",
    description="Utilities for converting between different font formats.",
    long_description=long,
    long_description_content_type="text/markdown",
    url="https://github.com/shark-whale/font",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
