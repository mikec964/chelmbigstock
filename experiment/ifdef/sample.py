# for python 2.7
from glblconf import PARALLEL

"""
This code demonstrates how to use PARALLEL()
"""

# sample 1
# directly check PARALLEL in the code
def func1():
    print 'Entering func1'
    if PARALLEL():
        print 'PARALLEL'
    else:
        print 'NON parallel'
    print 'Exiting func1'

# sample 2
# define function conditinally
if PARALLEL():
    def f_cond2():
        print 'PARALLEL f_cond'
else:
    def f_cond2():
        print 'NON parallel f_cond'

def func2():
    print 'Entering func2'
    f_cond2()
    print 'Exiting func2'

# sample 3
# real #ifdef; I don't reccomend, though.

def preprocessor(code, is_parallel):
    """
    This is a preprocessor for python scripts.
    Takes a python code as string and takes care of '#ifdef', '#else', and
    '#endif'.
    """
    st_regular = 0
    st_if = 1
    st_else = 2
    do_add = True
    
    delimiter = '\n'
    lines = code.split(delimiter)
    state = st_regular
    processed = []
    for line in lines:
        if state == st_if:
            if line.startswith('#else'):
                do_add = not do_add
                state = st_else
            elif line.startswith('#endif'):
                state = st_regular
            else:
                if do_add:
                    processed.append(line)
        elif state == st_else:
            if line.startswith('#endif'):
                state = st_regular
            else:
                if do_add:
                    processed.append(line)
        else:
            if line.startswith('#ifdef'):
                words = line.split()
                if len(words) >= 2 and words[1] == 'PARALLEL':
                    do_add = is_parallel
                    state = st_if
                else:
                    processed.append(line)
            else:
                processed.append(line)

    return delimiter.join(processed)

# this is the func3() code in string
code = """
def func3():
    print 'Entering func3'
#ifdef PARALLEL
    print 'PARALLEL preprocessor'
#else
    print 'NON parallel preprocessor'
#endif
    print 'Exiting func3'
"""

# instantiate func3()
exec( preprocessor(code, PARALLEL()) )
