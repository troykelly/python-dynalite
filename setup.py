import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dynalite",
    version="0.0.4",
    author="Troy Kelly",
    author_email="troy@troykelly.com",
    description="An unofficial Dynalite DyNET interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/troykelly/python-dynalite",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
