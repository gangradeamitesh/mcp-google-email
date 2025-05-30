from setuptools import setup, find_packages

setup(
    name="mcp-gmail",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "google-auth",
        "google-auth-oauthlib",
        "google-api-python-client",
        "mcp-server",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A Gmail service implementation using MCP",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mcp-gmail",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
) 