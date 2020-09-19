from setuptools import setup, find_packages

setup(
    name="notion2github",
    version="0.1",
    description="A tool to use Notion as a Github Flavored Markdown(aka GFM) editor.",
    author="younho9",
    author_email="younho9.choo@gmail.com",
    url="https://github.com/younho9/notion2github",
    download_url="",
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
