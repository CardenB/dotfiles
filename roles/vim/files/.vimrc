" URL: http://vim.wikia.com/wiki/Example_vimrc
" Authors: http://vim.wikia.com/wiki/Vim_on_Freenode
" Description: A minimal, but feature rich, example .vimrc. If you are a
"              newbie, basing your first .vimrc on this file is a good choice.
"              If you're a more advanced user, building your own .vimrc based
"              on this file is still a good idea.
"------------------------------------------------------------
" Features 
"
" These options and commands enable some very useful features in Vim, that
" no user should have to live without.
" Set 'nocompatible' to ward off unexpected things that your distro might
" have made, as well as sanely reset options when re-sourcing .vimrc
set nocompatible

" Set utf-8 encoding for YCM.
set encoding=utf-8

" set for vundle
filetype off                        " required

" set the runtime path to include Vundle and initialize
set rtp+=~/.vim/bundle/Vundle.vim    " required
call vundle#begin()                 " required
" alternatively, pass a path where Vundle should install plugins
" call vundle#begin('~/some/path/here')

" let Vundle manage Vundle, required
Plugin 'gmarik/Vundle.vim'          " required

" Keep Plugin commands between vundle#begin/end
" Plugin from git repo: https://github.com/Valloric/YouCompleteMe
Plugin 'Valloric/YouCompleteMe'

" Plugin for solarized colorscheme
Plugin 'altercation/vim-colors-solarized'

" Plugin for linting C++
Plugin 'scrooloose/syntastic'

" Plugin for using grep within vim
Plugin 'mhinz/vim-grepper'

" Plugin for handling git within vim
Plugin 'tpope/vim-fugitive'

" Plugin for handling github from vim-fugitive.
" Enables features like `:Gbrowse`.
Plugin 'tpope/vim-rhubarb'

" Plugin for fuzzy searching files.
Plugin 'ctrlpvim/ctrlp.vim'

" Plugin for vue.js syntax highlighting.
Plugin 'posva/vim-vue'
Plugin 'leafgarland/typescript-vim'

" Plugin for faster ctrlp fuzzy searching.
" Disabled in favor of fzf.
" Plugin 'wincent/command-t'

" Plugin for faster cmdt fuzzy searching.
Plugin 'junegunn/fzf'
Plugin 'junegunn/fzf.vim'

" All of your Plugins must be added before the following line
call vundle#end()                   " required
" Attempt to determine the type of a file based on its name and possibly its
" contents. Use this to allow intelligent auto-indenting for each filetype,
" and for plugins that are filetype specific.
filetype indent plugin on           " required

" To ignore plugin indent changes, instead use:
"filetype plugin on                 " required
"
" Brief help
" :PluginList       - lists configured plugins
" :PluginInstall    - installs plugins; append `!` to update or just
"                     :PluginUpdate
" :PluginSearch foo - searches for foo; append `!` to refresh local cache
" :PluginClean      - confirms removal of unused plugins; append `!` to
"                     auto-approve removal
" 
" see :h vundle for more details or wiki for FAQ
" Put your non-Plugin stuff after this line

"------------------------------------------------------------
" Must have options 
"
" These are highly recommended options.

" Vim with default settings does not allow easy switching between multiple files
" in the same editor window. Users can use multiple split windows or multiple
" tab pages to edit multiple files, but it is still best to enable an option to
" allow easier switching between files.

" One such option is the 'hidden' option, which allows you to re-use the same
" window and switch from an unsaved buffer without saving it first. Also allows
" you to keep an undo history for multiple files when re-using the same window
" in this way. Note that using persistent undo also lets you undo in multiple
" files even in the same window, but is less efficient and is actually designed
" for keeping undo history after closing Vim entirely. Vim will complain if you
" try to quit without saving, and swap files will keep you safe if your computer
" crashes.
set hidden
" Note that not everyone likes working this way (with the hidden option).
" Alternatives include using tabs or split windows instead of re-using the same
" window as mentioned above, and/or either of the following options:
" set confirm
" set autowriteall

" Enable syntax highlighting
syntax on
" Better command-line completion
set wildmenu
" Show partial commands in the last line of the screen
set showcmd
" Highlight searches (use <C-L> to temporarily turn off highlighting; see the
" mapping of <C-L> below)
set hlsearch
" Modelines have historically been a source of security vulnerabilities. As
" such, it may be a good idea to disable them and use the securemodelines
" script, <http://www.vim.org/scripts/script.php?script_id=1876>.
" set nomodeline

