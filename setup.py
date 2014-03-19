#!/usr/bin/env python
# User: Troy Evans
# Date: 3/19/14
#
# Copyright 2014, Nutrislice Inc.  All rights reserved.
from distutils.core import setup
import django_model_diff


def read_files(*filenames):
    """
    Output the contents of one or more files to a single concatenated string.
    """
    output = []
    for filename in filenames:
        f = open(filename)
        try:
            output.append(f.read())
        finally:
            f.close()
    return '\n\n'.join(output)


setup(
    name='django_model_diff',
    version=django_model_diff.VERSION,
    url='https://github.com/t-evans/django-model-diff.git',
    description='Contains a simple mixin with utility methods for retrieving the differences between two instances of a django Model class.',
    long_description=read_files('README.md'),
    author='Troy Evans',
    author_email='troy@nutrislice.com',
    platforms=['any'],
    packages=[
        'django_model_diff',
    ],
    classifiers=[
        'Development Status :: Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    zip_safe=False,
)
