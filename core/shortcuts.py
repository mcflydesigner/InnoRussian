from functools import partial
from datetime import datetime
import os


def upload_to(path):
    """ Function which uploads files to specific directory """
    return partial(change_filename_to_temporary, path=path)


def change_filename_to_temporary(instance, filename, path):
    """
        Function changes the name of the file to the timestamp
        to prevent collisions with filenames
    """
    extension = os.path.splitext(filename)
    # Create a unique name of the file using timestamp
    filename = str(int(datetime.now().timestamp() * (10 ** 6))) + extension[1]
    return os.path.join(path, filename)
