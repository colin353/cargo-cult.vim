# Cargo + vim

This script runs the cargo build command and puts the formatted
output into the quickfix list. 

## Features we need

 - [x] Package into a vim package which can be loaded by pathogen.
 - [x] Automatically detect the cargo directory of the file being
     edited so the CWD doesn't matter when running the script.
 - [x] Somehow reference the python file in the pathogen directory.
 - [ ] Get some nice command shortcuts.
 - [ ] Support warnings, test failures, etc.

