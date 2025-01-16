#!/usr/bin/env python3

# System imports
import difflib

# Third-party imports
import isort
import vim
from isort import Config as IsortConfig
from isort.sections import FIRSTPARTY, FUTURE, LOCALFOLDER, STDLIB, THIRDPARTY
from isort.settings import IMPORT_HEADING_PREFIX

USE_AUTOPEP8 = False
USE_YAPF = False
USE_BLACK = True
if USE_AUTOPEP8:
    # Third-party imports
    import autopep8
elif USE_YAPF:
    # Third-party imports
    import yapf
    from yapf.yapflib import yapf_api
elif USE_BLACK:
    # Third-party imports
    import black
else:
    print("No formatter selected. Exiting.")

IMPORT_HEADINGS = {
    FUTURE: "Future imports",
    STDLIB: "System imports",
    THIRDPARTY: "Third-party imports",
    "ROS": "ROS imports",
    FIRSTPARTY: "Cruise imports",
    LOCALFOLDER: "Package imports",
}
IMPORT_SECTIONS = tuple([heading.upper() for heading in IMPORT_HEADINGS.keys()])
ISORT_CONFIG_OVERRIDES = dict(
    profile="black",
    quiet=True,
    line_length=99,
    combine_as_imports=True,
    use_parentheses=True,
    include_trailing_comma=True,
    multi_line_output=3,
    # Skip __init__.py because import ordering there are senstive sometimes
    extend_skip="__init__.py",
    filter_files=True,
    sections=IMPORT_SECTIONS,
    format_error="{{error}}: {{message}} If you think this is a false-alarm, use # isort: skip to disable this.",
)
# Add the prefix and update config overrides to support the heading mapping.
IMPORT_HEADINGS = {
    f"{IMPORT_HEADING_PREFIX}{key.lower()}": val for key, val in IMPORT_HEADINGS.items()
}
ISORT_CONFIG_OVERRIDES.update(IMPORT_HEADINGS)


def main():
    """
    Works by formatting the entire file and writing it back out to the buffer.
    If only formatting specific lines, operates line by line, formatting the entire file each time, and merging the formatted result back into the buffer.
    """
    if not any([USE_AUTOPEP8, USE_YAPF, USE_BLACK]):
        return 0
    # Get the current text.
    buf = vim.current.buffer

    # Load the lines variable in vimrc if set.
    # This deals with the case where lines == "all"
    if int(vim.eval('exists("l:lines")')):
        lines = vim.eval("l:lines")
        start, end = None, None
    else:
        # Determine range to format.
        lines = [int(vim.current.range.start), int(vim.current.range.end + 1)]
        start, end = lines[0], lines[1]
        assert not USE_BLACK, "Black only formats the entire file at once, not specific lines."
    text = "\n".join(buf)
    yapf_options = {
        "unformatted_source": text,
        "style_config": {
            "based_on_style": "pep8",
            "dedent_closing_brackets": "false",
            "split_all_top_level_comma_separated_values": "true",
        },
    }
    black_options = {"line_length": 99}

    autopep8_options = {
        "aggressive": 1,
        "max_line_length": 79,
    }
    # Use start, end indices only for black formatter.
    if lines != "all":
        autopep8_options["line_range"] = lines
        yapf_options["lines"] = [(start, end)]

    fixed_code = None
    if USE_YAPF:
        fixed_code, changed = yapf_api.FormatCode(**yapf_options)
    if USE_AUTOPEP8:
        fixed_code = autopep8.fix_code(text, options=autopep8_options)
    if USE_BLACK:
        # Black does not format specific lines unfortunately.
        fixed_code = black.format_str(text, mode=black.Mode(**black_options))
    fixed_code = isort.api.sort_code_string(
        code=fixed_code, config=IsortConfig(**ISORT_CONFIG_OVERRIDES)
    )

    assert fixed_code, "No output from autoformatter!"

    line_arr = fixed_code.split("\n")[:-1]
    # Execute the sequence of changes.
    sequence = difflib.SequenceMatcher(None, vim.current.buffer, line_arr)
    for op in reversed(sequence.get_opcodes()):
        if op[0] != "equal":
            vim.current.buffer[op[1] : op[2]] = line_arr[op[3] : op[4]]


if __name__ == "__main__":
    main()
