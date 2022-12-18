"""A TeX-aware inline calculator/expression evaluator for Vim

Toby Thurston -- 23 Nov 2022

This is how I bind this to a key in MacVim.  Since I bind this to a key used by
the macmenus this has to be in .gvimrc and you have to nop the macmenu key
first.

    macmenu Edit.Font.Bigger key=<nop>
    imap <D-=> <ESC>:pyf ~/python-vim-proust/proust.py<CR>i

The first line <nop>s the <Apple-=> key that is normally bound (by MacVim
itself) to Edit.Font.Bigger.  The second line maps <Apple-=> (written as <D-=>)
to the command sequence to run this filter.

  <ESC>                                   come out of insert mode
  :pyf ~/python-vim-proust.proust.py<CR>  run this filter
  i                                       go back into insert mode

"""
# pylint: disable=C0103

import datetime
import fractions
import itertools
import re
from math import (acos, asin, atan, atan2, ceil, comb, cos, degrees, e, exp,
                  fabs, factorial, floor, gcd, hypot, log, perm, pi, radians,
                  sin, sqrt, tan)


def dow(isodate=None):
    '''Day of the week please

    >>> w = 'Monday Tuesday Wednesday Thursday Friday Saturday Sunday'.split()
    >>> dow() in w
    True
    >>> dow(1) in w
    True
    >>> dow('2022-12-25')
    'Sunday'


    '''
    if isodate is None:
        return datetime.date.today().strftime("%A")

    try:
        n = int(isodate)
    except ValueError:
        pass
    else:
        today = datetime.date.today()
        diff = datetime.timedelta(days=n)
        return (today + diff).strftime("%A")
  
    return datetime.datetime.strptime(isodate, "%Y-%m-%d").strftime("%A")


def date(n=0):
    ''' Today +/- n days
    date(120) = 2023-03-25 
    '''
    today = datetime.date.today()
    diff = datetime.timedelta(days=n)
    return (today + diff).isoformat()

def base(isodate=None):
    '''
    >>> base('2022-01-01')
    738156
    '''
    if isodate is None:
        return datetime.date.today().toordinal()
    return datetime.datetime.strptime(str(isodate), "%Y-%m-%d").toordinal()



def lcm(a, b):
    return abs(a * b) / gcd(a, b)


def ifactors(n):
    "Iterate through the factors"
    f = 2
    f_cycle = itertools.cycle([4, 2, 4, 2, 4, 6, 2, 6])
    increments = itertools.chain([1, 2, 2], f_cycle)
    for incr in increments:
        if f * f > n:
            break
        while n % f == 0:
            yield f
            n //= f
        f += incr
    if n > 1:
        yield n


def factors(n):
    '''find the factors of n and return a list... very slowly
    >>> factors(12345)
    [3, 5, 823]
    >>> factors(128)
    [2, 2, 2, 2, 2, 2, 2]
    '''
    return list(ifactors(n))


phi = 1.61803398875


def sind(x):
    """
    Sine of x in degrees.

    >>> abs(sind(45)-sqrt(1/2))<1e-15
    True
    """
    return sin(radians(x))


def cosd(x):
    '''Cosine of x in degrees

    >>> abs(cosd(30)-sqrt(3/4))<1e-15
    True
    '''
    return cos(radians(x))


def tand(x):
    '''Tangent of x in degress
    '''
    return sind(x) / cosd(x)


def angle(a, b):
    '''Like MP
    >>> angle(4,3)
    36.8699
    '''
    return round(degrees(atan2(b, a)), 5)


def dir(t):
    '''from MP
    >>> dir(0)
    (1.0, 0.0)
    >>> dir(45)
    (0.7071, 0.7071)
    '''
    return (round(cosd(t), 4), round(sind(t), 4))


def mexp(x):
    '''from MP = exp(x/256)
    >>> mexp(0)
    1.0
    >>> mexp(256)
    2.718281828459045
    '''
    return exp(x / 256)


def mlog(x):
    ''' from MP = 256 log(x)
    >>> mlog(10)
    589.4617838064758
    '''
    return 256 * log(x)


def abs(a, b=0):
    '''Like MP
    >>> abs(3,4)
    5.0
    >>> abs(1)
    1.0
    >>> abs(-42.1)
    42.1
    '''
    return hypot(a, b)


def choose(n, k):
    '''A fast way to calculate binomial coefficients by Andrew Dalke (contrib).

    >>> choose(4,2)
    6
    >>> choose(2,4)
    0
    >>> choose(20,8)
    125970
    '''
    if 0 <= k <= n:
        ntok = 1
        ktok = 1
        for t in range(1, min(k, n - k) + 1):
            ntok *= n
            ktok *= t
            n -= 1
        return ntok // ktok
    return 0


