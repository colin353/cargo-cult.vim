"
" cargo-vim
"
" Author:       Colin Merkel (colin.merkel@gmail.com)
" Date:         July 16 2017
"
" The plugin `cargo-vim` is designed to be the authoritative cargo
" plugin for vim, which allows you to build, run tests, show results
" in the quickfix window, and enable automatic formatting via rustfmt.
"

let s:plugin_path = expand('<sfile>:p:h')

func! RunCargoCommand(command)
  echom "running `cargo " . a:command . "`..."
  let data = eval(system("python " . s:plugin_path . "/cargo.py " . a:command . " " . expand('%:p') . " " . getcwd()))
  call setqflist(data.quickfix)
  echom data.message
  if len(data.quickfix)
    copen
  else
    cclose
  endif
endf


func! RunBlazeCommand(command)
  echom "python " . s:plugin_path . "/bazel.py " . a:command . " " . expand('%') . " " . getcwd()
  let data = eval(system("python " . s:plugin_path . "/bazel.py " . a:command . " " . expand('%') . " " . getcwd()))
  call setqflist(data.quickfix)
  echom data.message
  if len(data.quickfix)
    copen
  else
    cclose
  endif
endf

com! -nargs=* CargoBuild call RunCargoCommand("build")
com! -nargs=* CargoTest call RunCargoCommand("test")

com! -nargs=* BlazeBuild call RunBlazeCommand("build")
com! -nargs=* BlazeTest call RunBlazeCommand("test")
