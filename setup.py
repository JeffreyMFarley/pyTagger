from setuptools import setup

setup(name='pyTagger',
      version='0.1',
      description='Python version of my MP3 library management tools',
      url='https://github.com/JeffreyMFarley/pyTagger',
      author='Jeffrey M Farley',
      author_email='JeffreyMFarley@users.noreply.github.com',
      license='MIT',
      packages=['pyTagger'],
      install_requires=['eyed3', 'pymonad', 'requests'],  # 'hew'
      test_suite='tests',
      zip_safe=False)
