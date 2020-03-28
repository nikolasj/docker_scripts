#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import sys
import tempfile
import zipfile
from subprocess import call

import requests
from requests.packages.urllib3 import disable_warnings

disable_warnings()


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--opencv-version", action="store", help="opencv version", required=True)
    parser.add_argument("--modification", action="store", help="modification for build", required=True)

    return parser.parse_args()


def init_logging():
    logger_format_string = '%(thread)5s %(module)-20s %(levelname)-8s %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=logger_format_string, stream=sys.stdout)


def get_opencv_by_version(version):
    url = 'https://github.com/opencv/opencv/archive/{version}.zip'.format(**locals())
    print("DEBUG - Request URL: {url}".format(url=url))

    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
    except Exception as err:
        print("ERROR - {err}".format(**locals()))
        exit(1)

    return response.content


def extract_archive(path_to_unzip, archive):
    print('DEBUG - Unzip archive to {path_to_unzip}'.format(**locals()))
    file = tempfile.TemporaryFile()
    file.write(archive)
    fzip = zipfile.ZipFile(file)
    fzip.extractall(path_to_unzip)

    file.close()
    fzip.close()


def docker_build(image_name, dockerfile):
    docker_build_command = "docker build -t {image_name} -f {dockerfile} .".format(**locals())
    print("DEBUG - command to docker build: '{docker_build_command}'".format(**locals()))
    cmd = "{docker_build_command}".format(**locals()).split()

    call(cmd)


def main(opencv_version, modification):
    version_semver = '.'.join(opencv_version)
    opencv_name = 'opencv{opencv_version}'.format(**locals())
    path_to_dir = './{opencv_name}'.format(**locals())

    archive = get_opencv_by_version(version_semver)
    extract_archive(path_to_dir, archive)

    cmake_command = 'RUN cd ./{opencv_name} && mkdir build && mkdir install && cd build ' \
                    '&& cmake -DBUILD_EXAMPLES=ON .. && make -j$(nproc) && make install'.format(**locals())

    if modification == 'default':
        layers = cmake_command
    elif modification == 'mxnet':
        layers = 'RUN pip3 install mxnet==1.5.0\n{cmake_command}'.format(**locals())
    else:
        print('ERROR - modification should be given as "default" or "mxnet"')
        exit(1)

    dockerfile_content = """FROM ubuntu:18.04
RUN apt-get update && apt-get install -y \
    cmake \
    x11-apps \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*
RUN python3 -mpip install -U pip
COPY {path_to_dir}/opencv-{version_semver} ./{opencv_name}
{layers}
""".format(**locals())

    path_to_dockerfile = '{path_to_dir}/Dockerfile'.format(**locals())
    with open(path_to_dockerfile, 'w') as f:
        f.write(dockerfile_content)

    docker_build('{modification}-{opencv_name}'.format(**locals()), path_to_dockerfile)


if __name__ == "__main__":
    args = parse_args()
    init_logging()
    main(**args.__dict__)
