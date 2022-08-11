import os
import re
import shutil
import subprocess
import sys

from setuptools import Extension, find_packages, setup
from setuptools.command.build_ext import build_ext

# Our python package root dir is python/
PACKAGE_DIR = 'python'

PACKAGES = find_packages(PACKAGE_DIR)

# Convert distutils Windows platform specifiers to CMake -A arguments
PLAT_TO_CMAKE = {
    'win32': 'Win32',
    'win-amd64': 'x64',
    'win-arm32': 'ARM',
    'win-arm64': 'ARM64',
}


def parse_version_from_file(filepath):
    """Parse version txt into string and tuple.

    Args:
        filepath (str): The version filepath.
    Returns:
        str: The version string, e.g., "0.4.0"
        dict: The version info, e.g.,
            {
                'XRPRIMER_VERSION_MAJOR': 0,
                'XRPRIMER_VERSION_MINOR': 4,
                'XRPRIMER_VERSION_PATCH': 0,
            }
    """
    keywords = [
        'XRPRIMER_VERSION_MAJOR', 'XRPRIMER_VERSION_MINOR',
        'XRPRIMER_VERSION_PATCH'
    ]
    version_info = {}
    version_list = []
    with open(filepath) as f:
        content = f.read()
        for keyword in keywords:
            regex = rf'{keyword}\s*([0-9]+)'
            obj = re.search(regex, content)
            vid = obj.group(1)
            version_list.append(vid)
            assert keyword not in version_info
            version_info[keyword] = int(vid)
    version = '.'.join(version_list)
    return version, version_info


VERSION, VERSION_INFO = parse_version_from_file('version.txt')


# A CMakeExtension needs a sourcedir instead of a file list.
# The name must be the _single_ output extension from the CMake build.
# If you need multiple extensions, see scikit-build.
class CMakeExtension(Extension):

    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


def clean_cmake(folders):
    for folder in folders:
        if not os.path.exists(folder):
            continue
        shutil.rmtree(folder)


class CMakeBuild(build_ext):

    def build_extension(self, ext):
        extdir = os.path.abspath(
            os.path.dirname(self.get_ext_fullpath(ext.name)))

        # required for auto-detection & inclusion of auxiliary "native" libs
        if not extdir.endswith(os.path.sep):
            extdir += os.path.sep

        debug = int(os.environ.get('DEBUG',
                                   0)) if self.debug is None else self.debug
        cfg = 'Debug' if debug else 'Release'

        # CMake lets you override the generator - we need to check this.
        # Can be set with Conda-Build, for example.
        cmake_generator = os.environ.get('CMAKE_GENERATOR', '')

        # Set Python_EXECUTABLE instead if you use PYBIND11_FINDPYTHON
        # EXAMPLE_VERSION_INFO shows you how to pass a value into the C++ code
        # from Python.
        cmake_args = [
            f'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}',
            f'-DPYTHON_EXECUTABLE={sys.executable}',
            f'-DCMAKE_BUILD_TYPE={cfg}',  # not used on MSVC, but no harm
        ]
        build_args = []
        # Adding CMake arguments set as environment variable
        # (needed e.g. to build for ARM OSx on conda-forge)
        if 'CMAKE_ARGS' in os.environ:
            cmake_args += [
                item for item in os.environ['CMAKE_ARGS'].split(' ') if item
            ]

        # Enable test
        cmake_args += ['-DENABLE_TEST=OFF']
        # Build external from pre-built libs by default
        ret = os.system('conan remote list | grep xrlab')
        if ret == 0:  # remote exists
            cmake_args += ['-DBUILD_EXTERNAL=OFF']
        else:
            cmake_args += ['-DBUILD_EXTERNAL=ON']

        # Pass version
        for key, version in VERSION_INFO.items():
            assert key.isupper(), f'{key} is expected to be uppercase'
            cmake_args += [f'-D{key}={version}']

        if self.compiler.compiler_type != 'msvc':
            # Using Ninja-build since it a) is available as a wheel and b)
            # multithreads automatically. MSVC would require all variables be
            # exported for Ninja to pick it up, which is a little tricky to do.
            # Users can override the generator with CMAKE_GENERATOR in CMake
            # 3.15+.
            if not cmake_generator or cmake_generator == 'Ninja':
                try:
                    import ninja  # noqa: F401

                    ninja_executable_path = os.path.join(
                        ninja.BIN_DIR, 'ninja')
                    cmake_args += [
                        '-GNinja',
                        f'-DCMAKE_MAKE_PROGRAM:FILEPATH={ninja_executable_path}',  # noqa: E501
                    ]
                except ImportError:
                    pass

        else:

            # Single config generators are handled "normally"
            single_config = any(x in cmake_generator
                                for x in {'NMake', 'Ninja'})

            # CMake allows an arch-in-generator style for backward
            # compatibility.
            contains_arch = any(x in cmake_generator for x in {'ARM', 'Win64'})

            # Specify the arch if using MSVC generator, but only if it doesn't
            # contain a backward-compatibility arch spec already in the
            # generator name.
            if not single_config and not contains_arch:
                cmake_args += ['-A', PLAT_TO_CMAKE[self.plat_name]]

            # Multi-config generators have a different way to specify configs
            if not single_config:
                cmake_args += [
                    f'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{cfg.upper()}={extdir}'
                ]
                build_args += ['--config', cfg]

        if sys.platform.startswith('darwin'):
            # Cross-compile support for macOS - respect ARCHFLAGS if set
            archs = re.findall(r'-arch (\S+)', os.environ.get('ARCHFLAGS', ''))
            if archs:
                cmake_args += [
                    '-DCMAKE_OSX_ARCHITECTURES={}'.format(';'.join(archs))
                ]

        # Set CMAKE_BUILD_PARALLEL_LEVEL to control the parallel build level
        # across all generators.
        if 'CMAKE_BUILD_PARALLEL_LEVEL' not in os.environ:
            # self.parallel is a Python 3 only way to set parallel jobs by hand
            # using -j in the build_ext call, not supported by pip or
            # PyPA-build.
            if not hasattr(self, 'parallel') or not self.parallel:
                # Manually use 1/4 total cpu for compilation
                import multiprocessing as mp
                cpu_count = mp.cpu_count()
                self.parallel = max(1, int(cpu_count / 4))
                print(f'{self.parallel} cpu cores are used for compilation')
            if hasattr(self, 'parallel') and self.parallel:
                # CMake 3.12+ only.
                build_args += [f'-j{self.parallel}']

        install_dir = 'install'
        build_temp = self.build_temp
        clean_cmake(folders=['_deps', '_exts', build_temp, install_dir])
        subprocess.check_call(['cmake', '-S.', '-B', build_temp] + cmake_args)
        subprocess.check_call(
            ['cmake', '--build', build_temp, '--target', install_dir] +
            build_args)


