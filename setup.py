from setuptools import setup, find_packages

setup(
    name = "hotplotter",
    version = "0.0.1",
    author = "Benjamin Huddle",
    description = ("User Agent for Chia Remote Plotting"),
    license = "MIT",
    packages = find_packages(include=["hotplotterclient"]),
    install_requires=["configparser", "requests", "psutil"]

)
