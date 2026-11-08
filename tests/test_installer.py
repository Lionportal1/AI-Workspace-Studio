"""Offline regression tests for Windows/macOS/Linux installer."""
import json
from pathlib import Path
import shutil,subprocess,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
def invoke(*args,input_text=None):
    return subprocess.run([sys.executable,str(ROOT/"ai_workspace_portable.py"),*map(str,args)],input=input_text,capture_output=True,text=True,timeout=60)
class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)
    def test_skill_tiers_and_agents(self):
        for tier,count,mcp in [("minimal",20,0),("balanced",35,3),("max",50,10)]:
            target=self.path/tier
            r=invoke(target,"--agent","universal","--preset",tier,"--offline","--no-git")
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
            self.assertEqual(len(list((target/".agents/skills").glob("*/SKILL.md"))),count)
            self.assertEqual(len(json.loads((target/".agents/mcp_config.json").read_text())["mcpServers"]),mcp)
            self.assertTrue((target/"opencode.json").exists())
            self.assertTrue((target/".github/skills").is_dir())
    def test_workspace_profile_version_comes_from_installer(self):
        target = self.path / "versioned-workspace"
        args = (target, "--agent", "antigravity", "--preset", "minimal",
                "--mcp", "none", "--offline", "--no-git")
        result = invoke(*args)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        version = invoke("--version")
        self.assertEqual(version.returncode, 0, version.stderr)
        profile = target / "docs/integrations/WORKSPACE_PROFILE.json"
        self.assertEqual(json.loads(profile.read_text(encoding="utf-8"))["version"],
                         version.stdout.strip())

        # Preserve an existing profile unless overwrite is explicitly requested.
        preserved = profile.read_text(encoding="utf-8")
        result = invoke(*args)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(profile.read_text(encoding="utf-8"), preserved)

        # An independent adapter call with a different future version must not
        # retain a hard-coded version; the engine supplies this argument.
        future_version = "8.2.0-rc.1"
        adapter = ROOT / "lib/generate_profiles.py"
        result = subprocess.run(
            [sys.executable, str(adapter), str(target), "antigravity",
             "minimal", "none", "1", "general", future_version],
            capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(profile.read_text(encoding="utf-8"))["version"],
                         future_version)

    def test_dry_run(self):
        t=self.path/"dry"
        self.assertEqual(invoke(t,"--dry-run","--offline").returncode,0)
        self.assertFalse(t.exists())
    def test_preserves_files_and_custom_mcp(self):
        t=self.path/"existing"
        (t/".agents").mkdir(parents=True)
        (t/"AGENTS.md").write_text("user custom")
        (t/".agents/mcp_config.json").write_text('{"mcpServers":{"custom":{"command":"echo"}}}')
        r=invoke(t,"--agent","opencode,codex","--preset","max","--offline","--no-git")
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual((t/"AGENTS.md").read_text(),"user custom")
        self.assertIn("custom",json.loads((t/".agents/mcp_config.json").read_text())["mcpServers"])
    def test_malformed_mcp_preflight(self):
        t=self.path/"broken"
        (t/".agents").mkdir(parents=True)
        (t/".agents/mcp_config.json").write_text("{invalid")
        self.assertNotEqual(invoke(t,"--offline").returncode,0)
        self.assertFalse((t/"AGENTS.md").exists())
    def test_menu(self):
        t=self.path/"menu"
        r=invoke(t,"--menu","--no-git","--offline",input_text="2\n2,4\n3\n3\n9\ny\n")
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertTrue((t/"opencode.json").exists())
    def test_advanced_menu_shows_toggle_state_and_effects(self):
        t = self.path / "advanced-menu"
        r = invoke(
            t, "--menu", "--no-git", "--offline",
            input_text="7\n1\n7\n1\n7\n3\n7\n2\n0\n",
        )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("1 Git initialization: OFF", r.stdout)
        self.assertIn("Git initialization is now ON", r.stdout)
        self.assertIn("Git initialization is now OFF", r.stdout)
        self.assertIn("Offline mode is now OFF", r.stdout)
        self.assertIn("Initial commit is now ON", r.stdout)
        self.assertIn("Git init: ON", r.stdout)
        self.assertIn("Git init: OFF", r.stdout)
        self.assertIn("Offline: ON", r.stdout)
        self.assertIn("Offline: OFF", r.stdout)
        self.assertIn("Note: initial commit applies only", r.stdout)
        self.assertFalse(t.exists())

    def test_doctor_success_and_invalid_bundle_exit_codes(self):
        # Test the actual CLI against a small isolated copy of its core assets.
        # No edits are made to the development tree or a user's workspace.
        t = self.path / "doctor-bundle"
        t.mkdir()
        entry = t / "ai_workspace_portable.py"
        shutil.copyfile(ROOT / "ai_workspace_portable.py", entry)
        assets = t / "assets"
        shutil.copytree(ROOT / "assets/scaffold/.agents/skills",
                        assets / "scaffold/.agents/skills")
        index = assets / "profile-index.json"
        shutil.copyfile(ROOT / "assets/profile-index.json", index)
        (t / "lib").mkdir()
        adapter = t / "lib/generate_profiles.py"
        shutil.copyfile(ROOT / "lib/generate_profiles.py", adapter)

        def diagnose():
            return subprocess.run([sys.executable, str(entry), "--doctor"],
                                  capture_output=True, text=True, timeout=60)

        result = diagnose()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Template    OK", result.stdout)

        # Every failure is recoverable; restored fixtures must still pass.
        original_index = index.read_text(encoding="utf-8")
        index.unlink()
        result = diagnose()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Template    MISSING", result.stdout)

        index.write_text("{broken json", encoding="utf-8")
        result = diagnose()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Template    MISSING", result.stdout)
        index.write_text(original_index, encoding="utf-8")

        skill = assets / "scaffold/.agents/skills/api-contract-review/SKILL.md"
        skill.rename(skill.with_suffix(".hidden"))
        result = diagnose()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Template    MISSING", result.stdout)
        skill.with_suffix(".hidden").rename(skill)

        adapter.rename(adapter.with_suffix(".hidden"))
        result = diagnose()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Template    MISSING", result.stdout)
        adapter.with_suffix(".hidden").rename(adapter)

        original_adapter = adapter.read_text(encoding="utf-8")
        adapter.write_text("def broken(:\n", encoding="utf-8")
        result = diagnose()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Template    MISSING", result.stdout)
        adapter.write_text(original_adapter, encoding="utf-8")

        result = diagnose()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Template    OK", result.stdout)

    def test_windows_npx(self):
        from pathlib import PureWindowsPath
        sys.path.insert(0,str(ROOT))
        import ai_workspace_portable as studio
        mcp=studio.make_mcp(PureWindowsPath(r"C:\My Projects\Game"),"full",windows=True)
        self.assertEqual(mcp["filesystem"]["command"],"npx.cmd")
        self.assertEqual(mcp["filesystem"]["args"][-1],r"C:\My Projects\Game")
if __name__=="__main__":unittest.main()
