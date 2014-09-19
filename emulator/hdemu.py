#!/usr/bin/env python

"""
Hadoop stream API emulator for python mapper/reducer
"""

import subprocess as sp


def run_pipeline(commands):
    """
    Runs commands and connects the stdout of a command with the stdin of the next.
    Arguments:
        commands: list of command. command is the same format as the 'args' argument
        of subprocess.Popen().
    Return:
        List of processes
    """
    previous_p = None
    ps = []
    for command in commands:
        next_stdin = None if previous_p == None else previous_p.stdout
        p = sp.Popen(command, stdin = next_stdin, stdout = sp.PIPE)
        ps.append(p)
        if previous_p:
            previous_p.stdout.close()   # Allow previouse process to receive a SIGPIPE
                                        # if current process exits.
        previous_p = p
    
    return ps


commands = [
    ['python', 'TextInputFormat.py'],
    ['python', 'Shuffle.py']
    ]

ps = run_pipeline(commands)
output = ps[-1].stdout
for line in output:
    print line,
