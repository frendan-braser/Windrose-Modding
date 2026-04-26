from __future__ import annotations

from .recipes import ModRecipe


INSTALL_PATHS = [
    ("Single-player", r"Windrose\R5\Content\Paks\~mods"),
    ("Multiplayer", r"Windrose\R5\Builds\WindowsServer\R5\Content\Paks\~mods"),
    ("Dedicated Server", r"Windrose Dedicated Server\R5\Content\Paks"),
]


def _variant_lines(recipe: ModRecipe) -> list[str]:
    blurbs = {
        2: "Light boost",
        3: "Balanced default",
        5: "Faster progression",
        10: "High abundance / low grind",
    }
    lines = []
    for variant in recipe.variants:
        label = int(variant) if float(int(variant)) == float(variant) else variant
        blurb = blurbs.get(label, "Custom boost")
        lines.append(f"[*][b]{label}x[/b] - {blurb}")
    return lines


def render_nexus_description(recipe: ModRecipe) -> str:
    variant_title = " / ".join(
        f"{int(v) if float(int(v)) == float(v) else v}x" for v in recipe.variants
    )
    summary = recipe.nexus.summary or f"Increase {recipe.display_name} loot quantities while keeping vanilla drop chances intact."
    resources = ", ".join(recipe.nexus.resources) if recipe.nexus.resources else "configured resource drops"
    covered = ", ".join(recipe.nexus.covered)
    covered_sentence = f" {covered} are covered." if covered else ""
    details = f"\n\n[size=3][color=#D4D4D8]{recipe.nexus.details}[/color][/size]" if recipe.nexus.details else ""

    lines = [
        f"[size=5][b]{recipe.display_name} - Loot Variants ({variant_title})[/b][/size]",
        f"[size=3][color=#D4D4D8]{summary}[/color][/size]",
        "",
        "[size=4][b]What This Mod Does[/b][/size]",
        (
            "[size=3][color=#D4D4D8]"
            f"Scales Min/Max quantities for {resources} where those drops exist.{covered_sentence} "
            "Drop chances and weights are left unchanged."
            "[/color][/size]"
        ),
    ]
    if details:
        lines.append(details.strip())
    lines.extend(
        [
            "",
            "[size=4][b]Available Variants[/b][/size]",
            "[list]",
            *_variant_lines(recipe),
            "[/list]",
            "",
            "[size=4][b]Important Notes[/b][/size]",
            "[list]",
            "[*]Drop chance logic is unchanged from vanilla",
            "[*]If an entry is 0/0 in vanilla, it remains 0/0",
            "[*]Only quantity values are multiplied",
            "[*]Use only one variant `.pak` at a time",
            "[/list]",
            "",
            "[size=4][b]Install[/b][/size]",
            "[list=1]",
            "[*]Choose one variant `.pak`",
            "[*]Install it to the correct folder for how you are playing",
            "[*]Launch game",
            "[/list]",
            "",
            "[size=4][b]Install Paths[/b][/size]",
            "[list]",
        ]
    )
    lines.extend(
        f"[*][b]{label}:[/b] [color=#D4D4D8]{path}[/color]" for label, path in INSTALL_PATHS
    )
    lines.extend(
        [
            "[/list]",
            "",
            "[size=3][color=#D4D4D8]For dedicated servers, you can place the `.pak` directly in the listed folder without creating a `~mods` folder.[/color][/size]",
        ]
    )
    return "\n".join(lines)

