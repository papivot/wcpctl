import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='wcpctl',
    version='0.1.0',    
    description='A kubectl-like program for interacting with Tanzu vSphere 7.x',
    long_description=long_description,
    url='https://github.com/papivot/wcpctl',
    author='Navneet Verma',
    # author_email='shudson@anl.gov',
    # license='BSD 2-clause',
    install_requires=['argparse','requests','pysocks','PyYAML','jsonpatch==1.16','jsonpointer==1.10','jsonschema>=3.0.1'],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.9'
    ],
    python_requires=">=3.6",
    scripts=["src/wcpctl"]
)