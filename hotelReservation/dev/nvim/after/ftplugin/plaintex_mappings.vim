set spell
nnoremap <buffer> <C-c> :! ~/useful_scripts/compile_tex.sh '%:t'<CR>
"nnoremap <buffer> <C-b> :! ~/useful_scripts/compile_beamer.sh '%:t'<CR>
nnoremap <buffer> <C-b> :call RunCommand("~/useful_scripts/compile_beamer.sh '%:t'", 0x2)<CR>
