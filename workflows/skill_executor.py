"""
Skill Executor — runs skill workflows for the build system.
Skills are YAML-based workflows that validate, audit, and optimize the system.
"""
import yaml
import asyncio
from pathlib import Path
from typing import Dict, Any, List
import subprocess
import structlog

log = structlog.get_logger()

class SkillExecutor:
    """Executes skill workflows defined in YAML files."""
    
    def __init__(self, skills_dir: str = "/opt/agents/skills"):
        self.skills_dir = Path(skills_dir)
        self.skills: Dict[str, Dict] = {}
        self._load_skills()
    
    def _load_skills(self):
        """Load all skill YAML files from the skills directory."""
        if not self.skills_dir.exists():
            log.warning("skills_dir_not_found", dir=str(self.skills_dir))
            return
        
        for skill_file in self.skills_dir.glob("*.yaml"):
            with open(skill_file) as f:
                self.skills[skill_file.stem] = yaml.safe_load(f)
            log.info("skill_loaded", skill=skill_file.stem)
    
    def run(self, skill_name: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run a specific skill workflow."""
        if skill_name not in self.skills:
            return {
                "status": "FAIL",
                "error": f"Skill not found: {skill_name}",
                "available": list(self.skills.keys())
            }
        
        skill = self.skills[skill_name]
        context = context or {}
        results = []
        passed = 0
        failed = 0
        
        for step in skill.get("steps", []):
            step_name = step.get("name", "unnamed")
            step_type = step.get("type", "command")
            
            try:
                if step_type == "command":
                    result = self._run_command(step.get("command", ""))
                elif step_type == "python":
                    result = self._run_python(step.get("code", ""))
                else:
                    result = {"status": "FAIL", "error": f"Unknown step type: {step_type}"}
                
                if result.get("status") == "PASS":
                    passed += 1
                else:
                    failed += 1
                
                results.append({
                    "step": step_name,
                    "status": result.get("status"),
                    "output": result.get("output", ""),
                    "error": result.get("error", "")
                })
            except Exception as e:
                failed += 1
                results.append({
                    "step": step_name,
                    "status": "FAIL",
                    "error": str(e)
                })
        
        return {
            "status": "PASS" if failed == 0 else "FAIL",
            "passed": passed,
            "failed": failed,
            "total": len(results),
            "results": results
        }
    
    def _run_command(self, command: str) -> Dict[str, Any]:
        """Run a shell command."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "status": "PASS" if result.returncode == 0 else "FAIL",
                "output": result.stdout,
                "error": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {"status": "FAIL", "error": "Command timed out"}
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    def _run_python(self, code: str) -> Dict[str, Any]:
        """Run Python code."""
        try:
            exec_globals = {"__name__": "__skill__"}
            exec(code, exec_globals)
            return {
                "status": "PASS",
                "output": str(exec_globals.get("result", "OK"))
            }
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    def list_skills(self) -> List[str]:
        """List available skills."""
        return list(self.skills.keys())

# Singleton instance
executor = SkillExecutor()