" Fold all methods according to the syntax of the file.
set foldmethod=syntax

" Enables mouse scrolling and selection in vim.
set mouse=a


"------------------------------------------------------------
" Usability options 
"
" These are options that users frequently set in their .vimrc. Some of them
" change Vim's behaviour in ways which deviate from the true Vi way, but
" which are considered to add usability. Which, if any, of these options to
" use is very much a personal preference, but they are harmless.

" Use case insensitive search, except when using capital letters
set ignorecase
set smartcase
" Allow backspacing over autoindent, line breaks and start of insert action
set backspace=indent,eol,start
" When opening a new line and no filetype-specific indenting is enabled, keep
" the same indent as the line you're currently on. Useful for READMEs, etc.
set autoindent
" Stop certain movements from always going to the first character of a line.
" While this behaviour deviates from that of Vi, it does what most users
" coming from other editors would expect.
set nostartofline
" Display the cursor position on the last line of the screen or in the status
" line of a window
set ruler
" Always display the status line, even if only one window is displayed
set laststatus=2
" Instead of failing a command because of unsaved changes, instead raise a
" dialogue asking if you wish to save changed files.
set confirm
" Use visual bell instead of beeping when doing something wrong
set visualbell
" And reset the terminal code for the visual bell. If visualbell is set, and
" this line is also included, vim will neither flash nor beep. If visualbell
" is unset, this does nothing.
set t_vb=
" Set the command window height to 2 lines, to avoid many cases of having to
" "press <Enter> to continue"
set cmdheight=2
" Display line numbers on the left
set number
" Quickly time out on keycodes, but never time out on mappings
set notimeout ttimeout ttimeoutlen=200
" Use <F11> to toggle between 'paste' and 'nopaste'
set pastetoggle=<F11>


"------------------------------------------------------------
" Indentation options 
"
" Indentation settings according to personal preference.

" Indentation settings for using 2 spaces instead of tabs.
" Do not change 'tabstop' from its default value of 8 with this setup.
set shiftwidth=2
set softtabstop=2
set expandtab

" Python tabstops are set in ~/.vim/ftplugin/python.vim

"------------------------------------------------------------
" Mappings 
"
" Type `gb` to go to the BUILD file for this file.
function! GoToBuild()
python3 << EOF
import vim
import os.path

def look_above(filepath):
  dirpath, _, basename = fn.rpartition('/')
  buildfile = os.path.join(dirpath, 'BUILD')
  return os.path.exists(buildfile), buildfile, dirpath

try:
  fn = vim.current.buffer.name
  _, _, basename = fn.rpartition('/')
  while fn:
    exists, buildfile, fn = look_above(fn)
    if exists:
      print("found!!!",buildfile)
      vim.command('edit ' + buildfile)
      vim.command('call search("\\"' + basename + '\\"")')
      break
except Exception as e:
   print("Something went wrong: " + str(e))
EOF
endfunction
nnoremap gb :call GoToBuild()<cr>

" Useful mappings
" Map Y to act like D and C, i.e. to yank until EOL, rather than act as yy,
" which is the default
nmap Y y$

" Shitty decorator function to call some function with a confirm prompt.
" Only guaranteed to work if you have two options, hence the Binary.
" :input func: Function to call if The first answer is chosen.
"              Ex: function('tabclose')
" :input text: String confirmation dialog message.
" :input options: Confirmation options. Ex: '&Yes\n&No' gives a yes or no
"                 choice.
:function! BinaryConfirmDecorator(func, text, options) 
:  if confirm(a:text, a:options, 1) == 1
:    call a:func()
:  endif
:endfunction

:function! CloseTab()
:  tabc
:endfunction
:function! ConfirmCloseTab()
:  call BinaryConfirmDecorator(function("CloseTab"), "Close Tab?", "&Yes\n&No")
:endfunction
nnoremap ,w :call ConfirmCloseTab()<cr>

" Create a function to reload vimrc. Checks if it already exists to avoid
" redefining the function during the function call.
:if !exists("*SourceVimrc")
:  function! SourceVimrc()
:    so ~/.vimrc
:  endfunction
:endif
nnoremap ,, :call SourceVimrc()<cr>


