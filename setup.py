from setuptools import setup

try:
    import pypandoc
    long_description = pypandoc.convert_file('README.md', 'rst', extra_args=())
except ImportError:
    import codecs
    long_description = codecs.open('README.md', encoding='utf-8').read()

long_description = '\n'.join(long_description.splitlines())

setup(
    name='configurehue',
    description='Configuration management for Hue bridges',
    long_description=long_description,
    version='0.0.1',
    url='https://github.com/Overboard/configurehue',
    author='Overboard',
    author_email='amwroute-git@yahoo.com',
    license='MIT',

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='philips hue config',
    packages=['configurehue'],

    install_requires=['discoverhue'],

    entry_points={
        # 'console_scripts': [
        #     'httpfind = httpfind.httpfind:cli',
        # ],
    }
)
