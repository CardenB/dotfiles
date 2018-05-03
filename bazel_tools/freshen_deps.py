#!/usr/bin/python

import argparse
import shlex
import subprocess
import re
import sys
import os
import tempfile
from parse_workspace import parse_workspace_for_bind

BUILDOZER_PATH = '/mnt/flashblade/praveen/utils/buildozer'
BUILDIFIER_PATH = '/mnt/flashblade/praveen/utils/buildifier'

VISIBLE_PACKAGES = ' //base/... union //bin/... union //build/... union //calibration/... union //ci/... union //clams/... union //continuum/... union //data/... union //doc/...   union //fakeros/... union //firmware/... union //infra/...  union //kraken/... union //labeling/... union //lidar/... union //localization/... union //logger/...  union //mapping/... union //mapreduce/... union //omlet/... union //packages/... union //pipedream/... union //prediction/... union //public/... union //radar/... union //rostask/... union //ros_utilities/... union //scripts/... union //sim/... union //stdr_libraries/... union //teleop/... union //tflight/... union //third_party/... union //tools/... union //vehicle/... union //vis/... union //vision/... union //web_apps/...'

external_dep_converter = {
    '@eigen_archive//:eigen': ['//external:eigen'],
    '@boost_repo7//:optional': ['//external:boost_optional'],
    '@gmock_repo//:gtest': ['//base/test/gtest:gtest_main'],
    '@gmock_repo//:gmock': ['//external:gmock'],
}


def extract_include_path_if_possible(line):
    '''
    For an include #include "abc/xyz" or #include <abc/xyz> returns abc/xyz. Can return None if nothing was found.
  '''
    result = re.search('#include[ ]+[<"](.*)[">].*', line)
    if result is None or len(result.groups()) == 0:
        return None
    return result.groups()[0]


def combine_patterns(a, b):
    if a is None:
        return b
    if b is None:
        return a
    return a + "|" + b


def replace_last_occurence_of_character(s, original_character, new_character):
    '''Given a string s, will try to replace last occurrence of original_character with new_character. If there is no occurrence of that character, returns s unchanged'''
    last_occurrence_of_original_character = s.rfind(original_character)
    if (last_occurrence_of_original_character == -1):
        return s

    return s[0:last_occurrence_of_original_character] + new_character + s[
        last_occurrence_of_original_character + len(original_character):
    ]


def escape_include_path(include_path):
    return '(' + include_path + ')'


def get_include_matching_patterns(include_path):
    ''' Given an include path, e.g. 'foo/bar/baz.h' (without the quotes), will generate all the needed match patterns for this.'''
    include_path_with_colon = replace_last_occurence_of_character(
        include_path, '/', ':'
    )
    # Done to deal with case "munkres.h" which should have a hdr "src/munkres.h"
    if not os.path.dirname(include_path):
        include_path_with_src = 'src/' + include_path
        include_path = combine_patterns(
            escape_include_path(include_path),
            escape_include_path(include_path_with_src)
        )

    return combine_patterns(
        escape_include_path(include_path),
        escape_include_path(include_path_with_colon)
    )


def get_new_bazel_query(target):
    visibility = VISIBLE_PACKAGES
    if target:
        visibility = target
    return [
        'bazel', 'query', '--deleted_packages=log_tests,experimental',
        "'visible(%s, " % visibility
    ]


def add_include_patterns(query, include_pattern):
    return query + [
        'attr("hdrs", "%s", %s)' % (include_pattern, VISIBLE_PACKAGES)
    ]


def terminate_bazel_query(query):
    return query + [")'"]


def is_proto_include_path(include_path):
    return include_path.endswith('.pb.h') and 'caffe.pb.h' not in include_path


def add_proto_query(query, proto_include_path):
    include_path_with_colon = replace_last_occurence_of_character(
        proto_include_path, '/', ':'
    )

    query = query + [
        ' union (deps(%s,1) except %s) ' %
        (include_path_with_colon, include_path_with_colon)
    ]
    return query


