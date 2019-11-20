import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='prvd',
    version='0.2.1',
    author='Kyle Thomas',
    author_email='kyle@provide.services',
    description='Provide python client',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/provideservices/provide-python',
    packages=setuptools.find_packages(),
    install_requires=[
        'ipfshttpclient',
        'pyjwt',
        'requests',
    ],
    classifiers=[
    ],
)
