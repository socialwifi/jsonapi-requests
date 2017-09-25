import flask


class FlaskForwardAuth:
    def __call__(self, r):
        r.headers['Authorization'] = flask.request.headers['Authorization']
        return r
