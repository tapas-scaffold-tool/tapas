from setuptools import setup
from os import path
from encodings import utf_8


project_directory = path.abspath(path.dirname(__file__))


def load_from(file_name):
    with open(path.join(project_directory, file_name), encoding=utf_8.getregentry().name) as f:
        return f.read()


setup(
    name='tapas',
    version=load_from('tapas/tapas.version').strip(),
    url='https://github.com/tapas-scaffold-tool/tapas',
    author='Kirill Sulim',
    author_email='kirillsulim@gmail.com',
    license='MIT',
    description='A simple general purpose scaffold tool',
    long_description=load_from('README.md'),
    long_description_content_type='text/markdown',
    keywords='scaffold build generator generate',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    python_requires='~=3.6',
    install_requires=[
        'click~=7.0',
        'Jinja2~=2.10',
        'gitsnapshot~=0.1.1',
        'appdirs~=1.4.3',
        'PyYAML~=5.1',
        'requests~=2.21.0',
        'GitPython~=3.0.5',
        'lice==0.5',
    ],
    packages=[
        'tapas'
    ],
    package_data={
        'tapas': [
            'tapas.version',
        ]
    },
    entry_points={
        'console_scripts': [
            'tapas=tapas.app:main',
        ],
    },
)
