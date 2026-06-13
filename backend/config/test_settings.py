from config.settings import private_app_auth_default


def test_private_app_auth_is_enabled_by_default_in_production():
    assert private_app_auth_default(debug=False) is True


def test_private_app_auth_can_stay_relaxed_by_default_in_development():
    assert private_app_auth_default(debug=True) is False