def readme():
    with open('./README.md', encoding='utf-8') as f:
        content = f.read()
    return content


def parse_requirements(fname='requirements.txt', with_version=True):
    """Parse the package dependencies listed in a requirements file but strips
    specific versioning information.

    Args:
        fname (str): path to requirements file
        with_version (bool, default=False): if True include version specs

    Returns:
        List[str]: list of requirements items

    CommandLine:
        python -c "import setup; print(setup.parse_requirements())"
    """
    require_fpath = fname

    def parse_line(line):
        """Parse information from a line in a requirements text file."""
        if line.startswith('-r '):
            # Allow specifying requirements in other files
            target = line.split(' ')[1]
            for info in parse_require_file(target):
                yield info
        else:
            info = {'line': line}
            if line.startswith('-e '):
                info['package'] = line.split('#egg=')[1]
            else:
                # Remove versioning from the package
                pat = '(' + '|'.join(['>=', '==', '>']) + ')'
                parts = re.split(pat, line, maxsplit=1)
                parts = [p.strip() for p in parts]

                info['package'] = parts[0]
                if len(parts) > 1:
                    op, rest = parts[1:]
                    if ';' in rest:
                        # Handle platform specific dependencies
                        # http://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-platform-specific-dependencies
                        version, platform_deps = map(str.strip,
                                                     rest.split(';'))
                        info['platform_deps'] = platform_deps
                    else:
                        version = rest  # NOQA
                    info['version'] = (op, version)
            yield info

    def parse_require_file(fpath):
        with open(fpath, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    for info in parse_line(line):
                        yield info

    def gen_packages_items():
        if os.path.exists(require_fpath):
            for info in parse_require_file(require_fpath):
                parts = [info['package']]
                if with_version and 'version' in info:
                    parts.extend(info['version'])
                if not sys.version.startswith('3.4'):
                    # apparently package_deps are broken in 3.4
                    platform_deps = info.get('platform_deps')
                    if platform_deps is not None:
                        parts.append(';' + platform_deps)
                item = ''.join(parts)
                yield item

    packages = list(gen_packages_items())
    return packages


setup(
    name='xrprimer',
    version=VERSION,
    description='description',
    long_description=readme(),
    long_description_content_type='text/markdown',
    author='OpenXRLab',
    author_email='openxrlab@sensetime.com',
    keywords='xrprimer',
    url='https://gitlab.bj.sensetime.com/openxrlab/xrprimer',
    package_dir={'': PACKAGE_DIR},
    packages=PACKAGES,
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    license='Apache License 2.0',
    tests_require=parse_requirements('requirements/test.txt'),
    install_requires=parse_requirements('requirements/runtime.txt'),
    ext_modules=[CMakeExtension('xrprimer_cpp')],
    cmdclass={'build_ext': CMakeBuild},
    zip_safe=False)
