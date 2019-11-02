class HttpError(RuntimeError):
    pass

class UserNeedLogin(RuntimeError):
    pass

class LoginException(RuntimeError):
    pass
