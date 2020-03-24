#!/usr/bin/env python3
import autopep8
import yapf
from yapf.yapflib import yapf_api
import difflib
import json
import os
import subprocess
import vim

USE_AUTOPEP8 = False
USE_YAPF = True


def main():
    # Get the current text.
    buf = vim.current.buffer
    text = '\n'.join(buf)

    # Determine range to format.
    lines = None
    lines = [int(vim.current.range.start + 1), int(vim.current.range.end + 1)]
    # Load the lines variable in vimrc if set.
    if int(vim.eval('exists("l:lines")')):
        lines = vim.eval('l:lines')
    yapf_options = {
            'unformatted_source': text,
            'style_config': {
                'based_on_style': 'pep8',
                'dedent_closing_brackets': 'false',
                'split_all_top_level_commas_separated_values': 'true',
            }
    }

    autopep8_options = {
        'aggressive': 1,
        'max_line_length': 79,
    }
    if (lines != 'all'):
        autopep8_options['line_range'] = lines
        yapf_options['lines'] = [(lines[0], lines[1] + 1)]

    fixed_code = None
    if USE_YAPF:
        fixed_code, changed = yapf_api.FormatCode(**yapf_options)
    if USE_AUTOPEP8:
        fixed_code = autopep8.fix_code(text, options=autopep8_options)
    if not fixed_code:
        print('No output from autoformatter!')
    else:
        line_arr = fixed_code.split('\n')[:-1]
        # Execute the sequence of changes.
        sequence = difflib.SequenceMatcher(None, vim.current.buffer, line_arr)
        for op in reversed(sequence.get_opcodes()):
            if op[0] is not 'equal':
                vim.current.buffer[op[1]:op[2]] = line_arr[op[3]:op[4]]


if __name__ == '__main__':
    main()
