import os
import shutil
from utils.structures import Item


def rename_file(before: Item, after: str):
    location = before.path
    if os.path.exists(location / after):
        return False
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

def create_file_with_content(location: str, content: str):
    if os.path.exists(location):
        return False
    try:
        with open(location, "w") as f:
            f.write(content)
    except (FileNotFoundError, PermissionError):
        return False
    return True
