from pathlib import Path
from common import load_inventory, render_config

text = render_config(load_inventory())
Path("artifacts").mkdir(exist_ok=True)
Path("artifacts/rendered-loopbacks.cfg").write_text(text)
print(text)
print("Saved artifacts/rendered-loopbacks.cfg")
