# cargo-cult.vim

This script runs the `cargo build` and `cargo test` commands and
puts the formatted output into the quickfix list.

## Features to add

 - [x] Package into a vim package which can be loaded by pathogen.
 - [x] Automatically detect the cargo directory of the file being
     edited so the CWD doesn't matter when running the script.
 - [x] Somehow reference the python file in the pathogen directory.
 - [x] Support test failures
 - [x] Support warnings
 - [ ] Rewrite the python to be more readable and with more clear
       error messages.
 - [ ] Make a check.py file which will make sure you have cargo
       installed, correct vim version, etc.
 - [ ] Add installation instructions to this README.md
 - [ ] Get some nice command shortcuts, and describe them in this file.

## Bugs

 - [ ] There's some kind of bug where it occasionally prints blank error
       messages for each compiled file even when no errors occurred, I
       think this relates to recompiling when it was cached.
 - [ ] The file path translator sometimes gets the path wrong. I'm building
       from flagger/Users/colinmerkel/Documents/rust/flags/src/parse.rs
