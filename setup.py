from setuptools import setup, find_packages

setup(
    name="log_file_correlation_engine",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "log-correlate = log_file_correlation_engine.main:main",
        ],
    },
    install_requires=[
        "PyYAML>=6.0.1",
    ],
)
