set guicursor=
set nu
syntax enable
set mouse=a
set mousehide
set wrap
set autoindent
set cursorline
set shiftwidth=4
set relativenumber
set expandtab
set tabstop=4
set softtabstop=4
set scrolloff=5
" set colorcolumn=80
set tags=tags;/
set splitright
set splitbelow
filetype plugin indent on
scriptencoding utf-8

" Plugins (from vim-plug)
call plug#begin('~/.vim/plugged')
    Plug 'vim-airline/vim-airline'
    Plug 'kien/ctrlp.vim' " You gotta love CtrlP
    Plug 'matze/vim-tex-fold'
    Plug 'scrooloose/nerdtree' " Quick file explorer
    Plug 'easymotion/vim-easymotion' " Easymotion for enhanced f functionality
    Plug 'tpope/vim-obsession' " Vim Sessions to Support TMUX Resurrect
    Plug 'tpope/vim-repeat'
    Plug 'tpope/vim-surround'
    Plug 'rhysd/vim-clang-format' " Clang format
    Plug 'psf/black' " Python code formatting
    Plug 'ekalinin/Dockerfile.vim' " Dockerfile syntax highlighting
    Plug 'prabirshrestha/async.vim' " Code completlion
    Plug 'prabirshrestha/vim-lsp' " Language server
call plug#end()
let g:deoplete#enable_at_startup = 1

" Omnicomplete

filetype plugin on
set omnifunc=syntaxcomplete#Complete
set completeopt=longest,menuone
inoremap <expr> <CR> pumvisible() ? "\<C-y>" : "\<C-g>u\<CR>"

" vim-lsp

au User lsp_setup call lsp#register_server({
    \ 'name': 'pyls',
    \ 'cmd': {server_info->['pyls']},
    \ 'allowlist': ['python'],
    \ })

autocmd FileType python setlocal omnifunc=lsp#complete

au User lsp_setup call lsp#register_server({
    \ 'name': 'clangd',
    \ 'cmd': {server_info->['/usr/bin/clangd-10', '--background-index']},
    \ 'allowlist': ['c', 'cpp'],
\ })

autocmd FileType c setlocal omnifunc=lsp#complete
autocmd FileType cpp setlocal omnifunc=lsp#complete
autocmd FileType objc setlocal omnifunc=lsp#complete
autocmd FileType objcpp setlocal omnifunc=lsp#complete

au User lsp_setup call lsp#register_server({
  \ 'name': 'go-lang',
  \ 'cmd': {server_info->['gopls']},
  \ 'whitelist': ['go'],
\ })

autocmd FileType go setlocal omnifunc=lsp#complete

" NOTE: the leader key here is the default one (i.e. `\`) instead of the `,`
" used later on.
nnoremap <Leader>d :LspDefinition<CR>
nnoremap <Leader>i :LspImplementation<CR>
nnoremap <Leader>r :LspRename<CR>
nnoremap <Leader>n :LspNextError<CR>
nnoremap <Leader>a :LspCodeAction<CR>

" Disable auto popup
let g:asyncomplete_auto_popup = 0

" CtrlP Settings
let g:ctrlp_root_markers = ['build.sbt', '*.latexmain', 'pom.xml']
let g:ctrlp_custom_ignore = {
  \ 'dir':  '\v[\/]\.(git|hg|svn)$',
  \ 'file': '\v\.(exe|so|dll|log|toc|class|aux|blg|bbl|pdf|latexmain|out)$',
  \ 'link': 'some_bad_symbolic_links',
  \ }

" Colors
set termguicolors
set background=dark
" colorscheme material
" let g:material_theme_style = 'dark'
" let g:airline_theme = 'material'

" NERDTree Config
let NERDTreeQuitOnOpen=1
map <C-n> :NERDTreeToggle<CR>

" Easier split navigations
nnoremap <C-J> <C-W><C-J>
nnoremap <C-K> <C-W><C-K>
nnoremap <C-L> <C-W><C-L>
nnoremap <C-H> <C-W><C-H>

" Copy to system clipboard
vnoremap <C-c> "+y

" Easymotion configuration
" NOTE: we use the new leader for easy motion, but not for LSP
let mapleader = ","
let g:EasyMotion_leader_key = '<Leader>'
map <Leader> <Plug>(easymotion-prefix)

" Mappings to access buffers (don't use "\p" because a
" delay before pressing "p" would accidentally paste).
" \l       : list buffers
" \b \f \g : go back/forward/last-used
" \1 \2 \3 : go to buffer 1/2/3 etc
nnoremap <Leader>l :ls<CR>
nnoremap <Leader>b :bp<CR>
nnoremap <Leader>a :bn<CR>
nnoremap <Leader>g :e#<CR>
nnoremap <Leader>1 :1b<CR>
nnoremap <Leader>2 :2b<CR>
nnoremap <Leader>3 :3b<CR>
nnoremap <Leader>4 :4b<CR>
nnoremap <Leader>5 :5b<CR>
nnoremap <Leader>6 :6b<CR>
nnoremap <Leader>7 :7b<CR>
nnoremap <Leader>8 :8b<CR>
nnoremap <Leader>9 :9b<CR>
nnoremap <Leader>0 :10b<CR>

" Useful commands if sloppy fingers
:command WQ wq
:command Wq wq
:command W w
:command Q q

" 80 chs column
set colorcolumn=80
highlight ColorColumn guibg=gray

" Custom FileType Definition, for mappings see after/ftplugin/
" TODO this does not work
au BufRead,BufNewFile *.gp setfiletype gnuplot
au BufRead,BufNewFile *.tex setfiletype tex
nnoremap <C-s> :syntax sync fromstart<CR>

" Remove trailing whitespace
autocmd BufWritePre * :%s/\s\+$//e

" Asynchronous run command using TMUX. All credits go to:
" https://gist.github.com/tracyone/65cffd685fc9b9308e50c1a1783d1fb0
" Flags:
"   0x1 hor split window
"   0x2 vertical split window
"   0x4 new window
"   0x8 run command in background
function! RunCommand(cmd, flag) abort
    let l:action = 'split-window -p 38 '
    "split
    if and(a:flag, 0x1)
        let l:action = 'split-window -p 28 '
    elseif and(a:flag, 0x2)
        let l:action = 'split-window -h -p 28 '
    elseif and(a:flag, 0x4)
        let l:action = 'new-window '
    endif
    if and(a:flag, 0x8)
        let l:action .= ' -d '
    endif
    call system('tmux '.l:action.string(a:cmd))
endfunction
