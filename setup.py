from setuptools import setup, find_packages

# Function to read requirements.txt
def parse_requirements(filename):
    with open(filename, "r") as file:
        return file.read().splitlines()

setup(
    name="common_python_utils",
    version="0.1.0",
    description="A collection of common Python utilities",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown", 
    author="Martin Brummerstedt", 
    author_email="martinbrummerstedt1@gmail.com",
    url="https://github.com/mbrummerstedt/common_python_utils",
    packages=find_packages(),
    install_requires=parse_requirements("requirements.txt"), 
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    include_package_data=True,
)