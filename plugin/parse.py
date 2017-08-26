#
#   parse.py
#
#   Author:     Colin Merkel
#   Date:       July 15 2017
#
#   For some reason (see https://github.com/rust-lang/cargo/issues/1403),
#   `cargo test` ignores the --message-format=json directive and outputs
#   regular old text. So we need to parse the text directly in order to put
#   the output into the quickfix bar in vim. This module parses the text.

import json
import os
import re

class CargoParseError(Exception):
    pass

# transform_relative_path takes a file path relative to the
# cargo directory and transforms it into a path relative to the
# CWD inside of vim, which is passed as a command line argument.
def transform_relative_path(cargo_path, cargo_dir, working_dir):
    return os.path.relpath("%s/%s" % (cargo_dir, cargo_path), working_dir)

class Message(object):
    def __init__(self):
        self.text = ""
        self.filename = ""
        self.line = 0
        self.column = 0

        # self.level can either be "warning" or "error".
        self.level = 'error'

    def render(self):
        if self.text is None:
            self.text = ""

        return {
            "filename": self.filename,
            "lnum": self.line,
            "text": self.text,
            "type": "W" if self.level == 'warning' else "E",
        }

    def __eq__(self, other):
        return (
            self.text == other.text and \
            self.filename == other.filename and \
            self.line == other.line and \
            self.column == other.column
        )

    def __repr__(self):
        return "%s:%s || %s" % (self.filename, self.line, self.text)

def parse_command_output(command, output, path_transformer):
    errors = []
    warnings = []
    if command == "build":
        errors, warnings = parse_build_output(output, path_transformer)
    elif command == "test":
        errors, _ = parse_build_output(output, path_transformer)
        if len(errors) == 0:
            errors = parse_test_output(output, path_transformer)
    else:
        raise CargoParseError("No such command: `%s`" % command)

    return _deduplicate_messages(errors), _deduplicate_messages(warnings)

def parse_build_output(output, path_transformer):
    errors = []
    warnings = []
    skipped_build_due_to_fresh_cache = True
    for line in output.split('\n'):
        try:
            cargo_message = json.loads(line)
        except ValueError:
            continue

        if cargo_message['reason'] == 'compiler-artifact':
            if not cargo_message['fresh']:
                skipped_build_due_to_fresh_cache = False
        if cargo_message['reason'] != "compiler-message":
            continue

        for msg in cargo_message['message']['spans']:
            message = Message()
            message.filename = path_transformer(msg['file_name'])
            message.line = msg['line_start']

            # Sometimes it's the case that the error occurred inside macro-expanded code.
            # In that case, this filename isn't the one we want. We want the data from
            # inside the expansion, which maps back to the original code.
            if message.filename.startswith('<'):
                message.filename = msg['expansion']['span']['file_name']
                message.line = msg['expansion']['span']['line_start']

            message.text = msg['label']
            message.level = cargo_message['message']['level']
            # For some reason, warnings are not written to the 'label'. So we
            # need to read them from 'message'->'message' instead.
            if not message.text:
                message.text = cargo_message['message']['message']
            message.column = msg['column_start']

            if message.level == 'warning':
                warnings.append(message)
            else:
                errors.append(message)

    if skipped_build_due_to_fresh_cache:
        cache_warning = Message()
        cache_warning.text = "`cargo` skipped build since there were no changes since last build. To force rebuild, update the timestamp on a file (e.g. :w)."
        warnings.append(cache_warning)

    return errors, warnings

def _parse_accumulated_message(text, path_transformer):
    expr = r"---- ([^\s]+) [^\s]+ ----.+panicked at '(.*)', ([^\:]*):(\d+):?(\d+)?"
    results = re.match(expr, text)
    if not results:
        raise CargoParseError("Can't parse test output: %s" % text)

    m = Message()
    m.text = "%s %s" % (results.group(1), results.group(2))
    m.filename = path_transformer(results.group(3))
    m.line = int(results.group(4))
    if results.group(5) is not None:
        m.column = int(results.group(5))
    return m

# _deduplicate_messages makes sure that duplicate warnings/errors aren't
# repeated in the quickfix tray. For some reason, this can sometimes happen,
# and I'm not really sure how to avoid it via cargo flags, so we can just
# deduplicate here.
def _deduplicate_messages(messages):
    output = {}
    for m in messages:
        output[str(m)] = m

    return [ m for m in output.values() ]

def parse_test_output(output, path_transformer):
    lines = [ line.strip() for line in output.split('\n') ]
    accumulated_message = ""
    messages = []
    for line in lines:
        if accumulated_message != "":
            if line.startswith("----"):
                messages.append(_parse_accumulated_message(
                    accumulated_message,
                    path_transformer
                ))
                accumulated_message = line
            else:
                accumulated_message += " " + line

        elif line.startswith("----"):
                accumulated_message = line

    if accumulated_message != "":
        messages.append(_parse_accumulated_message(
            accumulated_message,
            path_transformer
        ))

    return messages
