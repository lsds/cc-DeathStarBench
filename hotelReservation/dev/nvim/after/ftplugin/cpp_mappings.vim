" clang-format (@Shillaker)
" Use local .clang-format files
let g:clang_format#detect_style_file = 1
" Do nothing unless .clang-format file found
let g:clang_format#enable_fallback_style = 1
" Specify the clang-format command to avoid confusion
let g:clang_format#command = '/usr/bin/clang-format-10'
" ClangFormat _very_ slow
" nnoremap <leader>c :<C-u>ClangFormat<CR>
nnoremap <leader>c :! clang-format-10 -i --style=file %<CR>