def workout(s):
    '''De-Texify the expression then call eval().
    Also spot units.

    >>> workout('1+1')
    2
    >>> workout(r'37\\times27')
    999
    >>> workout(r'{55\\over6}')
    9.166666666666666
    >>> workout('2^8+pi')
    259.1415926535898
    >>> workout(r'\\\\sqrt(3)')
    1.7320508075688772
    >>> workout('3e^-3')
    0.14936120510359185
    >>> workout('210mm-3in')
    379.27559055118115
    >>> workout('25.4mm')
    72.0
    >>> workout('2.5in')
    180.0

    '''

    s = s.replace(r'\times', '*')
    s = s.replace(r'\left(', '(')
    s = s.replace(r'\right)', ')')
    s = re.sub(r'{(.*?)\\over(.*?)}', r'((\1)/(\2))', s)
    s = re.sub(r'{(.*?)\\choose(.*?)}', r'choose(\1,\2)', s)
    s = s.replace(r'^', '**')
    s = s.replace(r'{', '(')
    s = s.replace(r'}', ')')
    s = s.replace('\\', '')
    s = re.sub(r'(\d?\d)!', r'factorial(\1)', s)
    s = re.sub(r'([0-9\)])([a-z\(])', r'\1*\2', s)
    s = re.sub(r'(\d+(:?\.\d+)?)\*mm', r'(\1*720/254)', s)
    s = re.sub(r'(\d+(:?\.\d+)?)\*in', r'(\1*72)', s)
    s = re.sub(r'(\d+(:?\.\d+)?)\*bp', r'(\1*1)', s)
    s = re.sub(r'(\d+(:?\.\d+)?)\*pt', r'(\1*7200/7227)', s)
    try:
        return eval(s)
    except SyntaxError:
        return '[' + s + ']'
    except ValueError:
        return '?' + s
    return None


def find_expression(line, col):
    '''Given a line and a cursor pos, 
       return a tuple of str (prefix, expression, suffix).

    Note that the cursor position is 0 indexed.
    Note trailing and leading blanks are preserved.

    >>> find_expression('',0)
    ('', '', '')
    >>> find_expression('This one is 3+4 easy', 15)
    ('This one is ', '3+4', ' easy')
    >>> find_expression('A bit harder', 0)
    ('', '', 'A bit harder')
    >>> find_expression('# Normal 2+2', 11)
    ('# Normal ', '2+2', '')

    >>> find_expression('12',1)
    ('', '12', '')

    >>> find_expression('12 ',2)
    ('', '12', ' ')

    >>> find_expression('12 ',2)
    ('', '12', ' ')

    >>> find_expression('String 3+4=',10)
    ('String ', '3+4=', '')


    '''

    if len(line) == 0:
        return ('', '', '')

    if col == 0:
        return ('', '', line)

    alphabet = "'abcdefghijklmnopqrstuvwxyz1234567890!,.-+*/^\\{}()"
    target = ''
    p = col
    while p >= 0:
        c = line[p]
        p -= 1
        if len(target) == 0:
            if c in '=' + alphabet:
                target = c
            elif c == ' ':
                col -= 1
        elif c in alphabet:
            target = c + target
        else:
            p = p + 1
            break

    return (line[0:p + 1], target, line[col + 1:])


def evaluate_expression(target):
    '''Check for terminal "signals" and call workout accordingly.

    If the expression ends in "=" then answer is "expr = answer".
    If the expression ends in "\" then make the answer a fraction.
    Otherwise just replace the expr with the answer.

    >>> evaluate_expression('3+4=')
    '3+4 = 7'
    >>> evaluate_expression(r'0.5\\\\')
    '0.5 = {1\\\\over2}'
    >>> evaluate_expression('')
    ''

    '''
    if not target:
        return ''

    if target.endswith('='):
        target = target.strip('=')
        answer = workout(target)
        try:
            approx = float('%g' % answer)
            rel = '=' if fabs(answer - approx) < 1e-15 else '\\simeq'
            return f'{target} {rel} {approx:g}'
        except TypeError:
            return f'{target} = {answer}'
        except ValueError:
            return answer + '?'

    if target.endswith("\\"):
        target = target.strip("\\")
        q = fractions.Fraction(workout(target)).limit_denominator()
        return f'{target} = {{{q.numerator}\\over{q.denominator}}}'

    return '{0}'.format(workout(target))


if __name__ == '__main__':
    try:
        import vim
        line = vim.current.line
        (row, col) = vim.current.window.cursor

        (prefix, expression, suffix) = find_expression(line, col)
        answer = evaluate_expression(expression)
        vim.current.line = prefix + answer + suffix + " "
        vim.current.window.cursor = (row, len(prefix + answer))
    except ImportError:
        pass
