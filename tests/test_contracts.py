from tarbot_console.contracts import (
    TARVERI_SCHEMA_VERSION,
    TARVERI_STUDENT_ROLE_NAMES,
    TARVERI_VERIFICATION_COLUMNS,
)


def test_role_names_are_lowercase_and_unprefixed():
    for name in TARVERI_STUDENT_ROLE_NAMES:
        assert name == name.lower()
        assert not name.startswith("tarumt ")


def test_schema_version_is_positive_int():
    assert isinstance(TARVERI_SCHEMA_VERSION, int)
    assert TARVERI_SCHEMA_VERSION >= 1


def test_verification_columns_include_the_keys_tarclub_joins_on():
    assert "discord_user_id" in TARVERI_VERIFICATION_COLUMNS
