from pip.req import parse_requirements
from setuptools import find_packages
from setuptools import setup


setup(
    name='jsonapi-requests',
    version='0.3.0',
    description='Python client implementation for json api. http://jsonapi.org/',
    author='Jakub Skiepko',
    author_email='it@socialwifi.com',
    url='https://github.com/socialwifi/jsonapi-requests',
    packages=find_packages(exclude=['tests']),
    install_requires=[str(ir.req) for ir in parse_requirements('base_requirements.txt', session=False)],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    license='BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)
