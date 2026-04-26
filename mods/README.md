# Mods Directory

Future-ready location for additional mods.

Current active project:

- `boar-loot/`
- `new-mod-template/` (scaffold source used by `init-mod`)

When adding new mods, use:

- `mods/<mod-name>/docs`
- `mods/<mod-name>/input`
- `mods/<mod-name>/output`
- `mods/<mod-name>/scripts`

Use the CLI to scaffold a new mod:

```powershell
python ".\modding_tools\windrose_mod_cli.py" init-mod --name "My New Mod"
```
