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
        'requests',
        'aiofiles',
        'aiohttp',
        'asyncio'
    ],
    entry_points={
        'console_scripts': [
            # Bash command example: `start-data-parser`
            # Description: Initializes the data parser application.
            'start-data-parser=src.__main__:main',
            
            # Bash command example: `run-data-parser`
            # Description: Executes the data parser application, processing input data based on provided configurations.
            'run-data-parser=src.__main__:main',
            
            # Bash command example: `data-parser-cli`
            # Description: Starts the CLI for user commands, allowing interaction with the data parser application.
            'data-parser-cli=src.__main__:main'
        ],
    }
)