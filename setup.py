from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="notion2github",
    version="1.0.4",
    description="A tool to use Notion as a Github Flavored Markdown(aka GFM) editor.",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="younho9",
    author_email="younho9.choo@gmail.com",
    url="https://github.com/younho9/notion2github",
    download_url="https://github.com/younho9/notion2github/archive/v1.0.4.tar.gz",
    install_requires=[],
    packages=find_packages(exclude=[]),
    keywords=["notion", "github"],
    python_requires=">=3.5",
    package_data={},
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
