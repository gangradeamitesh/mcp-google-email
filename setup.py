from setuptools import setup, find_packages

setup(
    name="mcp-google-email",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "google-auth",
        "google-auth-oauthlib",
        "google-api-python-client",
        "mcp-server",
    ],
    author="Amitesh Gangrade",
    author_email="gangradeamitesh@gmail.com",
    description="MCP for GMail",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mcp-gmail",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
) 