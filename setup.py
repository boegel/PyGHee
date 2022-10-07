import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyGHee",
    version="0.0.2",
    author="Kenneth Hoste",
    author_email="kenneth.hoste@ugent.be",
    description="PyGHee (pronounced as 'piggy') is the GitHub Event Executor, a Python library to facilitate creating a GitHub App implemented in Python to process [events from GitHub",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/boegel/pyghee",
    project_urls={
        "Bug Tracker": "https://github.com/boegel/pyghee",
    },
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
    ],
    packages=["pyghee"],
    python_requires=">=3.6",
    install_requires=[
        "Flask",
        "PyGithub",
        "waitress",
   ],
)
