"""Repository entry point; the same probe also ships inside the installed plugin."""
from pathlib import Path
import runpy


if __name__ == "__main__":
    probe = Path(__file__).resolve().parents[1] / "plugins/jamaica-command-center/integrations/hermes/check_connection.py"
    runpy.run_path(str(probe), run_name="__main__")
