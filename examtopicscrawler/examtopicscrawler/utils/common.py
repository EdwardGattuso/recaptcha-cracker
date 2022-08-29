def strip_newline_from_list(str_list):
    """
    Given a list of strings, strip the trailing newline from each
    string.
    """
    return filter(None, [s.strip() for s in str_list])

