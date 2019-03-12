#!/usr/bin/python
import argparse
import git
import os
import sys
from collections import defaultdict


class DagParseException(Exception):
    pass


class CascadeException(Exception):
    pass


def branch_name(branch):
    name = branch.name.lstrip('./')
    origin_str = 'origin/'
    if name.startswith(origin_str):
        name = name[len(origin_str):]
    return name


def print_tree(dag, key, depth=0, rebase=False, repo=None):
    tabstr = ''.join(['  ']*depth)
    if key in dag:
        for branch in dag[key]:
            bname = branch_name(branch)
            print('{}|->{branch}'.format(tabstr, branch=bname))
            if (rebase):
                if repo is None:
                    raise CascadeException('Must also supply a repo!')
                repo.git.checkout(branch)
                repo.git.pull()
            print_tree(dag, bname, depth+1, rebase=rebase, repo=repo)


def build_git_dag(r):
    # Key branch name to list of child branches.
    dag = defaultdict(list)
    roots = []
    for b in r.branches:
        bname = branch_name(b)
        tb = b.tracking_branch()
        if tb:
            tbname = branch_name(tb)
            if tbname == bname:
                roots.append(tbname)
                continue
            dag[tbname].append(b)
        dag.setdefault(bname, [])
    return dag, roots


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cascade', default=False, action='store_true')
    parser.add_argument('--branch', default=None)
    return parser.parse_args(argv)


def main(argv=sys.argv[1:]):
    args = parse_args(argv)
    cwd = os.getcwd()
    git_dir = os.path.join(cwd, '.git')
    if not(os.path.exists(git_dir) and os.path.isdir(git_dir)):
        raise DagParseException("Must be in git directory!")
    cwd = os.path.expanduser(os.getcwd())
    repo_dir = cwd
    repo = git.Repo(repo_dir)
    dag, roots = build_git_dag(repo)

    if args.branch:
        roots = [args.branch]
    for key in roots:
        print(' {key}'.format(key=key))
        print_tree(dag, key, depth=1, rebase=args.cascade, repo=repo)


if __name__ == '__main__':
    sys.exit(main())
