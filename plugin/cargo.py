#
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

def finish(output):
    sys.stdout.write(json.dumps(output))
    sys.exit(0)

def error(reason):
    finish({
        "message": reason,
        "quickfix": []
    })

class Message(object):
    def __init__(self):
        self.text = ""
        self.filename = ""
        self.line = 0
        self.column = 0

    def relative_file_path(self):
        common_prefix = os.path.commonprefix("%s/%s" % (CARGO_DIR, self.filename), CWD)
        return os.path.relpath(self.filename, common_prefix)

    def render(self):
        return {
            "filename": self.filename,
            "lnum": self.line,
            "text": self.text
        }

DEVNULL = open(os.devnull, 'w')
try:
    FILE = sys.argv[1]
    CWD = sys.argv[2]
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
            ["cargo", "build", "--message-format=json"],
            stderr=DEVNULL,
            cwd=CARGO_DIR
    )
except subprocess.CalledProcessError as e:
    stdout = e.output

errors = []
warnings = []
for line in str(stdout).split('\n'): 
   if line == "":
        continue
    
   try:
        cargo_message = json.loads(line)
   except ValueError:
        error("Problem parsing output of `cargo build`. Do you have cargo installed?")
   if cargo_message['reason'] != 'compiler-message':
       continue

   for msg in cargo_message['message']['spans']:
       message = Message()
       message.filename = msg['file_name']
       message.line     = msg['line_start']
       message.text     = msg['label']
       message.column   = msg['column_start']
       errors.append(message.render())

reason = "`cargo build`: success"
if len(errors) > 0:
    reason = "`cargo build` failed, check quickfix"

finish({
    "message": reason,
    "quickfix": errors
})
