"""
BlueStacks Manager
"""

import logging
import platform
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class BlueStacksManager:
    """Detects and manages BlueStacks emulator."""
    
    def __init__(self, bluestacks_path: Optional[str] = None):
        self.bluestacks_path = Path(bluestacks_path) if bluestacks_path else None
        self.common_paths = [
            Path(r"C:\\Program Files\\BlueStacks"),
            Path(r"C:\\Program Files (x86)\\BlueStacks"),
            Path.home() / "AppData" / "Local" / "Programs" / "BlueStacks"
        ]

    def get_status(self) -> Dict[str, Any]:
        """Get current BlueStacks status."""
        status = {
            "installed": False,
            "running": False,
            "path": None,
            "errors": []
        }
        
        try:
            install_path = self._find_installation()
            if install_path:
                status["installed"] = True
                status["path"] = str(install_path)
            
            status["running"] = self._is_process_running()
            status["errors"] = self._check_issues()
        except Exception as e:
            status["errors"].append(str(e))
            
        return status

    def _find_installation(self) -> Optional[Path]:
        if self.bluestacks_path and self.bluestacks_path.exists():
            return self.bluestacks_path
            
        for path in self.common_paths:
            if path.exists() and list(path.glob("BlueStacks.exe")):
                return path
        return None

    def _is_process_running(self) -> bool:
        try:
            if platform.system() == "Windows":
                result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq BlueStacks.exe"], capture_output=True, text=True, timeout=5)
                return "BlueStacks.exe" in result.stdout
        except Exception:
            pass
        return False

    def _check_issues(self) -> List[str]:
        issues = []
        if not self._find_installation():
            issues.append("BlueStacks not detected in common paths.")
        return issues

    def launch_bluestacks(self) -> Dict[str, Any]:
        """Attempt to launch BlueStacks."""
        result = {"success": False, "message": ""}
        path = self._find_installation()
        if not path:
            result["message"] = "BlueStacks not found."
            return result
            
        exe = path / "BlueStacks.exe"
        if exe.exists():
            try:
                subprocess.Popen([str(exe)])
                result["success"] = True
                result["message"] = "Launching BlueStacks..."
            except Exception as e:
                result["message"] = f"Launch failed: {e}"
        else:
            result["message"] = "Executable not found at installation path."
        return result