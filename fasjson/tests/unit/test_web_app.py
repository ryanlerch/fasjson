import json
import types

from flask_restx import abort

from fasjson.web.app import app


def test_app_gss_forbidden_error(client):
    rv = client.get("/")
    body = json.loads(rv.data)
    expected_codes = {
        "maj": 851968,
        "min": 2529639107,
        "routine": 851968,
        "supplementary": None,
    }

    assert rv.status_code == 403
    assert body == {"message": "Invalid credentials", "codes": expected_codes}


def test_app_default_unauthorized_error(client, mocker):
    creds_factory = mocker.patch("gssapi.Credentials")
    creds_factory.return_value = types.SimpleNamespace(lifetime=0)
    rv = client.get("/")
    body = json.loads(rv.data)

    assert rv.status_code == 401
    assert body == {"message": "Credential lifetime has expired"}


def test_app_default_notfound_error(client, gss_user):
    rv = client.get("/notfound")
    body = json.loads(rv.data)

    assert rv.status_code == 404
    assert body.get("message") is not None


def test_app_default_internal_error(client, gss_user):
    @app.route("/500")
    def fivehundred():
        x = []
        return x[10]

    # Don't catch the exception in the testing framework
    app.config["TESTING"] = False

    rv = client.get("/500")
    body = json.loads(rv.data)

    assert rv.status_code == 500
    assert body.get("message") is not None


def test_app_registered_error(client, gss_user):
    @app.route("/403")
    def forbidden():
        abort(403, "forbidden", foo="bar")

    rv = client.get("/403")
    body = json.loads(rv.data)

    assert rv.status_code == 403
    assert body == {"foo": "bar", "message": "forbidden"}
