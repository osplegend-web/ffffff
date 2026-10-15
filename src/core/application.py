"""
Core Application Class
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class Application:
    """Manages application state and configuration."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else Path.home() / ".ff_gaming_panel" / "config.json"
        self.config = self._load_config()
        self.window = None
        self.is_running = False
        logger.info("Application initialized. Config path: %s", self.config_path)

    def _load_config(self) -> Dict[str, Any]:
        """Load config from disk or create defaults."""
        default_config = {
            "theme": "dark",
            "window_size": [1200, 800],
            "key_bindings": {
                "forward": "W",
                "backward": "S",
                "left": "A",
                "right": "D",
                "fire": "LEFT_MOUSE",
                "aim": "RIGHT_MOUSE",
                "reload": "R",
                "interact": "F",
                "map": "M",
                "inventory": "TAB"
            },
            "aimbot_settings": {
                "enabled": False,
                "fov": 150,
                "smoothing": 0.5
            },
            "esp_settings": {
                "enabled": False,
                "show_boxes": True,
                "show_health": True
            }
        }
        
        try:
            if self.config_path.exists():
                with open(self.config_path, "r") as f:
                    config = json.load(f)
                # Merge defaults
                for k, v in default_config.items():
                    if k not in config:
                        config[k] = v
                return config
            else:
                self._save_config(default_config)
                return default_config
        except Exception as e:
            logger.warning("Config load failed, using defaults: %s", e)
            return default_config

    def _save_config(self, config: Dict[str, Any]):
        """Save config to disk."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error("Config save failed: %s", e)

    def get_config(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def update_config(self, key: str, value: Any):
        self.config[key] = value
        self._save_config(self.config)

    def run(self):
        """Start the GUI."""
        logger.info("Initializing GUI...")
        try:
            from src.ui.main_window import MainWindow
            self.window = MainWindow(self)
            self.window.mainloop()
        except Exception as e:
            logger.error("GUI failed to start: %s", e, exc_info=True)
            print(f"\nFailed to start GUI: {e}")
            print("Falling back to console mode...")
            self._console_mode()

    def _console_mode(self):
        """Fallback if GUI fails."""
        print("\n" + "="*50)
        print("FF GAMING ASSISTANT PANEL - CONSOLE MODE")
        print("="*50)
        print("1. Check BlueStacks")
        print("2. Show Config")
        print("3. Quit")
        
        while self.is_running:
            print("\nSelect option: ", end="")
            choice = input().strip()
            if choice == '1':
                from src.modules.bluestacks import BlueStacksManager
                mgr = BlueStacksManager()
                print(json.dumps(mgr.get_status(), indent=2))
            elif choice == '2':
                print(json.dumps(self.config, indent=2))
            elif choice == '3':
                break
            else:
                print("Invalid option.")