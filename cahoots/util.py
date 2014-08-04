def truncateText(text, limit=80):
    if len(text) > limit:
        text = text[:limit-3] + "..."
    return text


def isNumber(text):
    """Checking if the text is a number"""
    
    try:
        float(text.strip())
    except:
        return False

    return True