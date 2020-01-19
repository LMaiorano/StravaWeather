# Simple custom exceptions to handle events in program

class RequestLimitException(Exception):
    # **** Raised when API request limit has been reached ****
    # Do nothing here, except handler will execute in module
    pass

class StravaOtherError(Exception):
    pass

class QuitUI(Exception):
    pass

class MainMenUI(Exception):
    pass

class SkipParamException(Exception):
    pass