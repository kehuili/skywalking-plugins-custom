import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='utc-skywalking-plugins',
    version='0.2.0',
    author="Kehui Li",
    author_email="kehui.li@uisee.com",
    description="UISEE Technology Skywalking plugin for python",
    long_description=long_description,
    url="https://gitlab.uisee.ai/cloud/sdk/utc-skywalking-plugins",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],  
    install_requires = ['apache-skywalking'],
)