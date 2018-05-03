import argparse
import collections
import os
import re
import sys

bind_name_re = re.compile('\s*name\s*=\s*"(\w+)".*')
bind_target_re = re.compile('\s*actual\s*=\s*"(.+)".*')

invalid_names = set(['liblinear', 'tensorflow_cc', 'eigen_em', 'nanogui_em'])


def get_visibility_pkg(target):

    # Skip empty targets.
    if not target.lstrip('//'):
        return None
    if ':' in target:
        tgt_split = target.split(':')[0]
        if not tgt_split.endswith('/'):
            tgt_split += '/'
        return '{}...'.format(tgt_split)
    else:
        return target


def parse_workspace_for_bind(workspace_file):
    lines = []
    with open(workspace_file, 'r') as f:
        lines = [line.strip() for line in f.readlines()]
    i = 0
    actual_to_external_map = collections.defaultdict(list)
    visibility_targets = set()
    while i < len(lines):
        l = lines[i]
        # Move through the bind target to parse.
        if l == 'bind(':
            i += 1
            name_line = lines[i]
            i += 1
            target_line = lines[i]
            name_match = bind_name_re.match(name_line)
            target_match = bind_target_re.match(target_line)

            if ((not name_match or not target_match) or (
                len(name_match.groups()) < 1 or len(target_match.groups()) < 1
            )):
                print((
                    'Had trouble parsing name and target from bind!\n'
                    'name_line: {}\ntarget_line: {}'
                ).format(name_line, target_line))
                continue
            name = name_match.groups(0)[0]
            target = target_match.groups(0)[0]

            if name in invalid_names:
                print('Skipping invalid target: {}'.format(name))
                continue

            visibility_pkg = get_visibility_pkg(target)
            if visibility_pkg:
                visibility_targets.add(visibility_pkg)
            actual_to_external_map[target].append('//external:{}'.format(name))
        i += 1
    return actual_to_external_map, visibility_targets


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    if not os.path.isfile('WORKSPACE'):
        print 'Tool must be run from workspace root'
        return 1
    converter, visibility_pkgs = parse_workspace_for_bind('WORKSPACE')
    return 0


if __name__ == '__main__':
    sys.exit(main())
