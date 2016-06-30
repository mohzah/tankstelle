from flask import url_for


def test_sanity(client):
    assert client.get(url_for('hello_world')).status_code == 200
