from pip.req import parse_requirements
from setuptools import find_packages
from setuptools import setup


setup(
    name='jsonapi-requests',
    version='0.0.dev0',
    description='Python client implementation for json api. http://jsonapi.org/',
    author='Jakub Skiepko',
    author_email='it@socialwifi.com',
    url='https://github.com/socialwifi/jsonapi-requests',
    packages=['jsonapi_requests'],
    install_requires=[str(ir.req) for ir in parse_requirements('base_requirements.txt', session=False)],
    license='BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ]
)
