#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Apache Beam SDK for Python setup file."""

from __future__ import print_function

import os
import platform
import warnings
from distutils.version import StrictVersion

# Pylint and isort disagree here.
# pylint: disable=ungrouped-imports
import setuptools
from pkg_resources import DistributionNotFound
from pkg_resources import get_distribution
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info
from setuptools.command.sdist import sdist
from setuptools.command.test import test


def get_version():
  global_names = {}
  exec(open(os.path.normpath('./apache_beam/version.py')).read(), global_names)  # pylint: disable=exec-used
  return global_names['__version__']


PACKAGE_NAME = 'apache-beam'
PACKAGE_VERSION = get_version()
PACKAGE_DESCRIPTION = 'Apache Beam SDK for Python'
PACKAGE_URL = 'https://beam.apache.org'
PACKAGE_DOWNLOAD_URL = 'https://pypi.python.org/pypi/apache-beam'
PACKAGE_AUTHOR = 'Apache Software Foundation'
PACKAGE_EMAIL = 'dev@beam.apache.org'
PACKAGE_KEYWORDS = 'apache beam'
PACKAGE_LONG_DESCRIPTION = '''
Apache Beam is a unified programming model for both batch and streaming
data processing, enabling efficient execution across diverse distributed
execution engines and providing extensibility points for connecting to
different technologies and user communities.
'''

REQUIRED_PIP_VERSION = '7.0.0'
_PIP_VERSION = get_distribution('pip').version
if StrictVersion(_PIP_VERSION) < StrictVersion(REQUIRED_PIP_VERSION):
  warnings.warn(
      "You are using version {0} of pip. " \
      "However, version {1} is recommended.".format(
          _PIP_VERSION, REQUIRED_PIP_VERSION
      )
  )


REQUIRED_CYTHON_VERSION = '0.28.1'
try:
  _CYTHON_VERSION = get_distribution('cython').version
  if StrictVersion(_CYTHON_VERSION) < StrictVersion(REQUIRED_CYTHON_VERSION):
    warnings.warn(
        "You are using version {0} of cython. " \
        "However, version {1} is recommended.".format(
            _CYTHON_VERSION, REQUIRED_CYTHON_VERSION
        )
    )
except DistributionNotFound:
  # do nothing if Cython is not installed
  pass

# Currently all compiled modules are optional  (for performance only).
if platform.system() == 'Windows':
  # Windows doesn't always provide int64_t.
  cythonize = lambda *args, **kwargs: []
else:
  try:
    # pylint: disable=wrong-import-position
    from Cython.Build import cythonize
  except ImportError:
    cythonize = lambda *args, **kwargs: []


REQUIRED_PACKAGES = [
    'avro>=1.8.1,<2.0.0',
    'crcmod>=1.7,<2.0',
    'dill>=0.2.6,<=0.2.8.2',
    'grpcio>=1.8,<2',
    'hdfs>=2.1.0,<3.0.0',
    'httplib2>=0.8,<=0.11.3',
    'mock>=1.0.1,<3.0.0',
    'oauth2client>=2.0.1,<5',
    # grpcio 1.8.1 and above requires protobuf 3.5.0.post1.
    'protobuf>=3.5.0.post1,<4',
    'pydot>=1.2.0,<1.3',
    'pytz>=2018.3,<=2018.4',
    'pyyaml>=3.12,<4.0.0',
    'pyvcf>=0.6.8,<0.7.0',
    'six>=1.9,<1.12',
    'typing>=3.6.0,<3.7.0',
    'futures>=3.1.1,<4.0.0',
    'future>=0.16.0,<1.0.0',
    ]

REQUIRED_PACKAGES_LINUX_ONLY = [
    'fastavro==0.19.7',
]

# TODO(BEAM-4749): fastavro fails to install in MacOS.
if 'Linux' in platform.system():
  REQUIRED_PACKAGES.extend(REQUIRED_PACKAGES_LINUX_ONLY)

REQUIRED_TEST_PACKAGES = [
    'nose>=1.3.7',
    'numpy>=1.14.3,<2',
    'pyhamcrest>=1.9,<2.0',
    ]

GCP_REQUIREMENTS = [
    # oauth2client >=4 only works with google-apitools>=0.5.18.
    'google-apitools>=0.5.18,<=0.5.20',
    'proto-google-cloud-datastore-v1>=0.90.0,<=0.90.4',
    'googledatastore==7.0.1',
    'google-cloud-pubsub==0.26.0',
    'proto-google-cloud-pubsub-v1==0.15.4',
    # GCP packages required by tests
    'google-cloud-bigquery==0.25.0',
]


# We must generate protos after setup_requires are installed.
def generate_protos_first(original_cmd):
  try:
    # See https://issues.apache.org/jira/browse/BEAM-2366
    # pylint: disable=wrong-import-position
    import gen_protos

    class cmd(original_cmd, object):
      def run(self):
        gen_protos.generate_proto_files()
        super(cmd, self).run()
    return cmd
  except ImportError:
    warnings.warn("Could not import gen_protos, skipping proto generation.")
    return original_cmd


python_requires = '>=2.7'
if os.environ.get('BEAM_EXPERIMENTAL_PY3') is None:
  python_requires += ',<3.0'

setuptools.setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    description=PACKAGE_DESCRIPTION,
    long_description=PACKAGE_LONG_DESCRIPTION,
    url=PACKAGE_URL,
    download_url=PACKAGE_DOWNLOAD_URL,
    author=PACKAGE_AUTHOR,
    author_email=PACKAGE_EMAIL,
    packages=setuptools.find_packages(),
    package_data={'apache_beam': [
        '*/*.pyx', '*/*/*.pyx', '*/*.pxd', '*/*/*.pxd', 'testing/data/*.yaml']},
    ext_modules=cythonize([
        'apache_beam/**/*.pyx',
        'apache_beam/coders/coder_impl.py',
        'apache_beam/metrics/execution.py',
        'apache_beam/runners/common.py',
        'apache_beam/runners/worker/logger.py',
        'apache_beam/runners/worker/opcounters.py',
        'apache_beam/runners/worker/operations.py',
        'apache_beam/transforms/cy_combiners.py',
        'apache_beam/utils/counters.py',
        'apache_beam/utils/windowed_value.py',
    ]),
    install_requires=REQUIRED_PACKAGES,
    python_requires=python_requires,
    test_suite='nose.collector',
    tests_require=REQUIRED_TEST_PACKAGES,
    extras_require={
        'docs': ['Sphinx>=1.5.2,<2.0'],
        'test': REQUIRED_TEST_PACKAGES,
        'gcp': GCP_REQUIREMENTS,
    },
    zip_safe=False,
    # PyPI package information.
    classifiers=[
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    license='Apache License, Version 2.0',
    keywords=PACKAGE_KEYWORDS,
    entry_points={
        'nose.plugins.0.10': [
            'beam_test_plugin = test_config:BeamTestPlugin',
        ]},
    cmdclass={
        'build_py': generate_protos_first(build_py),
        'develop': generate_protos_first(develop),
        'egg_info': generate_protos_first(egg_info),
        'sdist': generate_protos_first(sdist),
        'test': generate_protos_first(test),
    },
)
