from setuptools import find_packages
from setuptools import setup


def parse_requirements(filename):
    with open(filename) as requirements_file:
        return requirements_file.readlines()


def get_long_description():
    with open('README.md') as readme_file:
        return readme_file.read()


setup(
    name='jsonapi-requests',
    version='0.7.0',
    description='Python client implementation for json api. http://jsonapi.org/',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    author='Social WiFi',
    author_email='it@socialwifi.com',
    url='https://github.com/socialwifi/jsonapi-requests',
    packages=find_packages(exclude=['tests']),
    install_requires=parse_requirements('base_requirements.txt'),
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'flask'],
    extras_require={
        'flask': ['flask']
    },
    license='BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ]
)
