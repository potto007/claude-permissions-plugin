"""Tests for find_new_permissions.py — diff logic and bogus pattern filtering."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = str(Path(__file__).resolve().parent.parent / "skills/permission-update/scripts/find_new_permissions.py")

# Also import the helper directly for unit tests
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills/permission-update/scripts"))
from find_new_permissions import _is_bogus_pattern


def run_find(env_home: Path, cwd: Path):
    """Run find_new_permissions.py in a subprocess with patched HOME and cwd."""
    import os

    env = os.environ.copy()
    env["HOME"] = str(env_home)
    code = f"""
import sys
from pathlib import Path
_orig_home = Path.home
Path.home = classmethod(lambda cls: Path({str(env_home)!r}))
exec(open({SCRIPT!r}).read())
"""
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        env=env,
    )


# ── _is_bogus_pattern (unit) ────────────────────────────────────────────────


class TestIsBogusPattern:
    @pytest.mark.parametrize("perm", [
        "Bash(do cp:*)",
        "Bash(done)",
        "Bash(then echo:*)",
        "Bash(fi)",
        "Bash(else rm:*)",
        "Bash(elif test:*)",
        "Bash(in foo:*)",
        "Bash(esac)",
        "Bash(case x:*)",
        "Bash(for i:*)",
        "Bash(while true:*)",
        "Bash(until false:*)",
        "Bash(if test:*)",
        "Bash(select opt:*)",
    ])
    def test_rejects_shell_reserved_words(self, perm):
        assert _is_bogus_pattern(perm) is True

    @pytest.mark.parametrize("perm", [
        "Bash(git add:*)",
        "Bash(pip3 list:*)",
        "Bash(docker run:*)",
        "Bash(npm install:*)",
        "Bash(cargo build:*)",
        "Bash(ls)",
        "Bash(xargs -I{}:*)",
    ])
    def test_accepts_real_commands(self, perm):
        assert _is_bogus_pattern(perm) is False

    def test_non_bash_pattern_not_bogus(self):
        assert _is_bogus_pattern("Read(*)") is False
        assert _is_bogus_pattern("Edit(*)") is False


# ── Full script (integration) ───────────────────────────────────────────────


class TestFindNewPermissions:
    def test_filters_bogus_patterns_from_output(self, tmp_path):
        home = tmp_path / "home"
        claude_dir = home / ".claude"
        claude_dir.mkdir(parents=True)
        (claude_dir / "settings.json").write_text(json.dumps({
            "permissions": {"allow": ["Bash(ls:*)"]}
        }))

        project = tmp_path / "project"
        proj_claude = project / ".claude"
        proj_claude.mkdir(parents=True)
        (proj_claude / "settings.local.json").write_text(json.dumps({
            "permissions": {"allow": [
                "Bash(ls:*)",
                "Bash(do cp:*)",
                "Bash(done)",
                "Bash(pip3 list:*)",
                "Bash(then echo:*)",
            ]}
        }))

        result = run_find(home, project)
        assert result.returncode == 0
        lines = result.stdout.strip().splitlines()
        # Only pip3 list should survive (ls is in global, others are bogus)
        assert lines == ["Bash(pip3 list:*)"]

    def test_all_bogus_returns_none(self, tmp_path):
        home = tmp_path / "home"
        claude_dir = home / ".claude"
        claude_dir.mkdir(parents=True)
        (claude_dir / "settings.json").write_text(json.dumps({}))

        project = tmp_path / "project"
        proj_claude = project / ".claude"
        proj_claude.mkdir(parents=True)
        (proj_claude / "settings.local.json").write_text(json.dumps({
            "permissions": {"allow": ["Bash(do cp:*)", "Bash(done)"]}
        }))

        result = run_find(home, project)
        assert result.returncode == 0
        assert result.stdout.strip() == "NONE"

    def test_normal_diff_without_bogus(self, tmp_path):
        home = tmp_path / "home"
        claude_dir = home / ".claude"
        claude_dir.mkdir(parents=True)
        (claude_dir / "settings.json").write_text(json.dumps({
            "permissions": {"allow": ["Bash(git:*)"]}
        }))

        project = tmp_path / "project"
        proj_claude = project / ".claude"
        proj_claude.mkdir(parents=True)
        (proj_claude / "settings.local.json").write_text(json.dumps({
            "permissions": {"allow": ["Bash(git:*)", "Bash(cargo:*)", "Bash(npm:*)"]}
        }))

        result = run_find(home, project)
        assert result.returncode == 0
        lines = result.stdout.strip().splitlines()
        assert "Bash(cargo:*)" in lines
        assert "Bash(npm:*)" in lines
        assert "Bash(git:*)" not in lines
