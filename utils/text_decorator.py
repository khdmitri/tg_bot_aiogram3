def strong(text):
    if text is None:
        text = ""
    return '<strong>'+text+'</strong>'


def italic(text):
    if text is None:
        text = ""
    return '<i>'+text+'</>'


def not_empty(text, add_str='-'):
    if not text:
        return add_str
    else:
        return text
