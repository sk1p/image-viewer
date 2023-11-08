from bokeh.server.auth_provider import AuthProvider


class TokenAuthProvider(AuthProvider):
    def __init__(self, token):
        self.token = token
        super().__init__()

    @property
    def get_user(self):
        def get_user(request_handler):
            api_key = request_handler.request.headers.get('X-Api-Key')
            if api_key != self.token:  # TODO: constant time compare
                return None  # this means "not logged in"
            request_handler.request.cookies["is_guest"] = "1"
            return "guest"
        return get_user

    @property
    def login_url(self):
        # don't care - don't have a login form anyways
        return '/login/'
