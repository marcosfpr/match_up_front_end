import re


def check_password_complexity(password, confirmation):

    if confirmation != password:
        return {'error': "The password and confirmation must match."}

    # calculating the length
    length_error = len(password) <= 8

    # searching for digits
    digit_error = re.search(r"\d", password) is None

    # searching for uppercase
    uppercase_error = re.search(r"[A-Z]", password) is None

    # searching for lowercase
    lowercase_error = re.search(r"[a-z]", password) is None

    # searching for symbols
    symbol_error = re.search(r"[ !@#$%&'()*+,-./[\\\]^_`{|}~" + r'"]', password) is None

    ret = {
        'Password is less than 8 characters': length_error,
        'Password does not contain a number': digit_error,
        'Password does not contain a uppercase character': uppercase_error,
        'Password does not contain a lowercase character': lowercase_error,
        'Password does not contain a special character': symbol_error,
    }

    for check in ret:
        if ret[check]:
            return {'error': 'Password does not meet the requirements'}

    return {'success': 'Password OK'}