" Map ctrl-I to clang formatting
"
:function! FormatEntirePythonFile()
:  let l:lines="all"
:  py3f ~/.vim/autoformat_python.py
:endfunction
:function! FormatPythonFileForLines()
:  py3f ~/.vim/autoformat_python.py
:endfunction
" format all lines for python files.
autocmd FileType python nnoremap <silent> <S-F> :call FormatEntirePythonFile()<cr>
" Format highlighted lines for python files.
autocmd FileType python vnoremap <silent> <S-F> :call FormatPythonFileForLines()<cr>

let g:clang_format_path='clang-format-3.6'
:function! FormatFile()
:  let l:lines="all"
:  py3f ~/.vim/clang-format.py
:endfunction
" Format entire file when no lines are highlighted.
autocmd FileType cpp nnoremap <silent> <S-F> :call FormatFile()<cr>
" Format only highlighted lines.
autocmd FileType cpp vnoremap <silent> <S-F> :py3f ~/.vim/clang-format.py<cr>
" Remaps gf with .pb.h -> .proto support
function! GotoProtoDef()
:  let l:fname=expand('<cfile>')
:  let l:fname = substitute(l:fname, ".pb.h", ".proto", "")
:  execute 'edit' l:fname
endfunction
nnoremap gp :call GotoProtoDef()<CR>

function! SwitchSourceHeader()
  " Get the current file extension. To see what this command is doing,
  " see :help expand.
  let l:cur_ext=expand("%:e")
  " See if we have a source file (ending in .cpp or .cc).
  if (expand ("%:e") == "cpp" || expand ("%:e") == "cc")
    " %:t gives the basename with extension, :r trims the extension.
    " Try searching for both .h and .hpp extensions, and open the first file
    " that is found.
    let l:h_path=expand("%:r") . ".h"
    let l:hpp_path=expand("%:r") . ".hpp"
    if filereadable(h_path)
      find %:t:r.h
    elseif filereadable(hpp_path)
      find %:t:r.hpp
    endif
  else
    let l:cpp_path=expand("%:r") . ".cpp"
    let l:cc_path=expand("%:r") . ".cc"
    if filereadable(cpp_path)
      find %:t:r.cpp
    elseif filereadable(cc_path)
      find %:t:r.cc
    endif
  endif
endfunction

nmap ,s :call SwitchSourceHeader()<CR>


" Map <C-L> (redraw screen) to also turn off search highlighting until the
" next search
"nnoremap <C-L>'a0:nohl<CR><C-L>

"------------------------------------------------------------}
" Visual Elements
"
" Create a color column at 80 character width
set colorcolumn=80
" Setup solorized color scheme
syntax enable
set background=dark
" Force terminal colors to 16.
set t_Co=16
let g:solarized_termtrans = 1
let g:solarized_termcolors=16
colorscheme solarized
" Set toggle color command (between nighttime and daytime).
call togglebg#map("<F5>")

"------------------------------------------------------------}
" YouCompleteMe Config
"
" Set this for compilation flags
" let g:ycm_global_ycm_extra_conf='~/.vim/ycm_config/cpp/.ycm_extra_conf.py'
let g:ycm_global_ycm_extra_conf='~/.ycm_extra_conf.py'
" Set this to make ycm a syntastic checker
let g:ycm_register_as_syntastic_checker=0
" Set this to use CTags
" let g:ycm_collect_identifiers_from_tags_files=1
let g:ycm_goto_buffer_command = 'horizontal-split'
nnoremap <C-\> :YcmCompleter GoToDefinition<CR>
nnoremap <bar> :YcmCompleter GoToDeclaration<CR>
nnoremap ,y :YcmCompleter FixIt<CR>
nnoremap ,t :YcmCompleter GetType<CR>
nnoremap ,d :YcmCompleter GetDoc<CR>

"------------------------------------------------------------}
" Syntastic Config
"
let g:syntastic_cpp_checkers=['clang_check']
let g:syntastic_cpp_check_header=1
let g:syntastic_always_populate_loc_list = 1
let g:syntastic_check_on_open=1
let g:syntastic_enable_signs=1
let g:syntastic_error_symbol = '✗'
let g:syntastic_warning_symbol = '⚠'
let g:syntastic_python_checkers=['pep8', 'flake8']
" set statusline+=%#warningmsg#
" set statusline+=%{SyntasticStatuslineFlag()}
" set statusline+=%*gbar

