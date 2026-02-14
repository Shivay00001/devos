"""
DevOS Setup Script
Install DevOS AI-Native Developer Operating Layer
"""

from setuptools import setup, find_packages
import os

# Read README
def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

# Read requirements
def read_requirements():
    requirements = []
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'r') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return requirements

setup(
    name='devos-ai',
    version='0.1.0',
    description='AI-Native Developer Operating Layer',
    long_description=read_file('README.md') if os.path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    author='DevOS Team',
    author_email='team@devos.ai',
    url='https://github.com/devos-ai/devos',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests>=2.31.0',
        'click>=8.1.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
        ]
    },
    entry_points={
        'console_scripts': [
            'devos=ai_engine.core.processor:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    keywords='ai developer tools automation llm devops',
    project_urls={
        'Bug Reports': 'https://github.com/devos-ai/devos/issues',
        'Source': 'https://github.com/devos-ai/devos',
        'Documentation': 'https://docs.devos.ai',
    },
)
