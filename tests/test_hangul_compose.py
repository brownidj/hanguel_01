from app.domain.hangul_compose import compose_cv

def test_compose_cv_basic():
    assert compose_cv("ㄱ", "ㅏ") == "가"
    assert compose_cv("ㄴ", "ㅣ") == "니"

def test_compose_cv_invalid():
    assert compose_cv("", "ㅏ") == ""
    assert compose_cv("ㄱ", "") == ""