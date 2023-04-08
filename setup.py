# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(
    name="pioreactor_logs2slack",
    version="0.1.2",
    license="MIT",
    description="Push logs generated by Pioreactors to your Slack workspace",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author_email="cam@pioreactor.com",
    author="Cam Davidson Pilon",
    url="https://github.com/Pioreactor/pioreactor-logs2slack",
    packages=find_packages(),
    entry_points={
        "pioreactor.plugins": "pioreactor_logs2slack = pioreactor_logs2slack"
    },
)
