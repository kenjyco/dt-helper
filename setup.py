from setuptools import setup, find_packages


with open('README.rst', 'r') as fp:
    long_description = fp.read()

setup(
    name='dt-helper',
    version='0.0.1',
    description='Helper funcs for doing things with datetime objects and UTC floats',
    long_description=long_description,
    author='Ken',
    author_email='kenjyco@gmail.com',
    license='MIT',
    url='https://github.com/kenjyco/dt-helper',
    download_url='https://github.com/kenjyco/dt-helper/tarball/v0.0.1',
    packages=find_packages(),
    install_requires=[
        'pytz',
        'settings-helper',
    ],
    include_package_data=True,
    package_dir={'': '.'},
    package_data={
        '': ['*.ini'],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries',
        'Intended Audience :: Developers',
    ],
    keywords = ['datetime', 'date', 'time', 'utc', 'helper']
)
