import sys
from setuptools import setup

install_requires = [
    'eyed3', 'pymonad', 'requests', 'elasticsearch>=2.0.0,<3.0.0',
    'configargparse'
]  # 'hew'

if sys.version < '3.0':
    install_requires.append('mock')

setup(name='pyTagger',
      version='0.1',
      description='Python version of my MP3 library management tools',
      url='https://github.com/JeffreyMFarley/pyTagger',
      author='Jeffrey M Farley',
      author_email='JeffreyMFarley@users.noreply.github.com',
      license='MIT',
      packages=['pyTagger'],
      install_requires=install_requires,
      test_suite='tests',
      tests_require=['nose', 'nose_parameterized'],
      zip_safe=False)
