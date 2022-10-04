import os
import shutil
import subprocess
import sys


def build_sphinx_docs(temp_dir='_build'):
    """Build sphinx docs for python."""
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    cmd = ['make', 'html']
    subprocess.check_call(cmd, stdout=sys.stdout, stderr=sys.stderr)


def build_doxygen_docs(temp_dir='doxygen', cpp_dir='cpp_api'):
    """Build sphinx docs for C++"""
    cmd = ['doxygen', 'Doxyfile']
    subprocess.check_call(cmd, stdout=sys.stdout, stderr=sys.stderr)
    # move generated results to _build
    doxygen_dir = os.path.join(temp_dir, 'html')
    dst_dir = os.path.join('_build', 'html', cpp_dir)
    shutil.copytree(doxygen_dir, dst_dir, dirs_exist_ok=True)
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    build_sphinx_docs()
    build_doxygen_docs()
