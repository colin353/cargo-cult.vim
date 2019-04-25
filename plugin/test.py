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

def message_object(filename, line, text, warning=False, column=0):
    m = parse.Message()
    m.text = text
    m.filename = filename
    m.line = line
    m.column = column
    m.level = 'warning' if warning else 'error'
    return m

def message(filename, line, text, warning=False, column=0):
    return message_object(filename, line, text, warning).render()

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

    def test_parse_warnings(self):
        stdout = """
{"features":[],"filenames":["/Users/colinmerkel/Documents/rust/flagger/target/debug/deps/libflags-ff67253274300a47.rlib"],"fresh":true,"package_id":"flags 0.1.0 (path+file:///Users/colinmerkel/Documents/rust/flags)","profile":{"debug_assertions":true,"debuginfo":2,"opt_level":"0","overflow_checks":true,"test":false},"reason":"compiler-artifact","target":{"crate_types":["lib"],"kind":["lib"],"name":"flags","src_path":"/Users/colinmerkel/Documents/rust/flags/src/lib.rs"}}
{"message":{"children":[{"children":[],"code":null,"level":"note","message":"#[warn(dead_code)] on by default","rendered":null,"spans":[]}],"code":null,"level":"warning","message":"function is never used: `unused`","rendered":null,"spans":[{"byte_end":143,"byte_start":109,"column_end":2,"column_start":1,"expansion":null,"file_name":"src/lib.rs","is_primary":true,"label":null,"line_end":11,"line_start":9,"suggested_replacement":null,"text":[{"highlight_end":27,"highlight_start":1,"text":"fn unused(g: i32) -> i32 {"},{"highlight_end":6,"highlight_start":1,"text":"    5"},{"highlight_end":2,"highlight_start":1,"text":"}"}]}]},"package_id":"flagger 0.1.0 (path+file:///Users/colinmerkel/Documents/rust/flagger)","reason":"compiler-message","target":{"crate_types":["lib"],"kind":["lib"],"name":"flagger","src_path":"/Users/colinmerkel/Documents/rust/flagger/src/lib.rs"}}
{"message":{"children":[{"children":[],"code":null,"level":"note","message":"#[warn(unused_variables)] on by default","rendered":null,"spans":[]}],"code":null,"level":"warning","message":"unused variable: `g`","rendered":null,"spans":[{"byte_end":120,"byte_start":119,"column_end":12,"column_start":11,"expansion":null,"file_name":"src/lib.rs","is_primary":true,"label":null,"line_end":9,"line_start":9,"suggested_replacement":null,"text":[{"highlight_end":12,"highlight_start":11,"text":"fn unused(g: i32) -> i32 {"}]}]},"package_id":"flagger 0.1.0 (path+file:///Users/colinmerkel/Documents/rust/flagger)","reason":"compiler-message","target":{"crate_types":["lib"],"kind":["lib"],"name":"flagger","src_path":"/Users/colinmerkel/Documents/rust/flagger/src/lib.rs"}}
{"features":[],"filenames":["/Users/colinmerkel/Documents/rust/flagger/target/debug/libflagger.rlib"],"fresh":false,"package_id":"flagger 0.1.0 (path+file:///Users/colinmerkel/Documents/rust/flagger)","profile":{"debug_assertions":true,"debuginfo":2,"opt_level":"0","overflow_checks":true,"test":false},"reason":"compiler-artifact","target":{"crate_types":["lib"],"kind":["lib"],"name":"flagger","src_path":"/Users/colinmerkel/Documents/rust/flagger/src/lib.rs"}}
"""
        errors, warnings = parse.parse_build_output(stdout, path_transformer)

        self.maxDiff = 10000
        self.assertItemsEqual(
            [ m.render() for m in errors ],
            []
        )
        self.assertItemsEqual(
            [ m.render() for m in warnings ],
            [
                message("src/lib.rs", 9, "function is never used: `unused`", True),
                message("src/lib.rs", 9, "unused variable: `g`", True),
            ]
        )

    def test_deduplicate(self):
        messages = [
                message("filename", 100, "hello world"),
                message("filename", 100, "hello world"),
                message("yet another message", 100, "hello world"),
                message("filename", 101, "hello world")
        ]

        expected_messages = [
                message("filename", 100, "hello world"),
                message("yet another message", 100, "hello world"),
                message("filename", 101, "hello world")
        ]

        self.assertItemsEqual(
                parse._deduplicate_messages(messages),
                expected_messages,
        )

    def test_cargo_test(self):
        stdout = """

running 9 tests
test tests::find_a_block ... FAILED
test tests::construct_sstable_builder ... ok
test tests::construct_sstable_builder_backwards ... ok
test tests::serialize_i64 ... ok
test tests::serialize_proto ... ok
test tests::read_next_key_on_constructed_sstable ... ok
test tests::read_constructed_sstable_with_iter ... ok
test tests::find_a_key ... FAILED
test tests::write_a_very_long_sstable ... ok

failures:

---- tests::find_a_block stdout ----
	thread 'tests::find_a_block' panicked at 'assertion failed: `(left == right)`
  left: `None`,
 right: `Some(123)`', src/lib.rs:502:8
note: Run with `RUST_BACKTRACE=1` for a backtrace.

---- tests::find_a_key stdout ----
	thread 'tests::find_a_key' panicked at 'assertion failed: `(left == right)`
  left: `None`,
 right: `Some(500)`', src/lib.rs:479:8
"""
        errors = parse.parse_test_output(stdout, path_transformer)
        self.maxDiff = 10000
        self.assertItemsEqual(
            [ m.render() for m in errors ],
            [
                message("src/lib.rs", 479, "tests::find_a_key assertion failed: `(left == right)` left: `None`, right: `Some(500)`", column=8),
                message("src/lib.rs", 502, "tests::find_a_block assertion failed: `(left == right)` left: `None`, right: `Some(123)`", column=8),
            ]
        )

    def test_relative_paths(self):
        self.assertEqual(
                parse.transform_relative_path(
                    "src/lib.rs",
                    "/Users/colinmerkel/Documents/rust/sstable",
                    "/Users/colinmerkel/Documents/rust",
                ),
                "sstable/src/lib.rs"
        )

    def test_error_parsing(self):
        stdout = """
error[E0425]: cannot find value `asdf1` in this scope
   --> largetable/largetable_test.rs:209:23
|
209 |         assert_eq!(0, asdf1);
|                       ^^^^^ not found in this scope

error: aborting due to previous error

For more information about this error, try `rustc --explain E0425`.
Target //largetable:largetable_test failed to build
Use --verbose_failures to see the command lines of failed build steps.
"""

        errors = parse.parse_bazel_build_output(stdout, path_transformer)
        
        self.assertEqual(
            [ m.render() for m in errors ],
            [ message("largetable/largetable_test.rs", 209, "cannot find value `asdf1` in this scope", column=23) ]
        )

    def test_error_parsing_2(self):
        stdout = """
error: couldn't read util/ws/template.html: No such file or directory (os error 2)
 --> util/ws/server.rs:7:25
  |
7 | static TEMPLATE: &str = include_str!("template.html");
  |                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

error: aborting due to previous error

Target //util/ws:server failed to build
Use --verbose_failures to see the command lines of failed build steps.
"""

        errors = parse.parse_bazel_build_output(stdout, path_transformer)
        
        self.assertEqual(
            [ m.render() for m in errors ],
            [ message("util/ws/server.rs", 7, "couldn't read util/ws/template.html: No such file or directory (os error 2)", column=25) ]
        )

if __name__ == '__main__':
    unittest.main()
