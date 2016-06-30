from setuptools import setup

setup(name='Tankstelle',
      version='0.1',
      description='',
      author='M. Zahraee',
      url='http://www.python.org/sigs/distutils-sig/',
      install_requires=['Flask',
                        'Flask-Bootstrap',
                        'Flask-PyMongo',
                        'requests',
                        ],
      setup_requires=['pytest-runner'],
      tests_require=['pytest'])
