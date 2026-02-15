import importlib.machinery
import importlib.util
import types
import subprocess

SCRIPT_PATH = 'scripts/validate-phase-5a.py'


def load_module():
    loader = importlib.machinery.SourceFileLoader('validate_phase_5a', SCRIPT_PATH)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def test_validate_all_pass(monkeypatch):
    mod = load_module()

    # stub run_cmd to always return success
    def fake_run_cmd(cmd, description=""):
        return True, "ok", ""

    monkeypatch.setattr(mod, 'run_cmd', fake_run_cmd)

    # stub shutil.which to pretend tools exist
    monkeypatch.setattr('shutil.which', lambda x: '/usr/bin/' + x)

    # stub os.geteuid to 0
    monkeypatch.setattr('os.geteuid', lambda: 0)

    # Run validate() and expect exit code 0
    rc = mod.validate()
    assert rc == 0


def test_validate_fails(monkeypatch):
    mod = load_module()

    # Make the first check fail, others succeed
    def fake_run_cmd(cmd, description=""):
        if 'zramctl | grep -q zram0' in cmd:
            return False, '', 'not found'
        return True, 'ok', ''

    monkeypatch.setattr(mod, 'run_cmd', fake_run_cmd)
    monkeypatch.setattr('shutil.which', lambda x: None)
    monkeypatch.setattr('os.geteuid', lambda: 1000)

    rc = mod.validate()
    assert rc == 1