# Transforms //foo:bar to foo or //foo/bar to foo/bar
def get_target_relpath(target):
    target = target.replace('//', '')
    if (':' in target):
        return target.split(':')[0]
    else:
        return target


def run(source_files, target=None, remove_deps=False):

    include_paths = set()
    proto_include_paths = set()
    for source_file in source_files:
        for l in open(source_file):
            possible_include_path = extract_include_path_if_possible(l)
            if not possible_include_path:
                continue
            # Skipping includes without forward slash helps prevent dealing
            # with system includes such as vector, map, etc...
            # We need to ignore munkres.h, however so that we can find the dep.
            if (
                '/' not in possible_include_path
                and possible_include_path != 'munkres.h'
            ):
                continue

            if is_proto_include_path(possible_include_path):
                proto_include_paths.add(possible_include_path)
            else:
                include_paths.add(possible_include_path)
    print('Include paths: ' + str(include_paths))
    current_pattern = None
    for include_path in include_paths:
        current_pattern = combine_patterns(
            current_pattern, get_include_matching_patterns(include_path)
        )

    query = get_new_bazel_query(target)
    query = add_include_patterns(query, current_pattern)

    for proto_include_path in proto_include_paths:
        query = add_proto_query(query, proto_include_path)

    query = terminate_bazel_query(query)
    print('')
    print(' '.join(query))
    print('')

    temp_file = tempfile.NamedTemporaryFile()
    print('Writing to: ' + temp_file.name)
    os.system(
        ' '.join(query) + ' | sort |  while read f; do echo $f; done > ' +
        temp_file.name
    )

    print('')
    all_deps = [l.strip() for l in open(temp_file.name)]
    deps = []
    # Search for external deps, then only add them if there is a conversion
    # available.
    for dep in all_deps:
        if '@' in dep:
            if dep in external_dep_converter:
                ext_deps = external_dep_converter[dep]
                deps.extend(ext_deps)
            else:
                print(
                    'Found {} as a dependency, but did not have an entry in the converter.'.
                    format(dep)
                )
        else:
            deps.append(dep)
    print('Deps before: ' + str(deps))
    deps = filter(lambda x: x != target, deps)
    # Don't allow the target to be in its own dependencies
    if target and ':' in target:
        target_name_with_colon = target[target.find(':'):]
        print target_name_with_colon
        deps = filter(lambda x: x != target_name_with_colon, deps)
        print 'Deps after: ' + str(deps)

    # Use key_value_store instead of key_value_store_base.
    if target:
        fixed_deps = []
        for d in deps:
            if d == '//vision/data:key_value_store_base' and not '//vision/data:' in target:
                d = '//vision/data:key_value_store'
            elif d == '//vision/detection:detection_classifier_internal':
                d = '//vision/detection:detection_classifier'
            elif '@eigen_archive' in d:
                if 'eigen_em' in d:
                    continue
                d.replace('@eigen_archive//', '//external')
            print 'kv base dep: ' + d
            fixed_deps.append(d)
        deps = fixed_deps

    # For now, assume _proto deps are _proto_cc.
    if target:
        deps_fixed = []
        for d in deps:
            if d.endswith('_proto'):
                d = d + '_cc'
            deps_fixed.append(d)
        deps = deps_fixed
    print 'deps after: ' + str(deps)

    if target:
        if remove_deps:
            dozer_cmd = ' '.join([
                BUILDOZER_PATH, '"' + 'remove deps' + '"', target
            ])
            print dozer_cmd
            os.system(dozer_cmd)
        dozer_cmd = ' '.join([
            BUILDOZER_PATH, '"' + 'add deps ' + ' '.join(deps) + '"', target
        ])
        relpath = get_target_relpath(target)
        buildifier_cmd = ' '.join([BUILDIFIER_PATH, relpath + '/BUILD'])

        os.system(dozer_cmd)
        os.system(buildifier_cmd)

    deps_with_quotes = ['"' + d + '",' for d in deps]
    print 'deps = [' + '\n'.join(deps_with_quotes) + ']'
    print ''


