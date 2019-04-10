#!/usr/bin/python
"""
TODOs:
    * Add divergence counts from tracked branch to gitflow prompt.
    * Have cascade abort as soon as a conflict is found.
    * If you have a root branch, instead of pointing them toward origin,
      tag them as remote and print divergence from origin.
"""
import argparse
import git
import os
import sys
from collections import defaultdict
from termcolor import colored


class DagParseException(Exception):
    pass


class CascadeException(Exception):
    pass


def branch_name(branch):
    if branch is None:
        return None
    name = branch.name.lstrip('./')
    return name


def commit_delta_by_branch_name(cur_branch_name, parent_branch_name, repo):
    cmd = [
        'git',
        'rev-list',
        '--count',
        '--left-right',
        '{}...{}'.format(cur_branch_name,
                         parent_branch_name)
    ]
    try:
        delta_str = repo.git.execute(cmd)
        parent_divergence, cur_branch_divergence = [
                int(count.strip()) for count in delta_str.split()]
        return parent_divergence, cur_branch_divergence
    except Exception as e:
        print("Failed to calculate status for branch, {}, and parent branch, "
              "{}. Error:\n{}".format(cur_branch_name, parent_branch_name, e))
        return 0, 0


def commit_delta_by_branch(cur_branch, repo):
    cur_branch_name = branch_name(cur_branch)
    parent_branch_name = branch_name(cur_branch.tracking_branch())
    return commit_delta_by_branch_name(cur_branch_name,
                                       parent_branch_name,
                                       repo)


def create_branch_str(bname, active_branch, depth, parent_bname='', repo=None):
    # Create a string with whitespace representing depth.
    tabstr = ''.join(['  '] * depth)
    if depth == 0:
        branch_str = ' {branch}'.format(tabstr, branch=bname)
    else:
        branch_str = '{} |-> {branch}'.format(tabstr, branch=bname)

    # If given enough information, print the status relative to the parent.
    if parent_bname and repo:
        (cur_ahead,
         parent_ahead) = commit_delta_by_branch_name(bname,
                                                     parent_bname,
                                                     repo)
        branch_str += '  '
        if parent_ahead:
            parent_ahead_str = colored('-{}'.format(str(parent_ahead)), 'red')
        else:
            parent_ahead_str = '-{}'.format(str(parent_ahead))
        if cur_ahead:
            cur_ahead_str = colored('+{}'.format(str(cur_ahead)), 'green')
        else:
            cur_ahead_str = '-{}'.format(str(cur_ahead))
        branch_str += '({}, {})'.format(parent_ahead_str, cur_ahead_str)

    # Highlight the current branch in terminal if it is currently checked
    # out.
    active_bname = branch_name(active_branch)
    if active_bname is not None and bname == active_bname:
        branch_str += ' *(active branch)'
        branch_str = colored(branch_str, 'green')
    return branch_str


def active_branch_from_repo(repo, verbose=False):
    if repo is None:
        return None
    try:
        return repo.active_branch
    except TypeError as e:
        if verbose:
            print('Could not get active branch due to error: {}'.format(
                str(e)))
        return None


def refresh_branch(branch, repo):
    try:
        repo.remote().fetch(branch_name(branch))
        cmd = [
            'git',
            'reset',
            '--keep',
            'origin/{}'.format(branch_name(branch))
        ]
        repo.git.execute(cmd)
    except Exception as e:
        print('Failed to refresh {} with error:\n{}'.format(
            branch_name(branch),
            colored(str(e), 'red')))


