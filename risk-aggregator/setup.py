"""
Setup configuration for Risk Aggregator Service.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="risk-aggregator",
    version="1.0.0",
    author="Fraud Detection Team",
    description="Risk aggregation service for fraud detection system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/fraud-detection",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "risk-aggregator=app.main:main",
        ],
    },
)

