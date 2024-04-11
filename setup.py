import setuptools

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setuptools.setup(
    name="data-parser",
    version="0.0.1",
    author="Your Name",
    author_email="your@email.com",
    description="A data parsing utility for LLM training data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'beautifulsoup4',
        'transformers',
        'huggingface-hub',
        'python-logging',
    ],
    entry_points={
        'console_scripts': [
            'data-parser=src.__main__:main',
        ],
    },
)