def print_tree(dag, current_branch_name, depth, repo, cascade=False):
    """
    Prints the git flow dependency tree recursively.
    Ex:
     master
       |-> my_feature_branch_0
         |-> my_current_feature_branch *
    Will terminate when a branch that is not in the dag is found or when there
    are no remaining child branches for teh current branch.

    :input dag: The gitflow graph that tracks dependencies.
    :input current_branch_name: String name of the branch for the current
                                recursive call.
    :input depth: Integer indicating the depth of the current tree.
    :input repo: GitPython repo object handle for dealing with git metadata.
    :input cascade: Boolean that, when True, will cause cascaded rebases to
                    occur, rebasing each child branch onto the parent branch
                    via `git pull --rebase [parent_branch]`.
                    Defaults to False.
    """
    # Print the active branch differently
    active_branch = active_branch_from_repo(repo)
    # Do not print branch if it is not in the flow dag.
    if current_branch_name not in dag:
        return True
    if depth == 0:
        print(create_branch_str(current_branch_name, active_branch, depth))
        return print_tree(
            dag,
            current_branch_name,
            depth + 1,
            repo,
            cascade=cascade)
    # Recurively print branches in the flow dag.
    for branch in dag[current_branch_name]:
        bname = branch_name(branch)
        # Print the final branch string to terminal.
        print(
            create_branch_str(bname,
                              active_branch,
                              depth,
                              branch_name(branch.tracking_branch()),
                              repo))

        # Perform the cascaded rebase if specified.
        if (cascade):
            if repo is None:
                raise CascadeException('Must also supply a repo!')
            print('Rebasing {cur_branch} onto {parent_branch}...'.format(
                cur_branch=bname,
                parent_branch=branch_name(branch.tracking_branch())))
            repo.git.checkout(branch)
            try:
                repo.git.rebase(quiet=True)
            except git.GitCommandError as e:
                print(colored('Failed cascade due to error:', 'red'))
                print(colored(str(e), 'yellow'))
                print(colored('Aborting cascade. Please resolve conflicts on '
                              'your own.', 'red'))
                repo.git.rebase(abort=True)
                return False
        if not print_tree(dag, bname, depth + 1, repo, cascade=cascade):
            return False
    return True


def build_git_dag(r):
    """
    Build the gitflow branch dependency graph.

    :input repo: The GitPython repository handle.

    :return: A dict of key, branch name, to list, GitPython branch objects.
    """
    # Key branch name to list of child branches.
    dag = defaultdict(list)
    roots = []
    for b in r.branches:
        bname = branch_name(b)
        dag.setdefault(bname, [])
        tb = b.tracking_branch()
        if tb:
            tbname = branch_name(tb)
            if tbname.startswith('origin'):
                roots.append(tbname)
            dag[tbname].append(b)
        else:
            roots.append(bname)
    return dag, roots


def print_dag(dag, roots, repo, cascade):
    # Begin traversing the tree from the top level branches.
    for root_branch_name in roots:
        if not print_tree(
                dag,
                root_branch_name,
                depth=0,
                repo=repo,
                cascade=cascade):
            return


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cascade', default=False, action='store_true')
    parser.add_argument('--branch', default=None)
    parser.add_argument('--refresh', default=False, action='store_true')
    return parser.parse_args(argv)


def main(argv=sys.argv[1:]):
    args = parse_args(argv)
    cwd = os.getcwd()
    git_dir = os.path.join(cwd, '.git')
    if not (os.path.exists(git_dir) and os.path.isdir(git_dir)):
        raise DagParseException("Must be in git directory!")
    cwd = os.path.expanduser(os.getcwd())
    repo_dir = cwd
    repo = git.Repo(repo_dir)
    dag, roots = build_git_dag(repo)
    initial_active_branch = active_branch_from_repo(repo, verbose=True)

    if args.refresh:
        refresh_branch(initial_active_branch, repo)


    if args.branch:
        roots = [args.branch]
    elif args.cascade:
        if initial_active_branch is not None:
            roots = [branch_name(initial_active_branch)]
    print_dag(dag, roots, repo, args.cascade)
    # If performing a cascade, print out status again.
    if args.cascade:
        # If cascaded, return to the original branch.
        repo.git.checkout(initial_active_branch)

        print('Status after cascade:')
        print_dag(dag, roots, repo, False)


if __name__ == '__main__':
    sys.exit(main())
