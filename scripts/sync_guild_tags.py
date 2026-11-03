from __future__ import annotations

import hashlib
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PRIMARY_BASE = "https://raw.githubusercontent.com/mezotv/discord-badges/main/assets/guilds"
SECONDARY_BASE = "https://raw.githubusercontent.com/5l41dev/Discord-Icons-and-Badges-History/main/assets/guilds"
CLIENT_CONSTANTS_URL = "https://raw.githubusercontent.com/Wumpus-Central/discord-mobile-datamining/main/discord_app/modules/guild_tag/GuildTagConstants.tsx"
OFFICIAL_CDN_TEMPLATE = "https://cdn.discordapp.com/guild-tag-badges/{guild_id}/{badge_hash}.png"

# archive_id, kind_id, enum_name, display_name, group, pack, customizable_colors
ITEMS = [
    (1, 20, "WIND", "Wind", "legacy", None, 2),
    (2, 19, "SUN", "Sun", "legacy", None, 2),
    (3, 18, "SOUND", "Sound", "legacy", None, 2),
    (4, 17, "SNOW", "Snow", "legacy", None, 2),
    (5, 16, "SMOKE", "Smoke", "legacy", None, 2),
    (6, 15, "PSYCHIC", "Psychic", "legacy", None, 2),
    (7, 14, "LAVA", "Lava", "legacy", None, 2),
    (8, 13, "GEM", "Gem", "legacy", None, 2),
    (9, 12, "FORCE", "Force", "legacy", None, 2),
    (10, 11, "FLOWER", "Flower", "legacy", None, 2),
    (11, 10, "CROSSHAIRS", "Crosshairs", "legacy", None, 2),
    (12, 9, "COMPASS", "Compass", "free", None, 2),
    (13, 8, "FIRE", "Fire", "free", None, 1),
    (14, 7, "HEART", "Heart", "free", None, 1),
    (15, 6, "LEAF", "Leaf", "free", None, 1),
    (16, 5, "LIGHTNING", "Lightning", "free", None, 1),
    (17, 4, "MOON", "Moon", "free", None, 1),
    (18, 3, "TOADSTOOL", "Toadstool", "free", None, 2),
    (19, 2, "SKULL", "Skull", "free", None, 1),
    (20, 1, "WATER_DROP", "Water Drop", "free", None, 1),
    (21, 0, "SWORD", "Sword", "free", None, 2),
    (22, 21, "BUNNY", "Bunny", "badge-pack", "Pets", 1),
    (23, 22, "DOG", "Dog", "badge-pack", "Pets", 2),
    (24, 23, "FROG", "Frog", "badge-pack", "Pets", 2),
    (25, 24, "GOAT", "Goat", "badge-pack", "Pets", 1),
    (26, 25, "CAT", "Cat", "badge-pack", "Pets", 1),
    (27, 26, "DIAMOND", "Diamond", "badge-pack", "Flex", 1),
    (28, 27, "CROWN", "Crown", "badge-pack", "Flex", 2),
    (29, 28, "TROPHY", "Trophy", "badge-pack", "Flex", 1),
    (30, 29, "MONEY_BAG", "Money Bag", "badge-pack", "Flex", 1),
    (31, 30, "DOLLAR_SIGN", "Dollar Sign", "badge-pack", "Flex", 1),
    (32, 31, "CLOVER", "Clover", "badge-pack", "Plant", 1),
    (33, 32, "BLOSSOM", "Blossom", "badge-pack", "Plant", 1),
    (34, 33, "POTTED_PLANT", "Potted Plant", "badge-pack", "Plant", 2),
    (35, 34, "MAPLE", "Maple", "badge-pack", "Plant", 1),
    (36, 35, "WILTED_FLOWER", "Wilted Flower", "badge-pack", "Plant", 2),
    (37, 36, "BUTTERFLY", "Butterfly", "badge-pack", "Creepy Crawlies", 2),
    (38, 37, "SNAIL", "Snail", "badge-pack", "Creepy Crawlies", 2),
    (39, 38, "CATERPILLAR", "Caterpillar", "badge-pack", "Creepy Crawlies", 2),
    (40, 39, "SPIDER", "Spider", "badge-pack", "Creepy Crawlies", 2),
    (41, 40, "BEE", "Bee", "badge-pack", "Creepy Crawlies", 1),
]


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "discord-badges-assets/1.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


def asset_path(group: str, pack: str | None, name: str) -> str:
    slug = slugify(name)
    if group == "badge-pack":
        return f"assets/guild-tags/packs/{slugify(pack or 'unknown')}/{slug}.svg"
    return f"assets/guild-tags/{group}/{slug}.svg"


