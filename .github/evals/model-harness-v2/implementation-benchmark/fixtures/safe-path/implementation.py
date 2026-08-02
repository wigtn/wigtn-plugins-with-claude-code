from pathlib import Path
def safe_join(root, user_path):
    return Path(root) / user_path
