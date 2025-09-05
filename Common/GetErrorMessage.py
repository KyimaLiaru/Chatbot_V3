# Function for extracting the error message from error object
def GetErrorMessage(e: Exception):
    if e.args and len(e.args) == 2 and isinstance(e.args[0], int):
        return e.args
    else:
        cause = e
        while cause is not None:
            if isinstance(cause, OSError) and cause.strerror:
                return None, cause.strerror
            cause = cause.__cause__ or cause.__context__
        return None, str(e)