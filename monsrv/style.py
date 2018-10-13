import math


# Color map going from green over orange to red.
_red_green_map = (
    (0, 200, 0),  # green
    (255,220, 0), # orange
    (255, 0, 0)   # red
) 


def _get_color_mapping(val, minval=0.0, maxval=1.0, cmap=_red_green_map):
    '''Map val between 0 and 1 to a color, e.g. to be used for a color scale
    indicating system load or temperature.
    
    :param val: The value to use for color coding.

    :param minval: The minimum posible value (by default coded as pure green)

    :param maxval: The maxumim possible value (by default coded as pure red)

    :param cmap: The color map. By default a green - orange - red map is used,
    but other maps can be supplied as an iterable of RGB tuples.

    :return: An array with red, green, blue components.

    '''
    
    # map range to [0.0, 1.0]
    val = (val - minval) / (maxval - minval)
    
    # Limit input to range [0, 1]. 
    val = max(0.0, min(1.0, val))

    # Number of intervals in map. 
    n = len(cmap) - 1
    
    # Calculate index of the lower relevant color vector. Prevent
    # edge case if val == 1.0 by limiting pi index.
    col_idx = min(math.floor(val * n), n - 1)

    # Get the start and and end color vectors. 
    col_s = cmap[col_idx]
    col_e = cmap[col_idx + 1]

    # Calculate length of one interval. 
    intlen = 1.0 / n
    # Start value of curent interval. 
    ints = intlen * col_idx 

    # Map val to [0..1] range in interval again. 
    val -= ints
    val /= intlen

    # Linear interpolate between interval start and end vectors. 
    col = (
        col_s[0] + (val * (col_e[0] - col_s[0])),
        col_s[1] + (val * (col_e[1] - col_s[1])),
        col_s[2] + (val * (col_e[2] - col_s[2])),
    )
    
    return col


# Map a value between 0 and 1 to a color between red and green.
def get_css_color(v, minval=0.0, maxval=1.0, cmap=_red_green_map):
    col = _get_color_mapping(val=v, minval=minval, maxval=maxval, cmap=cmap)
    
    return "rgb({0}, {1}, {2})".format(*col)


# Return html to format text according to val mapped to a color.
def get_html_color(v, minval=0.0, maxval=1.0, fmt='{v}', tag='span', cmap=_red_green_map):
    css_col = get_css_color(v=v, cmap=cmap, minval=minval, maxval=maxval)
    
    style = 'color: {c};'.format(c=css_col)

    fmt = '<{tag} style="{style}">{fmt}</{tag}>'.format(**locals())
    
    return fmt.format(v=v)

