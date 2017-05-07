#!/usr/bin/env python3

from setuptools import setup

setup(name='nlp-project',
      version='0.1',
      description='Our NLP project for Mooney at UT Austin',
      url='https://github.com/lock14/nlp-project',
      authors='Brian Bechtel, Jonathan Stites',
      license='None',
      packages=['nlp-project'],
      install_requires=[
          "argh",
          "scipy",
          "sklearn"
          ],
      scripts=[
          "bin/predict.py",
          "bin/xml_to_txt.py"
          ]
      zip_safe=False)
