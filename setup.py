import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="friends",
    version="0.0.1",
    author="barthelemy",
    author_email="barthelemy@adaltas.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bngom/azure-databricks-cicd",
    project_urls={
        "Bug Tracker": "https://github.com/bngom/azure-databricks-cicd/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=['.friends'],
    #package_dir={"": "src"},
    #packages=setuptools.find_packages(where="src"),
    #python_requires=">=3.6",
)