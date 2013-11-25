#!/usr/bin/env python
"""
Script for cleaning up latex files, for example for a final submission of
latex code for a publication.
"""
import re
import argparse
import os

__author__ = "Christoph Dann <cdann@cdann.de>"
__license__ = "MIT"

remove_commands = [("todo",1)]
remove_comments = True

input_file = "paper.tex"

parser = argparse.ArgumentParser("texclean.py",
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog='''\
Example:
  ./texclean.py paper.tex -r -o cleaned.tex --remove-commands todo needsfix 2 XX
Executing this line will take the source of paper.tex and recursively inserting all other files included with the \\input command and store the output in cleaned.tex.
It will also remove all comments from the output and delete all occurances of the commands: todo, needsfix and XX. While todo and XX take only one argument,
nedsfix takes two (e.g. \\needsfix{person}{issue}).''')
parser.add_argument("input", help="input tex-file to clean up")
parser.add_argument("-o", "--output", help="cleaned up content is stored in here, if omitted, the content in printed to the standard output", type=str, default=None)
parser.add_argument("-r", "--recursive-input", default=False, action="store_true",
                    help="merge all files included with the \\input command into a single file")
parser.add_argument("-k", "--keep-comments", default=False, action="store_true",
                    help="do not remove comments. Otherwise all comments introduced by %% are removed from the output")
parser.add_argument("--remove-commands", nargs="*",
                    help="""commands which should be removed from the output.
                    You can specify the number of arguments of a command by appending it after the command name.""")


def not_comment_only_line(line):
    return not re.match("\s*%.*", line, re.IGNORECASE)


def process_file(filename, remove_commands, remove_comments=True, recursive_input=True):

    with open(filename) as f:
        lines = f.readlines()

    if remove_comments:
        lines = filter(not_comment_only_line, lines)

        lines = [re.sub(r"(?<!\\)%.*$", "", l, flags=re.IGNORECASE) for l in lines]

    content = "".join(lines)

    for command, param in remove_commands:
        regex = r"\\{comm}{paren}".format(comm=command, paren=r"\{.*?\}" * param)
        content = re.sub(regex, "", content)

    def rec_input(match):
        fn = match.group("fn")
        if "." not in fn:
            fn += ".tex"
        return process_file(fn, remove_commands, remove_comments, recursive_input)

    if recursive_input:
        content = re.sub(r"\\input\{(?P<fn>.*?)\}", rec_input, content, flags=re.IGNORECASE)
    r"\\input\{(?P<fn>.*?)\}"
    return content

if __name__ == "__main__":
    args = parser.parse_args()
    input_file = args.input
    if args.remove_commands is not None:
        l = args.remove_commands
        i = 0
        while(i < len(l)):
            if i + 1 < len(l) and l[i+1].isdigit():
                remove_commands.append((l[i], l[i+1]))
                i+= 2
            else:
                remove_commands.append((l[i], 1))
                i += 1

    content = process_file(args.input, remove_commands, not args.keep_comments,
                           args.recursive_input)
    if args.output is None:
        print content
    else:
        with open(args.output, "w") as f:
            f.write(content)
