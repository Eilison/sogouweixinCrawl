# coding: utf-8

from setuptools import setup, find_packages

setup(
    name='sogouweixincrawl',
    version='v1.0.1.dev1',
    author='eilison',
    author_email='1277886419@qq.com',
    url='https://github.com/Eilison/sogouweixinCrawl.git',
    description=u'sogouweixin crawl features',
    license='MIT License',
    packages=find_packages(),
    platforms=["all"],
    install_requires=[
        "lxml",
        "pillow",
        "netcrawl",
        "selenium"
    ]
)