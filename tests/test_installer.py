"""Offline regression tests for Windows/macOS/Linux installer."""
import json
from pathlib import Path
import subprocess,sys,tempfile,unittest
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

    def test_windows_npx(self):
        from pathlib import PureWindowsPath
        sys.path.insert(0,str(ROOT))
        import ai_workspace_portable as studio
        mcp=studio.make_mcp(PureWindowsPath(r"C:\My Projects\Game"),"full",windows=True)
        self.assertEqual(mcp["filesystem"]["command"],"npx.cmd")
        self.assertEqual(mcp["filesystem"]["args"][-1],r"C:\My Projects\Game")
if __name__=="__main__":unittest.main()
