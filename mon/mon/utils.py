from subprocess import check_output


def get_file_data(filename, firstline=False, as_lines=False):
    '''Read contents of a file and return as string. If firstline is true,
    only the first line of the file is returned.

    '''

    with open(filename, 'r') as f:
        if firstline:
            s = f.readline()
        else:
            s = f.read()

    if as_lines:
        return s.split('\n')
    else:
        return s


def get_cmd_data(cmd, firstline=False, as_lines=False):
    '''Return output of a command. 

    :param cmd: The command with arguments as a list.
    :param firstline: Only return first line of output.
    :param as_lines: Split up output into an array of lines.'''
    
    output = check_output(cmd).decode('utf-8', errors='ignore')

    if firstline:
        return output.split('\n')[0]
    else:
        if as_lines:
            return output.strip().split('\n')
        else:
            return output
