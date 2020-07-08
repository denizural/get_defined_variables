#!/usr/bin/env python
# TODO:
# ======
# check for the nested expressions: Eg. val ${nested_${var}}
# Maybe match.groups() can be used for catching nested expressions
# Ask Paul about what to do with the nested variables.

import re
import argparse
import os

# ===
# command line parsing
# ===
parser = argparse.ArgumentParser(description='command-line argument parser')
parser.add_argument('script_path', type=str, \
    help='shell script to be parsed')
parser.add_argument("--verbose", help="increase output verbosity",\
    action="store_true")
args = parser.parse_args()


if not os.path.isfile(args.script_path):
    print(f"ERROR: file: {args.script_path} does not exist")
    import sys
    sys.exit()

#print(args.script_path)


def extract_var_name(line, verbose=False):
    """    
    Extracts the list of shell variables from the given line
    
    Parameters
    ----------    
    - line : string
          Contains a line from the shell script
          
    - debug: boolean
          If it is True then the function will print more information
    
    Returns
    -------
    - variables: list of strings
          Contains the variables names    
    """
    # number of variables on the current line
    var_count = line.count('$')
    brace_count = line.count('{')
    variables = list()
    non_alnum = r"[^0-9a-zA-Z_]"   # regex for non-alphanumerics
    
    # starting positions of the $ sign
    starts = [m.start() for m in re.finditer('\$', line)]

    # check if we are on a commented line. If '#' is encountered before the 
    # first occurence of '$' then ignore this line
    if '#' in line[:starts[0]]:
        #print('commented line')
        #print(f'>>> {line}')
        return None 
    
    # go for each variable and check their format and extract them
    # possible candidates:
    # ${var}
    # $var
    # ${nested_${var}}    --> nested variable [TODO]
    for i in range(var_count):
        # 1) check for ${var}    
        if line[starts[i]+1] == '{':
            var_start = starts[i]+2
            var_end = line.find('}', var_start)  
        
        # 2) check for $var
        elif line[starts[i]+1].isalpha():
            var_start = starts[i]+1
            # search a first non-alphanumeric character from current position
            # to the end of the line. This is the end of the variable name
            match = re.search(non_alnum, line[var_start : ])
            var_end = var_start + match.start()

            #var_end = line.find(' ', var_start)
            # if there is no space, eg. end of the line
            #if var_end == -1:
            #    var_end = len(line)-1

        # check for function arguments: $numeric, eg. $1, $2
        elif line[starts[i]+1].isnumeric():
            #print("debug: numeric found")
            continue
        
        # check for $(...) -> shell commands
        elif line[starts[i]+1] == '(':
            #print("debug: ( found")
            continue

        # space after $
        elif line[starts[i]+1] == ' ':
            #print("debug: space found after $")
            continue

        # some other strange non-alphanumeric character is found
        elif (line[starts[i]+1]).isalnum() == False:
            #print(f"debug: some other strange character after $ is found: {line[starts[i]+1]}")
            continue
            
        # extract the variable from the line
        var = line[var_start : var_end]
        
        variables.append(var)

        
    if verbose == True:
        print(f"::: found {var_count} variables on the line")
        if line[-1] == '\n':
            print(f"{line}", end='')
        else: 
            print(f"{line}")
        
        markers = list(' ' * len(line))
        for start in starts:
            markers[start] = '^'
        mark_line = ''.join(markers)
        print(f"{mark_line}")
        
        print(f"{variables}")
        # print(f"found {brace_count} braces on the line") 
        print()
    
    return variables
            


vars_list = list()
vars_set = set()

# scan the lines in the script and search for the variable patterns 
with open(args.script_path) as script:
    for line in script:
        match_1 = re.search(r"\$\{.*\}", line)    # ${var}
        match_2 = re.search(r"\$.*", line)        # $var 
        
        # if match_1 != None:     #or match_2 != None:
        if match_1 != None or match_2 != None:
            
            # extract variable names
            vars_cur_line = extract_var_name(line, verbose=args.verbose)
            if vars_cur_line is not None:
                vars_list.extend(vars_cur_line)

    #print(vars_list)
    #print(len(vars_list))
    #print(set(vars_list))    # breaks the order unfortunately
    #print(len(set(vars_list)))
    
    #for var in set(vars_list):
    #    print(var)

    # remove the duplicates while still preserving the order in the list
    vars_list_no_duplicate = sorted(set(vars_list), key=lambda x: vars_list.index(x))
    #print('\n\nlist of variables:')
    for var in vars_list_no_duplicate:
        print(var)

