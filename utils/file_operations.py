import os
import shutil
from utils.structures import Item


def rename_file(before: Item, after: str):
    try:
        os.rename(before.location, before.path / after)
    except (FileNotFoundError, PermissionError):
        return False
    return True


def delete_file(item: Item):
    try:
        if item.is_dir:
            shutil.rmtree(item.location)
        else:
            os.remove(item.location)
    except (FileNotFoundError, PermissionError):
        return False
    return True
