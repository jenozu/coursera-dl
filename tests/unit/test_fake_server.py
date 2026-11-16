import pytest
import requests

pytestmark = pytest.mark.unit


def test_memberships_requires_cauth(fake_coursera):
    r = requests.get(fake_coursera.base_url + "/memberships", timeout=5)
    assert r.status_code == 401


def test_memberships_with_cauth(fake_coursera):
    r = requests.get(
        fake_coursera.base_url + "/memberships", cookies={"CAUTH": "x"}, timeout=5
    )
    assert r.status_code == 200
    assert r.json()["linked"]["courses.v1"][0]["slug"] == "sample-course-one"


def test_file_served_and_unknown_404(fake_coursera):
    ok = requests.get(fake_coursera.base_url + "/files/slides.pdf", timeout=5)
    missing = requests.get(fake_coursera.base_url + "/files/nope.pdf", timeout=5)
    assert ok.status_code == 200
    assert missing.status_code == 404
