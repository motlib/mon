from datetime import timedelta
import math

def fmt_date_interval(seconds):
    '''Format output of a time interval specified in seconds. '''

    values = (
        ('weeks', 7*24*60*60),
        ('days', 24*60*60),
        ('hours', 60*60),
        ('minutes', 60),
        ('seconds', 1),
    )

    result = []
    for u,v in values:
        if seconds >= v:
            w = seconds // v
            result.append('{w:.0f} {u}'.format(w=w,u=u))
            seconds -= (w * v)

    
            
    return ', '.join(result)


# TODO: Format output of a DateTime value. 
def fmt_date(dt):
    return str(dt)


# FIXME: sometimes due to rounding errors, the number looks like 1.13000000000000001
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

 
def fmt_bytes(b, sig = 3) :
    '''Format bytes with the right data size value and the specified number of
    significant figures.

    :param b: The byte value to format.
    :param sig: The number of significant digits.

    :returns: the formatted value as string

    '''
    
    b = abs(b)
    
    sizes = {
        'TB': math.pow(1024, 4),
        'GB': math.pow(1024, 3),
        'MB': math.pow(1024, 2),
        'kB': math.pow(1024, 1),
    }

    fmt = "{v}{u}"
    
    for u, r in sizes.items():
        if(b >= r) :
            return fmt.format(v=fmt_sig(b / r, sig), u=u)

    return fmt.format(v=fmt_sig(bytes, sig), u='B')

