#   bazel.py
#
#   Author:     Colin Merkel
#   Date:       April 24 2019

import subprocess
import json
import os
import sys

import parse

def finish(output):
    sys.stdout.write(json.dumps(output))
    sys.exit(0)

def error(reason):
    finish({ "message": reason, "quickfix": [] })

def transform_relative_path(file_path):
    return parse.transform_relative_path(file_path, BAZEL_DIR, CWD)

try:
    COMMAND = sys.argv[1]
    FILE = sys.argv[2]
    CWD = sys.argv[3]
# Sometimes not enough parameters are passed in, which means that the
# user tried to run `cargo build` on an empty buffer, or something
# like that.
except IndexError:
    error("Can't find WORKSPACE, is this a bazel project?")

# Find the root directory of the project, where Cargo.toml is located.
BAZEL_DIR = os.path.dirname(CWD + "/" + FILE)
while not os.path.isfile(BAZEL_DIR + "/WORKSPACE"):
    parent_directory = os.path.dirname(BAZEL_DIR)
    # Make sure we haven't reached the top level directory.
    if parent_directory == BAZEL_DIR:
        error("Can't find WORKSPACE, is this a cargo project?")
    BAZEL_DIR = parent_directory


try:
    local_dir = os.path.dirname(os.path.realpath(__file__))
    command  = ' '.join(["%s/blaze.sh" % local_dir, COMMAND, FILE])
    stdout = subprocess.check_output( ["%s/blaze.sh" % local_dir, COMMAND, FILE],
            # If you don't provide this option, it'll end up emitting some
            # data to the screen.
            cwd=CWD,
            stderr=open(os.devnull, 'w'),)
except subprocess.CalledProcessError as e:
    # It's necessary to catch this error because rust will
    # intentionally return exit code > 0 when the build/test
    # fails, but it'll still output the correct info.
    stdout = e.output

quickfix = []
try:
    errors, warnings = parse.parse_bazel_output(
            COMMAND,
            str(stdout),
            transform_relative_path
            )
except parse.CargoParseError as e:
    error(str(e))

reason = "`cargo %s`: success" % COMMAND
if len(errors) > 0:
    reason = "`cargo %s` failed, check quickfix" % COMMAND
    quickfix = errors
elif len(warnings) > 0:
    reason = "`cargo %s` succeeded with warnings, check quickfix" % COMMAND
    quickfix = warnings

finish({ "message": reason, "quickfix": [m.render() for m in quickfix] })
