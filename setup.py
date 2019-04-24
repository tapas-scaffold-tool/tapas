from setuptools import setup


setup(
    name='tapas',
    version='0.1.0',
    description='A simple general purpose scaffold tool',
    url='https://github.com/tapas-scaffold-tool/tapas',
    author='Kirill Sulim',
    author_email='kirillsulim@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='scaffold build generator generate',
    python_requires='>=3',
    install_requires=[
        'click>=6.7',
        'Jinja2>=2.10',
        'gitsnapshot>=0.1.0',
        'appdirs',
        'pyyaml',
    ],
    packages=[
        'tapas'
    ],
    entry_points={
        'console_scripts': [
            'tapas=tapas.app:main',
        ],
    },
)
