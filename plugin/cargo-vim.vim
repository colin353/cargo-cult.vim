" 
" cargo-vim
"
" Author: 	Colin Merkel (colin.merkel@gmail.com)
" Date:		July 16 2017
"
" The plugin `cargo-vim` is designed to be the authoritative cargo
" plugin for vim, which allows you to build, run tests, show results 
" in the quickfix window, and enable automatic formatting via rustfmt.
"

let s:plugin_path = expand('<sfile>:p:h')

func! CargoQuickFix()
	let data = eval(system("python " . s:plugin_path . "/cargo.py " . expand('%:p') . " " . getcwd()))
	call setqflist(data.quickfix)
	echom data.message
	if len(data.quickfix)
		copen
	else
		cclose
	endif
endf

com! -nargs=* CargoQuickFix call CargoQuickFix()

