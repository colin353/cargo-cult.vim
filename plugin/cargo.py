
#   cargo.py
#
#   Author:     Colin Merkel
#   Date:       July 15 2017
#
#   cargo.py runs rust's package manager `cargo`, and outputs the build results
#   in a format that vim can understand for the quickfix bar.

import subprocess
import json
import os
import sys

import parse

def finish(output):
    sys.stdout.write(json.dumps(output))
    sys.exit(0)

def error(reason):
    finish({
        "message": reason,
        "quickfix": []
    })

# transform_relative_path takes a file path relative to the 
# cargo directory and transforms it into a path relative to the
# CWD inside of vim, which is passed as a command line argument.
def transform_relative_path(cargo_path):
    return os.path.relpath("%s/%s" % (CARGO_DIR, cargo_path), CWD)

try:
    COMMAND = sys.argv[1]
    FILE = sys.argv[2]
    CWD = sys.argv[3]
# Sometimes not enough parameters are passed in, which means that the
# user tried to run `cargo build` on an empty buffer, or something
# like that.
except IndexError:
    error("Can't find Cargo.toml, is this a cargo project?")

# Find the root directory of the project, where Cargo.toml is located.
CARGO_DIR = os.path.dirname(FILE)
while not os.path.isfile(CARGO_DIR + "/Cargo.toml"):
    parent_directory = os.path.dirname(CARGO_DIR)
    # Make sure we haven't reached the top level directory.
    if parent_directory == CARGO_DIR:
        error("Can't find Cargo.toml, is this a cargo project?")
    CARGO_DIR = parent_directory


try:
    stdout = subprocess.check_output(
            ["cargo", COMMAND, "--message-format=json"],
            # If you don't provide this option, it'll end up
            # emitting some data to the screen.
            stderr=open(os.devnull, 'w'),
            cwd=CARGO_DIR
    )
# It's necessary to catch this error because rust will
# intentionally return exit code > 0 when the build/test
# fails, but it'll still output the correct info.
except subprocess.CalledProcessError as e:
    stdout = e.output

quickfix = []
try:
    errors, warnings = parse.parse_command_output(
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

finish({
    "message": reason,
    "quickfix": [ m.render() for m in quickfix ]
})
