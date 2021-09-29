from veeam_exporter_src.veeam_exporter.constants import (PKG_NAME, PKG_VERSION)
from setuptools import setup, find_packages

# Global variables
name = PKG_NAME
version = PKG_VERSION

setup(
    name=PKG_NAME,
    version=PKG_VERSION,
    description='A Python-based Veeam Entreprise Exporter for Prometheus',
    long_description_content_type='text/markdown',
    long_description=open('README.md', 'r').read(),
    author="peekjef72",
    author_email="jfpik78@gmail.com",
    url="https://github.com/peekjef72/veeam_exporter",
    entry_points={
        'console_scripts': [
            'veeam_exporter = veeam_exporter.veeam_exporter:main',
            'build_veeam_exporter_conf = veeam_exporter.build_conf:main'
        ]
    },
    package_dir={"": "veeam_exporter_src"},
    packages=find_packages(where="veeam_exporter_src"),
    install_requires=open('./pip_requirements.txt').readlines(),

    package_data={
	"veeam_exporter": ["conf/*.yml", "conf/metrics/*.yml"],
    },
)

