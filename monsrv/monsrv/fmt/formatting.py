'''Some utility functions for rendering values in html outout.'''

from datetime import datetime, timedelta
import math

from monsrv import app


@app.template_filter()
def fmt_date_interval(seconds):
    '''Format output of a time interval specified in seconds. '''

    values = (
        ('week',   7*24*60*60),
        ('day',      24*60*60),
        ('hour',        60*60),
        ('minute',         60),
        ('second',          1),
    )

    result = []
    for u,v in values:
        if seconds >= v:
            w = seconds // v
            plural_s = 's' if w > 1 else ''
            result.append('{w:.0f} {u}{plural_s}'.format(w=w, u=u, plural_s=plural_s))
            seconds -= (w * v)
            
    return ', '.join(result)


# TODO: Format output of a DateTime value. 
def fmt_date(dt):
    return str(dt)


@app.template_filter()
def fmt_timestamp(ts):
    '''Format a unix timestamp as a date / time string.'''
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')


# FIXME: sometimes due to rounding errors, the number looks like 1.13000000000000001
@app.template_filter()
def fmt_sig(num, sig=3):
    '''Round num to the specified number of significant figures. '''
    
    if(num == 0):
        return 0

    l = math.floor(math.log10(num)) + 1
    
    num = num / math.pow(10, (l - sig))
    
    num = round(num)    

    fmt = '{0}'

    num = num * math.pow(10, (l - sig))

    # workaround to prevent floating point precision errors.
    num = round(num, 10)
    
    return fmt.format(num)


@app.template_filter()
def fmt_bytes(b, sig=3, baseunit='B') :
    '''Format bytes with the right data size value and the specified number of
    significant figures.

    :param b: The byte value to format.
    :param sig: The number of significant digits.

    :returns: the formatted value as string

    '''
    
    b = abs(b)
    
    sizes = (
        ('T', math.pow(1024, 4)),
        ('G', math.pow(1024, 3)),
        ('M', math.pow(1024, 2)),
        ('k', math.pow(1024, 1)),
    )

    fmt = "{v}{u}{baseunit}"
    
    for unit, r in sizes:
        if(b >= r):
            return fmt.format(
                v=fmt_sig(b / r, sig),
                u=unit,
                baseunit=baseunit)

    return fmt.format(
        v=0,
        u='',
        baseunit=baseunit)

