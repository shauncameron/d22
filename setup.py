import setuptools

PACKAGE_NAME = 'd22'
PACKAGE_VERSION = '0.0.1'
PACKAGE_DESCRIPTION = 'A simple dice roller made with API in mind'

setuptools.setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    author="Shaun Cameron",
    author_email="shauncameron13034@gmail.com",
    description=PACKAGE_DESCRIPTION,
    long_description=open('package/README.md', 'r').read(),
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ], 
    python_requires='>=3.8',
)