def parse_buildozer_print_result(result):
    result = result.strip()
    result = result.replace('[', '')
    result = result.replace(']', '')
    chunks = result.split(' ')
    return chunks


def get_src_files_for_target(target):
    target_relpath = get_target_relpath(target)
    print 'target relpath: ' + target_relpath
    all_src_files = []
    for src_type in ['hdrs', 'srcs']:
        tmp_file = '/tmp/srcs.txt'
        cmd = [
            BUILDOZER_PATH,
            "'print %s'" % src_type, target, ' > ', tmp_file
        ]
        cmd = ' '.join(cmd)
        print cmd
        os.system(cmd)
        result = parse_buildozer_print_result(
            ' '.join([l.strip() for l in open(tmp_file)])
        )
        print 'result: ' + str(result)
        if 'missing' in str(result):
            continue
        all_src_files.extend(result)

    return [target_relpath + '/' + f for f in all_src_files]


def get_deps_for_target(target):
    tmp_file = '/tmp/deps.txt'
    cmd = ' '.join([BUILDOZER_PATH, "' print deps '", target])
    os.system(cmd + ' > ' + tmp_file)
    deps = parse_buildozer_print_result(
        ' '.join([l.strip() for l in open(tmp_file)])
    )
    deps = filter(lambda x: '(missing)' not in x, deps)
    return deps


def print_dep_diff_summary(old_deps, new_deps):
    old_deps = set(old_deps)
    new_deps = set(new_deps)

    dep_sets_by_name = {'Old deps': old_deps, 'New deps': new_deps}
    for name, dep_set in dep_sets_by_name.iteritems():
        print name
        for dep in sorted(list(dep_set)):
            print '\t' + dep
        print ''

    added_deps = new_deps.difference(old_deps)
    print 'Added deps:'
    for dep in sorted(list(added_deps)):
        print '\t' + dep


def parse_args():
    parser = argparse.ArgumentParser(
        description=
        'Tool to add missing dependencies to a target. Currently only supports cc_library|cc_binary; must be run from WORKSPACE ROOT!'
    )
    parser.add_argument(
        'target',
        help=
        'Bazel target to update dependencies for. Targets must begin with // and have a : in them.'
    )
    parser.add_argument(
        '--remove_deps',
        default=False,
        action="store_true",
        help=
        'If specified, will also remove dependencies that are determined to be unneeded. The default (false) behavior is to only add missing dependencies.',
        required=False
    )

    args = parser.parse_args()
    return args


def start():
    args = parse_args()
    print 'args.remove_deps: ' + str(args.remove_deps)
    if True:
        if not os.path.isfile('WORKSPACE'):
            print 'Tool must be run from workspace root'
            return
        global external_dep_converter
        global VISIBLE_PACKAGES
        (external_bind_dep_converter,
         external_visibility_pkgs) = parse_workspace_for_bind('WORKSPACE')
        external_dep_converter.update(external_bind_dep_converter)
        VISIBLE_PACKAGES += ' '.join([
            ' union {}'.format(pkg) for pkg in external_visibility_pkgs
        ])
        first_arg = args.target
        has_target = ('//' in first_arg and ":" in first_arg)
        if not has_target:
            print 'Tool only accepts targets that begin with // and have a : in them'
            return
        target = None
        if has_target:
            target = first_arg
            init_deps = get_deps_for_target(target)
            source_files = get_src_files_for_target(target)
        else:
            source_files = sys.argv[1:]
        print 'Using source files: ' + str(source_files)
        run(source_files, target, args.remove_deps)

        final_deps = get_deps_for_target(target)
        print_dep_diff_summary(init_deps, final_deps)


if __name__ == "__main__":
    start()
