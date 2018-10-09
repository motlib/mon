import math

# Map a value between 0 and 1 to a color between red and green.
def get_css_color(val, cmap):
    col = get_color_mapping(val, cmap)
    
    return "rgb({0}, {1}, {2})".format(*col)



# Color map going from green over orange to red.
red_green_map = (
    (0, 200, 0),  # green
    (255,220, 0), # orange
    (255, 0, 0)   # red
) 


# Map val between 0 and 1 to a color, e.g. to be used for a color
# scale indicating system load or temperature.
#
# By default a green - orange - red map is used, but other maps can
# be supplied in the map parameter as an array of RGB vectors.
#
# @returns An array with red, green, blue components.
def get_color_mapping(val, cmap=red_green_map):
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


# Return html to format text according to val mapped to a color.
def get_html_color(text, val, format='{t}', tag='span', cmap=red_green_map):
    style = 'color: {c};'.format(c=get_css_color(val, cmap))

    fmt = '<{tag} style="{style}">' + format + '</{tag}>'
    
    return fmt.format(
        tag=tag,
        t=text,
        style=style)

