"""Facts one TAR bot relies on about another.

Each value describes what TARVeri writes. TARVeri's tests check its own config and database against
these values; TARClub's tests check the columns and roles it reads. Changing a value here is a
cross-bot change: both bots' test suites must pass before merging.
"""

from typing import Final

# PRAGMA user_version that TARVeri stamps on its database.
TARVERI_SCHEMA_VERSION: Final[int] = 1

# Columns of TARVeri's `verifications` table that TARClub reads.
TARVERI_VERIFICATION_COLUMNS: Final[frozenset[str]] = frozenset(
    {
        "discord_user_id",
        "faculty_code",
        "campus_code",
        "level_code",
        "programme_code",
        "is_alumni",
        "card_expiry_date",
        "verified_at",
    }
)

# Role names that mark a verified student, lowercased, with any "TARUMT " prefix removed.
# Faculty codes and study levels are the names TARVeri assigns. "verified" is TARVeri's base role
# ("TARUMT Verified"). "bachelor's degree" is the older name of the Degree level role. TARVeri still
# resolves it on existing servers, so both stay.
TARVERI_STUDENT_ROLE_NAMES: Final[frozenset[str]] = frozenset(
    {
        "cpus",
        "fafb",
        "fcci",
        "focs",
        "foas",
        "fobe",
        "foet",
        "fssh",
        "degree",
        "diploma",
        "foundation",
        "postgraduate",
        "bachelor's degree",
        "verified",
    }
)
