from setuptools import setup, find_packages

setup(name='tv_server',
      version='0.2.0',
      description="A API-controlled TV tuner management library.",
      long_description="",
      classifiers=[],
      keywords='tv tuner',
      author='Dustin Oprea',
      author_email='myselfasunder@gmail.com',
      url='https://github.com/dsoprea/tvserver',
      license='GPL 2',
      packages=find_packages(exclude=['dev']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
            'protobuf==2.5.0',
            'pyzap==0.3.0',
            'web.py==0.37',
      ],
      scripts=[
            'tv_server/resources/scripts/tv_start_backend',
            'tv_server/resources/scripts/tv_start_webserver',
      ],
)
