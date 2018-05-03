
def _check_output(command, *args, cwd=None, env=None, **kwargs):
    """
    Wrapper around subprocess.check_output that logs commands, decodes output
    as utf-8, removes trailing whitespace, and catches KeyboardInterrupts.
    """
    try:
        output = subprocess.check_output(
                command, *args, cwd=cwd, env=env, **kwargs)
        return output.decode("utf-8").rstrip()
    except KeyboardInterrupt:
        fatal("Caught keyboard interrupt. Exiting.")



def _check_call(command, *args, cwd=None, env=None, **kwargs):
    """
    Wrapper around subprocess.check_call that logs commands and catches
    KeyboardInterrupts.
    """
    try:
        subprocess.check_call(command, *args, cwd=cwd, env=env, **kwargs)
    except KeyboardInterrupt:
        fatal("Caught keyboard interrupt. Exiting.")


def _bazel_query(subject, query_options, workspace_root):
    return _check_output(
        ["bazel", "query"] + query_options + [subject],
        cwd=workspace_root).split()

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


def _find_build_dir(filename):
    return _find_parent_dir_with_file(os.path.dirname(filename), "BUILD")


def _find_package(workspace_root, build_dir):
    return "//{}".format(os.path.relpath(build_dir, workspace_root))


def _find_file_targets(
        relative_filename, workspace_root):
    """
    Perform a Bazel query to find all targets that directly depend on a file.
    """
    assert (workspace_root != []), (
        "Prevent this case as os.path.join will split the string up very "
        "strangely in this circumstance."
    )
    build_dir = _find_build_dir(
        os.path.join(workspace_root, relative_filename)
    )
    package = _find_package(workspace_root, build_dir)
    escaped_package = _escape_bazel_target("{}/...".format(package))
    package_query = "rdeps({}, {}, 1))".format(
        escaped_package, relative_filename
    )
    subject = "kind('rule', {}".format(package_query)
    return _bazel_query(subject, [], workspace_root)


def _escape_bazel_target(target):
    """
    Wraps a target string in `'` so that `+`s in a target's name do not break
    our queries.
    """
    return "'{}'".format(target)


def _escape_bazel_targets(targets):
    """
    Escapes an entire list of targets using `_escape_bazel_target`.
    """
    return [_escape_bazel_target(t) for t in targets]


def main():
    fname = vim.eval('l:fname')
    workspace = find_workspace_dir(fname)
    rel_fpath = os.path.relpath(fname, start=workspace)
    targets = _find_file_targets(rel_fpath, workspace)
    for target in targets:
        cmd = ['/mnt/flashblade/praveen/utils/freshen_deps.py', target]
        print('Executing command {}'.format(' '.join(cmd)))
        subprocess.check_call(cmd)


if __name__ == '__main__':
    main()
