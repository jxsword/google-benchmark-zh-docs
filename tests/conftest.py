import sys
from pathlib import Path

# 让 pytest 能导入 scripts/ 下的模块
SCRIPTS = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
