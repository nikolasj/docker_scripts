#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import subprocess
import sys


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--opencv-version", action="store", help="opencv version", required=True)
    parser.add_argument("--modification", action="store", help="modification for build", required=True)
    parser.add_argument("--check1", action='store_true', help="xeyes check")
    parser.add_argument("--check2", action='store_true', help="opencv version check")
    parser.add_argument("--check3", action='store_true', help="mxnet check")

    return parser.parse_args()


def init_logging():
    logger_format_string = '%(thread)5s %(module)-20s %(levelname)-8s %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=logger_format_string, stream=sys.stdout)


def docker_run(image_name, command, subprocess_call=True):
    docker_run_command = "docker run --rm -it {image_name} {command}".format(**locals())
    print("DEBUG - command to docker run: '{docker_run_command}'".format(**locals()))

    if subprocess_call:
        cmd = "{docker_run_command}"

        subprocess.call(docker_run_command, shell=True)
    else:
        try:
            subprocess.check_call(command, shell=True)
        except Exception as err:
            print("ERROR - {err}".format(**locals()))
            exit(1)


def main(opencv_version, modification, check1, check2, check3):
    image_name = '{modification}-opencv{opencv_version}'.format(**locals())

    if check1:
        command = 'xeyes'
        docker_run(image_name, command, subprocess_call=False)

    if check2:
        command = 'opencv_version'
        docker_run(image_name, command)

    if check3:
        command = 'python3 -mpip list | grep mxnet'
        docker_run(image_name, command)

    if not (check1 or check2 or check3):
        docker_run(image_name, '')


if __name__ == "__main__":
    args = parse_args()
    init_logging()
    main(**args.__dict__)
