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

class Message(object):
    def __init__(self):
        self.text = ""
        self.filename = ""
        self.line = 0
        self.column = 0

    def render(self):
        if self.text is None:
            self.text = ""

        return {
            "filename": self.filename,
            "lnum": self.line,
            "text": self.text
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
    if command == "build":
        return parse_build_output(output, path_transformer)
    elif command == "test":
        return parse_test_output(output, path_transformer)

    raise CargoParseError("No such command: `%s`" % command)

def parse_build_output(output, path_transformer):
    errors = []
    for line in output.split('\n'):
        if line == "":
            continue

        try:
            cargo_message = json.loads(line)
        except ValueError:
            raise CargoParseError("Problem parsing output of `cargo build`. Do you have cargo installed?")

        if cargo_message['reason'] != "compiler-message":
            continue

        for msg in cargo_message['message']['spans']:
            message = Message()
            message.filename = path_transformer(msg['file_name'])
            message.line = msg['line_start']
            message.text = msg['label']
            message.column = msg['column_start']
            errors.append(message)

    return errors

def _parse_accumulated_message(text, path_transformer):
    expr = "---- ([^\s]+) [^\s]+ ----.+panicked at '(.*)', (.*):(\d+)"
    results = re.match(expr, text)
    if not results:
        raise CargoParseError("Can't parse test output: %s" % text)

    m = Message()
    m.text = "%s %s" % (results.group(1), results.group(2))
    m.filename = results.group(3)
    m.line = int(results.group(4))
    return m

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
                accumulated_message += line

        elif line.startswith("----"):
                accumulated_message = line

    if accumulated_message != "":
        messages.append(_parse_accumulated_message(
            accumulated_message, 
            path_transformer
        ))

    return messages
