"""Open file manager folders or reveal items on Linux."""

import os
import shutil
import subprocess
from pathlib import Path

from ok.util.logger import Logger

logger = Logger.get_logger(__name__)


def open_explorer_folder(folder):
    """Open folder using system file manager."""
    folder_path = Path(folder).resolve()
    folder_path.mkdir(parents=True, exist_ok=True)
    target = str(folder_path)

    # 优先检测原生 Linux 桌面文件管理器，防止 xdg-open 被 nwjs/chrome 劫持 inode/directory
    file_managers = [
        ("dolphin", ["dolphin", target]),
        ("nautilus", ["nautilus", target]),
        ("nemo", ["nemo", target]),
        ("thunar", ["thunar", target]),
    ]
    for name, cmd in file_managers:
        if shutil.which(name):
            try:
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logger.info(f"Opened folder using {name}: {target}")
                return True
            except Exception as e:
                logger.warning(f"{name} failed: {e}")

    if shutil.which("xdg-open"):
        try:
            subprocess.Popen(["xdg-open", target], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info(f"Opened folder using xdg-open: {target}")
            return True
        except Exception as e:
            logger.warning(f"xdg-open failed: {e}")
    return False


def reveal_in_explorer(path):
    """Open directory or select item using system file manager."""
    item_path = Path(path).resolve()
    if item_path.is_dir():
        return open_explorer_folder(item_path)
    return open_explorer_folder(item_path.parent)
