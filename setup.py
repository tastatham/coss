from setuptools import setup, find_packages


def readme():
    with open("README.md") as f:
        return f.read()


install_requires = [
    "statsmodels==0.13.1",
    "geopandas==0.10.2",
    "geobootstrap==0.11",
    "tobler==0.8.2",
    "astropy==5.0.1",
]

extra_require = [
    "matplotlib==3.5.1",
    "seaborn==0.11.2",
    "mapclassify==2.4.3",
]

setup(
    name="coss",
    version="0.12",
    description="Python tools for spatial interpolation",
    long_description=(readme()),
    long_description_content_type="text/markdown",
    url="https://github.com/tastatham/coss",
    author="Thomas Statham",
    author_email="tastatham@gmail.com",
    keywords="spatial, interpolation, support, areal",
    license="MIT",
    packages=find_packages(exclude=["tests"]),
    install_requires=install_requires,
    extra_require=extra_require,
    include_package_data=False,
)
