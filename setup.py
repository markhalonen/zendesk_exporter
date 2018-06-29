import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="zendesk_exporter",
    version="0.0.1",
    author="Mark Halonen",
    author_email="halonen.mark@gmail.com",
    description="A small zendesk export tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/markhalonen/zendesk_exporter",
    packages=setuptools.find_packages(),
    install_requires=[
        'openpyxl',
        'requests'
    ],
    classifiers=(
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    entry_points = {
        'console_scripts': ['zendesk_exporter=zendesk_expoter.export_tickets:main'],
    }
)