"""Tests for Alembic migration structure."""
import pathlib

VERSIONS_DIR = pathlib.Path(__file__).parent.parent / "migrations" / "versions"


def _load_module(path: pathlib.Path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _migration_files() -> list[pathlib.Path]:
    return sorted(VERSIONS_DIR.glob("*.py"))


def test_migration_files_exist() -> None:
    files = _migration_files()
    assert len(files) >= 3, "Expected at least 3 migration files"


def test_each_migration_has_required_attributes() -> None:
    for path in _migration_files():
        mod = _load_module(path)
        assert hasattr(mod, "revision"),      f"{path.name} missing 'revision'"
        assert hasattr(mod, "down_revision"), f"{path.name} missing 'down_revision'"
        assert hasattr(mod, "upgrade"),       f"{path.name} missing 'upgrade'"
        assert hasattr(mod, "downgrade"),     f"{path.name} missing 'downgrade'"


def test_revision_chain_is_linear() -> None:
    mods = [_load_module(p) for p in _migration_files()]
    revisions = {m.revision for m in mods}
    down_revisions = {m.down_revision for m in mods if m.down_revision is not None}
    # Every down_revision must point to an existing revision
    for dr in down_revisions:
        assert dr in revisions, f"down_revision '{dr}' has no matching revision"


def test_revision_ids_are_unique() -> None:
    mods = [_load_module(p) for p in _migration_files()]
    ids = [m.revision for m in mods]
    assert len(ids) == len(set(ids)), f"Duplicate revision IDs: {ids}"
