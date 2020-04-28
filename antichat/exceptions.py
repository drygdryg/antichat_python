# -*- coding: utf-8 -*-
class AntichatClientError(Exception):
    pass


class AuthError(AntichatClientError):
    pass


class SessionError(AntichatClientError):
    pass


class ContentNotFound(AntichatClientError):
    pass