"------------------------------------------------------------}
" Grepper Config
"
" Use :Grepper to open a prompt, enter your query, optionally cycle through
" list of tools, fire up the search.
" Use the current visual selection to pre-fill the prompt or start searching
" immediately.
" Use :GrepperGit, :GrepperAg, etc.. to grep with different tools built on top
" of :Grepper. (:GrepperGit is for `git grep`)
" See more examples here:
" https://github.com/mhinz/vim-grepper/wiki/example-configurations-and-mappings
"
" Can fill out a map of grepper setttings here or set them one by one below.
let g:grepper = {'operator': {'tools': ['rg']}}
"
" Enable git grep and regular grep as grepping tools.
let g:grepper.tools = ['rg', 'git', 'grep']
" Use grepper to jump to the first result that pops up in the current window.
" let g:grepper.jump = 1
" let g:grepper.next_tool = '<leader>g'
" let g:grepper.simple_prompt = 1
" let g:grepper.quickfix = 0
"
" This defines an |operator| "gs" that takes any |{motion}| and uses that
" selection to populate the search prompt. The query is quoted automatically.
" In visual mode, it uses the current selection.
nmap gs  <plug>(GrepperOperator)
xmap gs  <plug>(GrepperOperator)

"------------------------------------------------------------}
" Fugitive Config
"
" View any blob, tree, commit, or tag in the git repo with :Gedit (and
" :Gsplit, :Gvsplit, :Gtabedit, ...). Edit a file in the index and write
" to it to stage the changes. Use :Gdiff to bring up the staged version of the
" file side by side with the working tree version with vimdiff. Bring up
" git status with :Gstatus. Press `-` to add/reset a file's changes, or `p` to
" add/reset `--patch`. :Gcommit to commit. Use :Gblame to vsplit a git blame.
" :Gmove does git mv and renames teh buffer, and :Gdelete does git rm and
" deletes the file. Use :Ggrep to search teh work tree (or any arbitrary
" commit) with `git grep`. :Glog loads all previous revisions of a file into
" the quickfix list for iteration through the file's evolutions. Use :Gbrowse
" to open the web front-end for github with optional line range specified by
" visual highlights! :Git for running any arbitrary command, and :Git! will
" open the output of the command in a temp file.
" See more here: https://github.com/tpope/vim-fugitive

"------------------------------------------------------------}
" Rhubarb Config
"
" Enable vim-fugitive to use Gbrose properly.
" See more here: https://github.com/tpope/vim-fugitive
" To get this to work using git enterprise, you must add the base url here.
" let g:github_enterprise_urls = ['']

"------------------------------------------------------------}
" CtrlP Config
"
" Press <c-p> for fuzzy searching. With the quickfix window open, press <c-d>
" to switch to filename only searching.
"
" Fix the max file limit which makes things slower but prevents files from
" not being found.
let g:ctrlp_max_files=0
let g:ctrlp_types = ['buf', 'mru', 'fil']

"------------------------------------------------------------}
" CmdT Config
"
"
" The following mappings are active when the prompt has focus:
" 
"     <BS>        delete the character to the left of the cursor
"     <Del>       delete the character at the cursor
"     <Left>      move the cursor one character to the left
"     <C-h>       move the cursor one character to the left
"     <Right>     move the cursor one character to the right
"     <C-l>       move the cursor one character to the right
"     <C-a>       move the cursor to the start (left)
"     <C-e>       move the cursor to the end (right)
"     <C-u>       clear the contents of the prompt
"     <Tab>       change focus to the file listing
"
" The following mappings are active when the file listing has focus:
" 
"     <Tab>       change focus to the prompt
" 
" The following mappings are active when either the prompt or the file listing
" has focus:
" 
"     <CR>        open the selected file
"     <C-CR>      open the selected file in a new split window
"     <C-s>       open the selected file in a new split window
"     <C-v>       open the selected file in a new vertical split window
"     <C-t>       open the selected file in a new tab
"     <C-d>       delete the selected buffer
"     <C-j>       select next file in the file listing
"     <C-n>       select next file in the file listing
"     <Down>      select next file in the file listing
"     <C-k>       select previous file in the file listing
"     <C-p>       select previous file in the file listing
"     <Up>        select previous file in the file listing
"     <C-f>       flush the cache (see |:CommandTFlush| for details)
"     <C-q>       place the current matches in the quickfix window
"     <C-c>       cancel (dismisses file listing)
" 
" The following is also available on terminals which support it:
" 
"     <Esc>       cancel (dismisses file listing)
" 
" 
" Fix the max file limit which makes things slower but prevents files from
" not being found.
let g:CommandTMaxFiles=900000


"------------------------------------------------------------}
" FZF Config
"
" Map file search to <leader>f
nmap <leader>f :GFiles<cr>
