def float2str(float_value, mask='%6.8f', no_trailing_zeros=True):
    """
    Some smart method to do simple operation - convert float value into string.
    """
    try:
        f = float(float_value)
    except:
        return float_value
    s = mask % f
    if no_trailing_zeros:
        s = s.rstrip('0').rstrip('.')
    return s


def percent2string(percent, precis=3):
    """
    A tool to make a string (with % at the end) from given float, ``precis`` is
    precision to round the number.
    """
    s = float2str(round(percent, precis), mask=("%%3.%df" % (precis + 2)))
    return s + '%'


