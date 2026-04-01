from __future__ import annotations

import os
import sys
from datetime import UTC, datetime, timedelta

import jwt

from oidc_id_token_file_server.config import load_settings


def main() -> int:
    if len(sys.argv) < 2:
        print(
            "usage: uv run python scripts/mint_test_token.py <email> [audience] [groups_csv]",
            file=sys.stderr,
        )
        return 1

    config_path = os.getenv("OIDC_CONFIG_PATH", "oidc-config.toml")
    settings = load_settings(config_path)
    email = sys.argv[1].lower()

    audience = sys.argv[2] if len(sys.argv) > 2 else settings.audiences[0]
    groups = (
        [group for group in sys.argv[3].split(",") if group]
        if len(sys.argv) > 3
        else list(settings.groups.keys())[:1]
    )
    now = datetime.now(UTC)

    token = jwt.encode(
        {
            "iss": settings.issuer,
            "sub": email,
            "email": email,
            "groups": groups,
            "aud": audience,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=30)).timestamp()),
        },
        settings.shared_secret,
        algorithm=settings.algorithm,
    )
    print(token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
