from setuptools import setup, find_packages

setup(
    name = "hotplotter",
    version = "0.0.1",
    author = "Benjamin Huddle",
    description = ("A Client Server for Chai farming"),
    license = "MIT",
    packages = find_packages(include=["hotplotterclient"]),
    install_requires=["configparser", "requests"]

)
