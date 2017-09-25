import flask
import requests


class FlaskForwardAuth(requests.auth.AuthBase):
    def __call__(self, r):
        r.headers['Authorization'] = flask.request.headers['Authorization']
        return r
