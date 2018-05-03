"""
Map in your ~/.vimrc, copy to ~/.vim/sort_includes.py and then add this:

:function! SortIncludes()
:  let l:fname=expand('%:p')
:  py3f ~/.vim/sort_includes.py
:  call input('Press any key to continue')
:  redraw!
:  execute 'edit' l:fname
:endfunction
nmap ,i :call SortIncludes()<cr>
"""
import os
import vim
import subprocess


def _find_parent_dir_with_file(directory, filename, root=None):
    """
    Recursively search in parent directory until filename is found.
    Returns the path to the first directory where filename was found.
    """
    if not root:
        root = "/"

    non_trivial_directory = lambda d: d and d != root
    file_exists_in_dir = \
        lambda d, f: os.path.exists(os.path.join(directory, filename))
    while non_trivial_directory(directory) and \
            not file_exists_in_dir(directory, filename):
        directory = os.path.dirname(directory)
    return directory if file_exists_in_dir(directory, filename) else None


def find_workspace_dir(filename):
    return _find_parent_dir_with_file(os.path.dirname(filename), "WORKSPACE")

def main():
    fname = vim.eval('l:fname')
    workspace = find_workspace_dir(fname)
    rel_fpath = os.path.relpath(fname, start=workspace)
    cmd = [
            '/mnt/flashblade/praveen/utils/include_sorter.py', rel_fpath
            ]
    print(cmd)
    if fname:
        subprocess.check_call(cmd)


if __name__ == '__main__':
    main()
