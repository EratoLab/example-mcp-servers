from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GroupAccess:
    group: str
    allowed_files: frozenset[str]


@dataclass(frozen=True)
class OidcSettings:
    issuer: str
    algorithm: str
    shared_secret: str
    audiences: tuple[str, ...]
    clock_skew_seconds: int
    groups: dict[str, GroupAccess]


def load_settings(path: str | Path) -> OidcSettings:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(
            f"OIDC configuration file not found: {config_path}. "
            "Copy oidc-config.template.toml to oidc-config.toml first."
        )

    with config_path.open("rb") as file_handle:
        raw_config = tomllib.load(file_handle)

    group_config = raw_config.get("groups", {})
    if not isinstance(group_config, dict) or not group_config:
        raise ValueError("OIDC config must contain a non-empty [groups] table.")

    groups = {
        group_name: GroupAccess(
            group=group_name,
            allowed_files=frozenset(group_settings["allowed_files"]),
        )
        for group_name, group_settings in group_config.items()
    }

    audiences = tuple(raw_config["audiences"])
    if not audiences:
        raise ValueError("OIDC config must define at least one audience.")

    return OidcSettings(
        issuer=raw_config["issuer"],
        algorithm=raw_config.get("algorithm", "HS256"),
        shared_secret=raw_config["shared_secret"],
        audiences=audiences,
        clock_skew_seconds=int(raw_config.get("clock_skew_seconds", 30)),
        groups=groups,
    )
