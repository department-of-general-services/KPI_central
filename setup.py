from distutils.core import setup
from setuptools import find_packages
from os.path import basename, splitext
from glob import glob

setup(
    name="kpicentral",
    version="0.1.1",
    description="The code used to compute FMD's KPIs at the fiscal year level",
    author="James Trimarco",
    author_email="james.trimarco@baltimorecity.gov",
    install_requires=[],
    include_package_data=True,
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
)
