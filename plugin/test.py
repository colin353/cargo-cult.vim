#
#   test.py
#
#   Author:     Colin Merkel
#   Date:       July 15 2017
#
#   This file contains tests for parse.py, to make sure it can
#   correctly decode test output.
#   

import unittest

import parse

def path_transformer(path):
    return path

def message(filename, line, text):
    m = parse.Message()
    m.text = text
    m.filename = filename
    m.line = line
    return m.render()

class TestParseData(unittest.TestCase):
    def test_parse_output(self):
        messages = parse.parse_test_output("""

running 1 test
test bloop::test_something ... FAILED

failures:

---- bloop::test_something stdout ----
        thread 'bloop::test_something' panicked at 'assertion failed: `(left == right)` (left: `true`, right: `false`)', src/bloop.rs:7

---- bloop::test_something_else stdout ----
        thread 'bloop::test_something_else' panicked at 'assertion failed: `(left == right)` (left: `"asdf"`, right: `"asdfasdf"`)', src/bloop.rs:12
note: Run with `RUST_BACKTRACE=1` for a backtrace.

failures:
    bloop::test_something

test result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured
        """, path_transformer)

        self.assertItemsEqual(
            [ m.render() for m in messages ], 
            [
                message("src/bloop.rs", 7, "bloop::test_something assertion failed: `(left == right)` (left: `true`, right: `false`)"),
                message("src/bloop.rs", 12, "bloop::test_something_else assertion failed: `(left == right)` (left: `\"asdf\"`, right: `\"asdfasdf\"`)")
            ]
        )

if __name__ == '__main__':
    unittest.main()
