import os
from pathlib import Path


ENV_PATH = Path(__file__).resolve().parents[1] / ".env"


def load_env_file(env_path=ENV_PATH):
    """
    載入專案根目錄的 .env，已存在的系統環境變數不覆蓋。
    """
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def get_required_env(name):
    value = os.getenv(name)
    if value:
        return value
    raise RuntimeError(
        f"缺少必要環境變數 {name}。請在專案根目錄的 .env 中設定它。"
    )
