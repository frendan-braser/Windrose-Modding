from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys

import pytest


def _load_cli_module():
    cli_path = Path(__file__).resolve().parents[1] / "windrose_mod_cli.py"
    spec = importlib.util.spec_from_file_location("windrose_mod_cli_test_module", cli_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


cli = _load_cli_module()


def test_scale_value_rounding_and_floor():
    assert cli.scale_value(0, 3.0) == 0
    assert cli.scale_value(1, 0.1) == 1
    assert cli.scale_value(2, 1.5) == 3
    assert cli.scale_value(5, 3.0) == 15


def test_parse_resource_types_accepts_csv_and_rejects_invalid():
    assert cli.parse_resource_types("leather, meat") == {"leather", "meat"}
    with pytest.raises(ValueError):
        cli.parse_resource_types("leather,unknown")


def test_parse_multipliers_and_labels():
    assert cli.parse_multipliers("2,3,5,10") == [2.0, 3.0, 5.0, 10.0]
    assert cli.multiplier_label(2.0) == "2"
    assert cli.multiplier_label(2.5) == "2p5"
    with pytest.raises(ValueError):
        cli.parse_multipliers("0")


def test_clear_matching_paks_removes_only_matching_files(tmp_path: Path):
    mods_dir = tmp_path / "mods"
    mods_dir.mkdir()
    (mods_dir / "BoarLoot_P.pak").write_bytes(b"x")
    (mods_dir / "BoarLoot_P_x3.pak").write_bytes(b"x")
    (mods_dir / "OtherMod.pak").write_bytes(b"x")
    removed = cli.clear_matching_paks(mods_dir, "BoarLoot_P")
    assert removed == 2
    assert not (mods_dir / "BoarLoot_P.pak").exists()
    assert not (mods_dir / "BoarLoot_P_x3.pak").exists()
    assert (mods_dir / "OtherMod.pak").exists()


def test_slug_and_pak_name_helpers():
    assert cli.slugify_mod_name("Better Boar Loot!!") == "better-boar-loot"
    assert cli.pak_name_from_mod_name("better boar loot") == "BetterBoarLoot"


def test_iter_ucas_files_prefers_s3_default(tmp_path: Path):
    paks = tmp_path / "paks"
    paks.mkdir()
    (paks / "pakchunk0_s3-Windows.ucas").write_text("x", encoding="utf-8")
    (paks / "pakchunk0-Windows.ucas").write_text("x", encoding="utf-8")
    result = cli.iter_ucas_files(paks)
    assert result == [paks / "pakchunk0_s3-Windows.ucas"]


def test_iter_ucas_files_include_filter(tmp_path: Path):
    paks = tmp_path / "paks"
    paks.mkdir()
    (paks / "a.ucas").write_text("x", encoding="utf-8")
    (paks / "b.ucas").write_text("x", encoding="utf-8")
    result = cli.iter_ucas_files(paks, include_files=["b.ucas", "missing.ucas"])
    assert result == [paks / "b.ucas"]


def test_load_local_env_from_dotenv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    local_dir = tmp_path / ".local"
    local_dir.mkdir()
    (local_dir / ".env").write_text(
        "\n".join(
            [
                "# comment",
                "TEST_KEY=hello",
                "QUOTED='abc def'",
                "EXISTING=from_file",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(cli, "workspace_root", lambda: tmp_path)
    monkeypatch.setenv("EXISTING", "from_env")

    cli.load_local_env()

    assert cli.os.environ["TEST_KEY"] == "hello"
    assert cli.os.environ["QUOTED"] == "abc def"
    # setdefault keeps existing env value
    assert cli.os.environ["EXISTING"] == "from_env"


def test_resolve_config_string_token_expansion(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setattr(cli, "workspace_root", lambda: tmp_path)
    monkeypatch.setattr(cli, "repo_root", lambda: tmp_path / "modding_tools")
    monkeypatch.setenv("WINDROSE_MODS_DIR", r"C:\Mods")
    monkeypatch.setenv("CUSTOM_NAME", "abc")

    raw = r"<REPO_ROOT>\mods\${CUSTOM_NAME}\out"
    resolved = cli.resolve_config_string(raw, tmp_path / "cfg.json", "output_pak")
    assert resolved.endswith(r"mods\abc\out")
    assert str(tmp_path) in resolved


def test_resolve_config_string_missing_required_env_raises(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.delenv("WINDROSE_PAKS_DIR", raising=False)
    with pytest.raises(ValueError):
        cli.resolve_config_string("<WINDROSE_PAKS_DIR>\\x", tmp_path / "cfg.json", "paks")


def test_resolve_config_path_relative_to_config_file(tmp_path: Path):
    cfg = tmp_path / "cfg" / "build.json"
    cfg.parent.mkdir(parents=True)
    cfg.write_text("{}", encoding="utf-8")
    resolved = cli.resolve_config_path(r".\output\file.pak", cfg, "output_pak")
    assert resolved == (cfg.parent / r".\output\file.pak").resolve()


def test_cmd_setup_boar_template_creates_structure(tmp_path: Path):
    project = tmp_path / "boar-loot"
    args = argparse.Namespace(project_dir=str(project))
    exit_code = cli.cmd_setup_boar_template(args)
    assert exit_code == 0
    assert (project / "input" / "staged" / "R5" / "Plugins" / "R5BusinessRules" / "Content").exists()
    assert (project / "docs" / "build_config.json").exists()
    assert (project / "docs" / "boar_required_assets.json").exists()


def test_cmd_init_mod_scaffolds_template_and_replaces_tokens(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    workspace = tmp_path / "repo"
    template = workspace / "mods" / "new-mod-template"
    (template / "docs").mkdir(parents=True)
    (template / "scripts").mkdir(parents=True)
    (template / "__MOD_SLUG___notes").mkdir(parents=True)
    (template / "README.md").write_text("name=__MOD_NAME__", encoding="utf-8")
    (template / "scripts" / "build_install.ps1").write_text("slug=__MOD_SLUG__", encoding="utf-8")
    (template / "__MOD_SLUG___notes" / "info.txt").write_text("pak=__MOD_PAK_NAME__", encoding="utf-8")

    monkeypatch.setattr(cli, "workspace_root", lambda: workspace)

    args = argparse.Namespace(
        name="Starter Mod",
        slug="",
        mods_root=str(workspace / "mods"),
        force=False,
    )
    assert cli.cmd_init_mod(args) == 0

    mod_dir = workspace / "mods" / "starter-mod"
    assert (mod_dir / "README.md").read_text(encoding="utf-8") == "name=Starter Mod"
    assert (mod_dir / "scripts" / "build_install.ps1").read_text(encoding="utf-8") == "slug=starter-mod"
    assert (mod_dir / "starter-mod_notes" / "info.txt").read_text(encoding="utf-8") == "pak=StarterMod"

    cfg = json.loads((mod_dir / "docs" / "build_config.json").read_text(encoding="utf-8"))
    assert cfg["name"] == "StarterMod"
    assert "starter-mod" in cfg["input_dir"]


def test_cmd_init_mod_existing_dir_requires_force(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    workspace = tmp_path / "repo"
    template = workspace / "mods" / "new-mod-template"
    (template / "docs").mkdir(parents=True)
    (template / "README.md").write_text("x", encoding="utf-8")
    monkeypatch.setattr(cli, "workspace_root", lambda: workspace)

    existing = workspace / "mods" / "starter-mod"
    existing.mkdir(parents=True)
    (existing / "already.txt").write_text("x", encoding="utf-8")
    args = argparse.Namespace(name="Starter Mod", slug="", mods_root=str(workspace / "mods"), force=False)
    with pytest.raises(FileExistsError):
        cli.cmd_init_mod(args)


def test_cmd_build_install_resolves_config_and_dispatches(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.setattr(cli, "workspace_root", lambda: repo)
    monkeypatch.setattr(cli, "repo_root", lambda: repo / "modding_tools")
    monkeypatch.setenv("WINDROSE_MODS_DIR", str(repo / "mods_install"))

    config = {
        "input_dir": r"<REPO_ROOT>\mods\boar\input\staged",
        "output_pak": r"<REPO_ROOT>\mods\boar\output\Boar.pak",
        "mods_dir": "<WINDROSE_MODS_DIR>",
        "backup_dir": r"<REPO_ROOT>\mods\boar\output\mods_backups",
        "mount_point": "../../../",
        "version": "V11",
        "compression": "",
    }
    cfg_path = repo / "cfg.json"
    cfg_path.write_text(json.dumps(config), encoding="utf-8")
    source_staged = repo / "mods" / "boar" / "input" / "staged"
    source_staged.mkdir(parents=True)
    (source_staged / "seed.txt").write_text("x", encoding="utf-8")

    calls = {"backup": None, "pack": None}

    def fake_backup(ns):
        calls["backup"] = ns
        return 0

    def fake_pack(ns):
        calls["pack"] = ns
        return 0

    monkeypatch.setattr(cli, "cmd_backup_mods", fake_backup)
    monkeypatch.setattr(cli, "cmd_pack_pak", fake_pack)

    args = argparse.Namespace(config=str(cfg_path), backup_first=True, repak_path="")
    assert cli.cmd_build_install(args) == 0
    assert calls["backup"] is not None
    assert calls["pack"] is not None
    assert "mods_install" in calls["pack"].install_to_mods
    assert calls["pack"].output_pak.endswith("Boar.pak")


def test_cmd_build_variants_runs_prepare_pack_and_report(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.setattr(cli, "workspace_root", lambda: repo)
    monkeypatch.setattr(cli, "repo_root", lambda: repo / "modding_tools")
    monkeypatch.setenv("WINDROSE_MODS_DIR", str(repo / "mods_install"))

    config = {
        "input_dir": r"<REPO_ROOT>\mods\boar\input\staged",
        "output_pak": r"<REPO_ROOT>\mods\boar\output\Boar.pak",
        "mods_dir": "<WINDROSE_MODS_DIR>",
        "backup_dir": r"<REPO_ROOT>\mods\boar\output\mods_backups",
        "mount_point": "../../../",
        "version": "V11",
        "compression": "",
    }
    cfg_path = repo / "cfg.json"
    cfg_path.write_text(json.dumps(config), encoding="utf-8")
    source_staged = repo / "mods" / "boar" / "input" / "staged"
    source_staged.mkdir(parents=True)
    (source_staged / "seed.txt").write_text("x", encoding="utf-8")

    prep_calls = []
    backup_calls = []
    pack_calls = []

    def fake_prepare(template, multiplier, project_dir, variant_staged_dir, variant_output_pak):
        prep_calls.append((template, multiplier, project_dir, variant_staged_dir, variant_output_pak))

    def fake_backup(ns):
        backup_calls.append(ns)
        return 0

    def fake_pack(ns):
        pack_calls.append(ns)
        return 0

    monkeypatch.setattr(cli, "run_prepare_template", fake_prepare)
    monkeypatch.setattr(cli, "cmd_backup_mods", fake_backup)
    monkeypatch.setattr(cli, "cmd_pack_pak", fake_pack)

    args = argparse.Namespace(
        config=str(cfg_path),
        multipliers="2,3,5",
        prepare_command_template="prepare --mult {multiplier} --staged {variant_staged_dir}",
        project_dir=str(repo / "mods" / "boar"),
        install_multipliers="5",
        backup_first=True,
        report_path="",
        generated_root="",
        allow_unsafe_prepare_template=False,
        repak_path="",
    )
    assert cli.cmd_build_variants(args) == 0
    assert len(prep_calls) == 3
    assert len(pack_calls) == 3
    assert len(backup_calls) == 1
    assert len(prep_calls) == 3
    assert prep_calls[0][3].as_posix().endswith("/mods/boar/output/generated/x2/staged")
    assert pack_calls[0].input_dir.endswith(r"mods\boar\output\generated\x2\staged")
    assert pack_calls[0].output_pak.endswith("Boar_x2.pak")
    assert pack_calls[1].output_pak.endswith("Boar_x3.pak")
    assert pack_calls[2].output_pak.endswith("Boar_x5.pak")
    assert pack_calls[2].install_to_mods.endswith("mods_install")
    report = json.loads((repo / "mods" / "boar" / "output" / "variant_build_report.json").read_text(encoding="utf-8"))
    assert report["multipliers"] == [2.0, 3.0, 5.0]
    assert report["generated_root"].endswith(r"mods\boar\output\generated")


def test_cmd_prepare_boar_hide_json_mod_requires_aes(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.delenv("WINDROSE_AES_KEY", raising=False)
    args = argparse.Namespace(
        aes_key="",
        pak_path="pakchunk0-Windows.pak",
        project_dir=str(tmp_path),
        staged_root="",
        multiplier=2.0,
        resource_types="leather",
        repak_path="",
    )
    with pytest.raises(ValueError):
        cli.cmd_prepare_boar_hide_json_mod(args)


def test_cmd_prepare_boar_hide_json_mod_writes_scaled_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    paks_dir = tmp_path / "paks"
    paks_dir.mkdir()
    pak_file = paks_dir / "pakchunk0-Windows.pak"
    pak_file.write_bytes(b"pak")
    monkeypatch.setenv("WINDROSE_PAKS_DIR", str(paks_dir))

    paths = [
        "R5/Plugins/R5BusinessRules/Content/LootTables/Mobs/Rss/DA_LT_Mob_Boar_Leather.json",
        "R5/Plugins/R5BusinessRules/Content/LootTables/Mobs/Rss/DA_LT_Mob_Boar_Meat.json",
        "R5/Plugins/R5BusinessRules/Content/LootTables/Mobs/Rss/DA_LT_Mob_BoarMega_Leather.json",
    ]
    sample_json = {
        "$type": "R5BLLootParams",
        "LootData": [{"Min": 1, "Max": 2, "Weight": 100, "LootItem": "X", "LootTable": "None"}],
    }

    def fake_run_capture(cmd, cwd=None):
        if "list" in cmd:
            return "\n".join(paths)
        if "get" in cmd:
            return json.dumps(sample_json)
        raise AssertionError(f"Unexpected command: {cmd}")

    monkeypatch.setattr(cli, "resolve_tool", lambda *_args, **_kwargs: Path("repak.exe"))
    monkeypatch.setattr(cli, "run_cmd_capture", fake_run_capture)

    project_dir = tmp_path / "mods" / "boar-loot"
    args = argparse.Namespace(
        aes_key="0xabc",
        pak_path="pakchunk0-Windows.pak",
        project_dir=str(project_dir),
        staged_root="",
        multiplier=3.0,
        resource_types="leather,meat",
        repak_path="",
    )
    assert cli.cmd_prepare_boar_hide_json_mod(args) == 0

    out_file = project_dir / "input" / "staged" / Path(paths[0])
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["LootData"][0]["Min"] == 3
    assert data["LootData"][0]["Max"] == 6
    report = json.loads((project_dir / "docs" / "boar_hide_edit_report.json").read_text(encoding="utf-8"))
    assert report["edited_file_count"] == 3
    assert report["resource_types"] == ["leather", "meat"]


def test_cmd_prepare_cayenne_pepper_json_mod_scales_pepper_only(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    paks_dir = tmp_path / "paks"
    paks_dir.mkdir()
    (paks_dir / "pakchunk0-Windows.pak").write_bytes(b"pak")
    monkeypatch.setenv("WINDROSE_PAKS_DIR", str(paks_dir))

    payload_main = {
        "LootData": [
            {
                "Min": 1,
                "Max": 2,
                "LootItem": "/R5BusinessRules/InventoryItems/Consumables/Food/DA_CID_Food_Raw_Pepper_T01.DA_CID_Food_Raw_Pepper_T01",
                "LootTable": "None",
            },
            {"Min": 1, "Max": 1, "LootItem": "None", "LootTable": "/R5BusinessRules/LootTables/Foliage/Sub_tables/DA_LT_Foliage_Bush_Pepper_Seeds.DA_LT_Foliage_Bush_Pepper_Seeds"},
        ]
    }
    payload_sub = {
        "LootData": [
            {
                "Min": 1,
                "Max": 2,
                "LootItem": "/R5BusinessRules/InventoryItems/Consumables/Food/DA_CID_Food_Raw_Pepper_T01.DA_CID_Food_Raw_Pepper_T01",
                "LootTable": "None",
            }
        ]
    }

    def fake_run_capture(cmd, cwd=None):
        path = cmd[-1]
        if path.endswith("DA_LT_Foliage_Bush_Pepper.json"):
            return json.dumps(payload_main)
        if path.endswith("DA_LT_Foliage_Bush_Pepper_Pepper.json"):
            return json.dumps(payload_sub)
        raise AssertionError(f"Unexpected command: {cmd}")

    monkeypatch.setattr(cli, "resolve_tool", lambda *_args, **_kwargs: Path("repak.exe"))
    monkeypatch.setattr(cli, "run_cmd_capture", fake_run_capture)

    project_dir = tmp_path / "mods" / "cayenne-pepper-yield"
    args = argparse.Namespace(
        aes_key="0xabc",
        pak_path="pakchunk0-Windows.pak",
        project_dir=str(project_dir),
        staged_root="",
        multiplier=3.0,
        repak_path="",
    )
    assert cli.cmd_prepare_cayenne_pepper_json_mod(args) == 0

    main_file = project_dir / "input" / "staged" / "R5/Plugins/R5BusinessRules/Content/LootTables/Foliage/DA_LT_Foliage_Bush_Pepper.json"
    data = json.loads(main_file.read_text(encoding="utf-8"))
    assert data["LootData"][0]["Min"] == 3
    assert data["LootData"][0]["Max"] == 6
    # Seed link row should remain unchanged.
    assert data["LootData"][1]["Min"] == 1
    assert data["LootData"][1]["Max"] == 1


def test_cmd_prepare_mob_rss_json_mod_filters_and_scales(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    paks_dir = tmp_path / "paks"
    paks_dir.mkdir()
    (paks_dir / "pakchunk0-Windows.pak").write_bytes(b"pak")
    monkeypatch.setenv("WINDROSE_PAKS_DIR", str(paks_dir))

    paths = [
        "R5/Plugins/R5BusinessRules/Content/LootTables/Mobs/Rss/DA_LT_Mob_Crocodile_Leather.json",
        "R5/Plugins/R5BusinessRules/Content/LootTables/Mobs/Rss/DA_LT_Mob_CorruptedCrocodile_Bones.json",
        "R5/Plugins/R5BusinessRules/Content/LootTables/Mobs/Rss/DA_LT_Mob_Boar_Leather.json",
    ]
    sample_json = {"LootData": [{"Min": 1, "Max": 2, "LootItem": "X", "LootTable": "None"}]}

    def fake_run_capture(cmd, cwd=None):
        if "list" in cmd:
            return "\n".join(paths)
        if "get" in cmd:
            return json.dumps(sample_json)
        raise AssertionError(f"Unexpected command: {cmd}")

    monkeypatch.setattr(cli, "resolve_tool", lambda *_args, **_kwargs: Path("repak.exe"))
    monkeypatch.setattr(cli, "run_cmd_capture", fake_run_capture)

    project_dir = tmp_path / "mods" / "crocodile-bounty"
    args = argparse.Namespace(
        mob_keywords="crocodile",
        aes_key="0xabc",
        pak_path="pakchunk0-Windows.pak",
        project_dir=str(project_dir),
        staged_root="",
        report_name="crocodile_loot_edit_report",
        report_path="",
        multiplier=3.0,
        repak_path="",
    )
    assert cli.cmd_prepare_mob_rss_json_mod(args) == 0

    croc_file = project_dir / "input" / "staged" / "R5/Plugins/R5BusinessRules/Content/LootTables/Mobs/Rss/DA_LT_Mob_Crocodile_Leather.json"
    data = json.loads(croc_file.read_text(encoding="utf-8"))
    assert data["LootData"][0]["Min"] == 3
    assert data["LootData"][0]["Max"] == 6
    boar_file = project_dir / "input" / "staged" / "R5/Plugins/R5BusinessRules/Content/LootTables/Mobs/Rss/DA_LT_Mob_Boar_Leather.json"
    assert not boar_file.exists()


def test_cmd_prepare_sweet_potato_json_mod_scales_potato_only(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    paks_dir = tmp_path / "paks"
    paks_dir.mkdir()
    (paks_dir / "pakchunk0-Windows.pak").write_bytes(b"pak")
    monkeypatch.setenv("WINDROSE_PAKS_DIR", str(paks_dir))

    payload = {
        "LootData": [
            {
                "Min": 2,
                "Max": 3,
                "LootItem": "/R5BusinessRules/InventoryItems/DefaultItems/Resource/DA_DID_Resource_Potato_T01.DA_DID_Resource_Potato_T01",
                "LootTable": "None",
            },
            {
                "Min": 1,
                "Max": 1,
                "LootItem": "/R5BusinessRules/InventoryItems/DefaultItems/Resource/DA_DID_Resource_PotatoSeeds_T01.DA_DID_Resource_PotatoSeeds_T01",
                "LootTable": "None",
            },
        ]
    }

    def fake_run_capture(cmd, cwd=None):
        if "get" in cmd:
            return json.dumps(payload)
        raise AssertionError(f"Unexpected command: {cmd}")

    monkeypatch.setattr(cli, "resolve_tool", lambda *_args, **_kwargs: Path("repak.exe"))
    monkeypatch.setattr(cli, "run_cmd_capture", fake_run_capture)

    project_dir = tmp_path / "mods" / "sweet-potato-bounty"
    args = argparse.Namespace(
        aes_key="0xabc",
        pak_path="pakchunk0-Windows.pak",
        project_dir=str(project_dir),
        staged_root="",
        multiplier=3.0,
        repak_path="",
    )
    assert cli.cmd_prepare_sweet_potato_json_mod(args) == 0

    out_file = project_dir / "input" / "staged" / "R5/Plugins/R5BusinessRules/Content/LootTables/Foliage/DA_LT_Foliage_Potato.json"
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["LootData"][0]["Min"] == 6
    assert data["LootData"][0]["Max"] == 9
    assert data["LootData"][1]["Min"] == 1
    assert data["LootData"][1]["Max"] == 1


def test_load_recipe_validates_mob_keywords(tmp_path: Path):
    project = tmp_path / "mods" / "goat-bounty"
    docs = project / "docs"
    docs.mkdir(parents=True)
    (docs / "mod_recipe.json").write_text(
        json.dumps(
            {
                "display_name": "Goat Bounty",
                "slug": "goat-bounty",
                "pak_name": "GoatBounty",
                "workflow": "mob_rss",
                "report_name": "goat_loot_edit_report",
                "variants": [2, 3],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        cli.load_recipe(project)


def test_cmd_build_mod_uses_recipe_packages_and_variant_reports(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    repo = tmp_path / "repo"
    project = repo / "mods" / "goat-bounty"
    staged = project / "input" / "staged"
    staged.mkdir(parents=True)
    (staged / ".gitkeep").write_text("", encoding="utf-8")
    (project / "docs").mkdir(parents=True)
    monkeypatch.setattr(cli, "workspace_root", lambda: repo)
    monkeypatch.setattr(cli, "repo_root", lambda: repo / "modding_tools")
    monkeypatch.setenv("WINDROSE_MODS_DIR", str(repo / "mods_install"))

    (project / "docs" / "mod_recipe.json").write_text(
        json.dumps(
            {
                "display_name": "Goat Bounty",
                "slug": "goat-bounty",
                "pak_name": "GoatBounty",
                "workflow": "mob_rss",
                "mob_keywords": ["goat"],
                "report_name": "goat_loot_edit_report",
                "variants": [2, 3],
                "default_install_variant": 3,
                "install_target": "custom",
                "package_variants": True,
                "validate_outputs": True,
                "nexus": {"summary": "Goats", "resources": ["goat drops"]},
            }
        ),
        encoding="utf-8",
    )
    (project / "docs" / "build_config.example.json").write_text(
        json.dumps(
            {
                "input_dir": r"<REPO_ROOT>\mods\goat-bounty\input\staged",
                "output_pak": r"<REPO_ROOT>\mods\goat-bounty\output\GoatBounty_P.pak",
                "mods_dir": "<WINDROSE_MODS_DIR>",
                "backup_dir": r"<REPO_ROOT>\mods\goat-bounty\output\mods_backups",
                "mount_point": "../../../",
                "version": "V11",
                "compression": "",
            }
        ),
        encoding="utf-8",
    )

    pack_calls = []
    backup_calls = []

    def fake_prepare(recipe, project_dir, variant_staged_dir, multiplier, label, repak_path):
        out = variant_staged_dir / "R5" / "Plugins" / "R5BusinessRules" / "Content" / "LootTables" / "Mobs" / "Rss" / "DA_LT_Mob_GoatF_Meat.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({"LootData": [{"Min": multiplier, "Max": multiplier}]}), encoding="utf-8")
        report = project_dir / "docs" / f"{recipe.report_name}_x{label}.json"
        report.write_text(json.dumps({"multiplier": multiplier}), encoding="utf-8")
        return report

    def fake_pack(ns):
        pack_calls.append(ns)
        output = Path(ns.output_pak)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(b"pak")
        if ns.install_to_mods:
            target = Path(ns.install_to_mods) / output.name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"pak")
        return 0

    def fake_backup(ns):
        backup_calls.append(ns)
        return 0

    monkeypatch.setattr(cli, "prepare_recipe_variant", fake_prepare)
    monkeypatch.setattr(cli, "cmd_pack_pak", fake_pack)
    monkeypatch.setattr(cli, "cmd_backup_mods", fake_backup)

    args = argparse.Namespace(
        project_dir=str(project),
        config="",
        install_multipliers="",
        install_target="",
        backup_first=True,
        no_package=False,
        no_validate=False,
        repak_path="",
    )
    assert cli.cmd_build_mod(args) == 0
    assert len(pack_calls) == 2
    assert len(backup_calls) == 1
    assert (project / "output" / "GoatBounty_P_x2.zip").exists()
    assert (project / "output" / "GoatBounty_P_x3.zip").exists()
    assert (project / "docs" / "goat_loot_edit_report_x2.json").exists()
    report = json.loads((project / "output" / "variant_build_report.json").read_text(encoding="utf-8"))
    assert report["variants"][1]["installed"] is True
    assert report["variants"][0]["package"].endswith("GoatBounty_P_x2.zip")


def test_cmd_discover_mob_loot_reports_final_and_rss_rows(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    paks_dir = tmp_path / "paks"
    paks_dir.mkdir()
    (paks_dir / "pakchunk0-Windows.pak").write_bytes(b"pak")
    monkeypatch.setenv("WINDROSE_PAKS_DIR", str(paks_dir))
    paths = [
        "R5/Plugins/R5BusinessRules/Content/LootTables/Mobs/DA_LT_Mob_GoatF_Final.json",
        "R5/Plugins/R5BusinessRules/Content/LootTables/Mobs/Rss/DA_LT_Mob_GoatF_Meat.json",
        "R5/Plugins/R5BusinessRules/Content/LootTables/Mobs/Rss/DA_LT_Mob_Boar_Meat.json",
    ]

    def fake_run_capture(cmd, cwd=None):
        if "list" in cmd:
            return "\n".join(paths)
        if "get" in cmd:
            return json.dumps({"LootData": [{"Min": 1, "Max": 2, "Weight": 100, "LootItem": "X", "LootTable": "None"}]})
        raise AssertionError(f"Unexpected command: {cmd}")

    monkeypatch.setattr(cli, "resolve_tool", lambda *_args, **_kwargs: Path("repak.exe"))
    monkeypatch.setattr(cli, "run_cmd_capture", fake_run_capture)
    output = tmp_path / "goat_discovery.json"
    args = argparse.Namespace(
        keyword="goat",
        aes_key="0xabc",
        pak_path="pakchunk0-Windows.pak",
        output=str(output),
        repak_path="",
    )
    assert cli.cmd_discover_mob_loot(args) == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["final_tables"] == [paths[0]]
    assert payload["rss_tables"][0]["rows"][0]["min"] == 1


def test_generate_nexus_description_from_recipe(tmp_path: Path):
    project = tmp_path / "mods" / "goat-bounty"
    (project / "docs").mkdir(parents=True)
    (project / "docs" / "mod_recipe.json").write_text(
        json.dumps(
            {
                "display_name": "Goat Bounty",
                "slug": "goat-bounty",
                "pak_name": "GoatBounty",
                "workflow": "mob_rss",
                "mob_keywords": ["goat"],
                "report_name": "goat_loot_edit_report",
                "variants": [2, 3, 5, 10],
                "nexus": {"summary": "Increase goats.", "resources": ["goat meat"], "covered": ["goats"]},
            }
        ),
        encoding="utf-8",
    )
    args = argparse.Namespace(project_dir=str(project), output="")
    assert cli.cmd_generate_nexus_description(args) == 0
    text = (project / "docs" / "NEXUS_DESCRIPTION.txt").read_text(encoding="utf-8")
    assert "Goat Bounty - Loot Variants" in text
    assert "Single-player" in text


def test_cmd_init_mob_bounty_scaffolds_recipe_and_docs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    workspace = tmp_path / "repo"
    template = workspace / "mods" / "new-mod-template"
    (template / "docs").mkdir(parents=True)
    (template / "input" / "staged").mkdir(parents=True)
    (template / "output").mkdir(parents=True)
    (template / "README.md").write_text("# __MOD_NAME__", encoding="utf-8")
    (template / "docs" / "build_config.example.json").write_text(
        json.dumps(
            {
                "name": "__MOD_PAK_NAME__",
                "input_dir": "<REPO_ROOT>\\mods\\__MOD_SLUG__\\input\\staged",
                "output_pak": "<REPO_ROOT>\\mods\\__MOD_SLUG__\\output\\__MOD_PAK_NAME___P.pak",
                "mods_dir": "<WINDROSE_MODS_DIR>",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(cli, "workspace_root", lambda: workspace)
    args = argparse.Namespace(
        name="Goat Bounty",
        mob_keywords="goat",
        resources="goat meat, leather",
        slug="",
        mods_root=str(workspace / "mods"),
        force=False,
    )
    assert cli.cmd_init_mob_bounty(args) == 0
    project = workspace / "mods" / "goat-bounty"
    recipe = json.loads((project / "docs" / "mod_recipe.json").read_text(encoding="utf-8"))
    assert recipe["workflow"] == "mob_rss"
    assert recipe["mob_keywords"] == ["goat"]
    assert (project / "docs" / "NEXUS_DESCRIPTION.txt").exists()
