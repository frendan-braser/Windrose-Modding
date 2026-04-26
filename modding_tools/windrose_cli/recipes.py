from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


SUPPORTED_WORKFLOWS = {"mob_rss", "boar_resources", "cayenne_pepper", "sweet_potato"}
SUPPORTED_INSTALL_TARGETS = {"single-player", "multiplayer", "dedicated", "custom"}


@dataclass(frozen=True)
class NexusMetadata:
    summary: str
    resources: list[str] = field(default_factory=list)
    covered: list[str] = field(default_factory=list)
    details: str = ""


@dataclass(frozen=True)
class ModRecipe:
    display_name: str
    slug: str
    pak_name: str
    workflow: str
    variants: list[float]
    default_install_variant: float | None
    install_target: str
    report_name: str
    mob_keywords: list[str] = field(default_factory=list)
    resource_types: list[str] = field(default_factory=list)
    package_variants: bool = True
    validate_outputs: bool = True
    nexus: NexusMetadata = field(default_factory=lambda: NexusMetadata(summary=""))


def _as_list(value: Any, field_name: str) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return [item.strip() for item in value if item.strip()]
    raise ValueError(f"Recipe field '{field_name}' must be a string or list of strings.")


def _as_float_list(value: Any, field_name: str) -> list[float]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"Recipe field '{field_name}' must be a non-empty list.")
    result = []
    for item in value:
        number = float(item)
        if number <= 0:
            raise ValueError(f"Recipe field '{field_name}' values must be > 0.")
        result.append(number)
    return result


def _optional_float(value: Any, field_name: str) -> float | None:
    if value in (None, ""):
        return None
    number = float(value)
    if number <= 0:
        raise ValueError(f"Recipe field '{field_name}' must be > 0.")
    return number


def recipe_path(project_dir: Path) -> Path:
    return project_dir / "docs" / "mod_recipe.json"


def load_recipe(project_dir: Path) -> ModRecipe:
    path = recipe_path(project_dir)
    if not path.exists():
        raise FileNotFoundError(f"Recipe not found: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    return parse_recipe(raw)


def parse_recipe(raw: dict[str, Any]) -> ModRecipe:
    required = ["display_name", "slug", "pak_name", "workflow", "variants", "report_name"]
    missing = [field for field in required if field not in raw]
    if missing:
        raise ValueError(f"Recipe missing required field(s): {', '.join(missing)}")

    workflow = str(raw["workflow"]).strip()
    if workflow not in SUPPORTED_WORKFLOWS:
        raise ValueError(f"Unsupported recipe workflow: {workflow}")

    install_target = str(raw.get("install_target", "custom")).strip() or "custom"
    if install_target not in SUPPORTED_INSTALL_TARGETS:
        raise ValueError(f"Unsupported install_target: {install_target}")

    nexus_raw = raw.get("nexus", {})
    if not isinstance(nexus_raw, dict):
        raise ValueError("Recipe field 'nexus' must be an object.")

    recipe = ModRecipe(
        display_name=str(raw["display_name"]).strip(),
        slug=str(raw["slug"]).strip(),
        pak_name=str(raw["pak_name"]).strip(),
        workflow=workflow,
        variants=_as_float_list(raw["variants"], "variants"),
        default_install_variant=_optional_float(raw.get("default_install_variant"), "default_install_variant"),
        install_target=install_target,
        report_name=str(raw["report_name"]).strip(),
        mob_keywords=_as_list(raw.get("mob_keywords"), "mob_keywords"),
        resource_types=_as_list(raw.get("resource_types"), "resource_types"),
        package_variants=bool(raw.get("package_variants", True)),
        validate_outputs=bool(raw.get("validate_outputs", True)),
        nexus=NexusMetadata(
            summary=str(nexus_raw.get("summary", "")).strip(),
            resources=_as_list(nexus_raw.get("resources"), "nexus.resources"),
            covered=_as_list(nexus_raw.get("covered"), "nexus.covered"),
            details=str(nexus_raw.get("details", "")).strip(),
        ),
    )
    validate_recipe(recipe)
    return recipe


def validate_recipe(recipe: ModRecipe) -> None:
    if not recipe.display_name:
        raise ValueError("Recipe display_name is required.")
    if not recipe.slug:
        raise ValueError("Recipe slug is required.")
    if not recipe.pak_name:
        raise ValueError("Recipe pak_name is required.")
    if not recipe.report_name:
        raise ValueError("Recipe report_name is required.")
    if recipe.workflow == "mob_rss" and not recipe.mob_keywords:
        raise ValueError("mob_rss recipes require mob_keywords.")
    if recipe.workflow == "boar_resources" and not recipe.resource_types:
        raise ValueError("boar_resources recipes require resource_types.")


def write_recipe(path: Path, recipe: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(recipe, indent=2), encoding="utf-8")