def validate_client_enum() -> str:
    text = fetch(CLIENT_CONSTANTS_URL).decode("utf-8", errors="replace")
    for _, kind_id, enum_name, *_ in ITEMS:
        pattern = rf"\b{re.escape(enum_name)}:\s*{kind_id}\b"
        if re.search(pattern, text) is None:
            raise RuntimeError(f"Discord client enum mismatch: {enum_name} != {kind_id}")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def render_table(entries: list[dict]) -> list[str]:
    lines = [
        "| Preview | Name | Kind ID | Archive ID | Colors |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for item in entries:
        lines.append(
            f'| <img src="{item["asset_path"]}" width="36" alt="{item["name"]}"> '
            f'| **{item["name"]}** | `{item["kind_id"]}` | `{item["archive_id"]}` | {item["customizable_colors"]} |'
        )
    return lines


def build_section(entries: list[dict]) -> str:
    free = [item for item in entries if item["group"] == "free"]
    legacy = [item for item in entries if item["group"] == "legacy"]
    packs = {}
    for item in entries:
        if item["group"] == "badge-pack":
            packs.setdefault(item["pack"], []).append(item)

    lines = [
        "<!-- guild-tags:start -->",
        "## Guild Tag preset icons",
        "",
        "Discord currently defines **41 Guild Tag badge kinds** in the client. This archive contains their SVG vector renders: **10 free Server Tags icons, 20 Badge Pack icons, and 11 legacy Guild experiment icons**.",
        "",
        "> Guild Tag badges served for a specific server use Discord's `guild-tag-badges/{guild_id}/{badge_hash}` CDN route, whose documented image formats are raster (PNG/JPEG/WebP), not SVG. The files below are the preset/client vector assets, cross-checked against two public Discord asset archives and the current client enum.",
        "",
        "### Free Server Tags icons",
        "",
        *render_table(free),
        "",
    ]

    for pack_name in ("Pets", "Flex", "Plant", "Creepy Crawlies"):
        lines += [f"### Badge Pack — {pack_name}", "", *render_table(packs[pack_name]), ""]

    lines += [
        "### Legacy Guild experiment icons",
        "",
        "These 11 icons were part of the earlier Guild Tags experiment and are not in the current free/purchasable icon sets.",
        "",
        *render_table(legacy),
        "",
        "Metadata, hashes, source mirrors and client enum IDs are in [`data/guild-tags.json`](data/guild-tags.json).",
        "",
        "<!-- guild-tags:end -->",
    ]
    return "\n".join(lines)


def update_readme(entries: list[dict]) -> None:
    readme_path = ROOT / "README.md"
    text = readme_path.read_text(encoding="utf-8")
    section = build_section(entries)

    start = "<!-- guild-tags:start -->"
    end = "<!-- guild-tags:end -->"
    if start in text and end in text:
        text = re.sub(
            rf"{re.escape(start)}.*?{re.escape(end)}",
            section,
            text,
            flags=re.S,
        )
    else:
        marker = "## Profile, Legacy & App Badges"
        text = text.replace(marker, section + "\n\n" + marker, 1)

    coverage_row = "| Guild Tag preset SVGs | 41 |"
    if coverage_row not in text:
        text = text.replace("| Server Boost Tiers | 9 |", "| Server Boost Tiers | 9 |\n" + coverage_row, 1)

    text = re.sub(
        r"\*\*Total: \d+ badge assets\.\*\*",
        "**Total: 123 assets (82 profile/badge assets + 41 Guild Tag preset SVGs).**",
        text,
        count=1,
    )
    text = re.sub(
        r"\*\*Total: 123 assets \(82 profile/badge assets \+ 41 Guild Tag preset SVGs\)\.\*\*",
        "**Total: 123 assets (82 profile/badge assets + 41 Guild Tag preset SVGs).**",
        text,
        count=1,
    )
    readme_path.write_text(text, encoding="utf-8")


def main() -> None:
    client_constants_sha256 = validate_client_enum()
    entries = []

    for archive_id, kind_id, enum_name, name, group, pack, colors in ITEMS:
        primary_url = f"{PRIMARY_BASE}/{archive_id}.svg"
        secondary_url = f"{SECONDARY_BASE}/{archive_id}.svg"
        primary = fetch(primary_url)
        secondary = fetch(secondary_url)
        if primary != secondary:
            raise RuntimeError(f"Source mirrors differ for Guild Tag SVG {archive_id}")
        if not primary.lstrip().startswith(b"<svg"):
            raise RuntimeError(f"Unexpected non-SVG payload for Guild Tag SVG {archive_id}")

        rel_path = asset_path(group, pack, name)
        target = ROOT / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(primary)

        entries.append(
            {
                "archive_id": archive_id,
                "kind_id": kind_id,
                "enum_name": enum_name,
                "name": name,
                "slug": slugify(name),
                "group": group,
                "pack": pack,
                "legacy": group == "legacy",
                "current": group != "legacy",
                "customizable_colors": colors,
                "format": "svg",
                "asset_path": rel_path,
                "sha256": hashlib.sha256(primary).hexdigest(),
                "source_primary": primary_url,
                "source_secondary": secondary_url,
                "source_mirrors_match": True,
                "client_constants_url": CLIENT_CONSTANTS_URL,
                "official_svg_cdn": False,
                "official_guild_tag_cdn_template": OFFICIAL_CDN_TEMPLATE,
            }
        )
        print(f"Guild Tag {archive_id:02d} {name}: OK")

    data_dir = ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    payload = {
        "count": len(entries),
        "current_count": sum(1 for item in entries if item["current"]),
        "legacy_count": sum(1 for item in entries if item["legacy"]),
        "free_count": sum(1 for item in entries if item["group"] == "free"),
        "badge_pack_count": sum(1 for item in entries if item["group"] == "badge-pack"),
        "client_constants_sha256": client_constants_sha256,
        "client_constants_url": CLIENT_CONSTANTS_URL,
        "official_guild_tag_cdn_template": OFFICIAL_CDN_TEMPLATE,
        "official_guild_tag_cdn_svg_supported": False,
        "entries": entries,
    }
    (data_dir / "guild-tags.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    update_readme(entries)


if __name__ == "__main__":
    main()
