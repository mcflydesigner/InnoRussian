from django.db.models.signals import post_save
from functools import partial
import os

from .models import (Category,
                     SubCategory,
                     Card)


def renameFileToIDofObject(sender, instance, created, **kwargs):
    """
        Function changes the name of the file to the id of the object
        for which this belongs to.
    """
    # Get the name of the file field of the instance(we will work with it)
    nameOfTheFileField = kwargs.get('name_of_filefield_to_use', None)

    # Check that `name_of_filefield_to_use` provided
    if not nameOfTheFileField:
        raise ValueError("Argument 'name_of_filefield_to_use' must be provided.")

    # If blankField is empty, so then nothing to rename
    if not getattr(instance, nameOfTheFileField):
        return None

    # Get current path of the file
    path = str(getattr(instance, nameOfTheFileField).path).split('\\')

    # Change the path of the file, new name is the id of the object
    extension = os.path.splitext(path[-1])
    newFileName = str(instance.id) + extension[1]

    # New name of the file will be id of the instance model
    newPath = '\\'.join(path[0:len(path) - 1]) + '\\' + newFileName

    if os.path.isfile(newPath) and newPath != '\\'.join(path):
        # If such a file already exists, it means that
        # a new file was added, so then remove the old one
        os.remove(newPath)

    # Set new path to the file
    os.rename(getattr(instance, nameOfTheFileField).path, newPath)

    # Change the previous name of the file to a new one
    namePath = getattr(instance, nameOfTheFileField).name.split('/')
    setattr(getattr(instance, nameOfTheFileField), 'name',
            '/'.join(namePath[0:len(namePath) - 1]) + '/' + newFileName)

    sender.objects.filter(pk=instance.id).update(**{nameOfTheFileField: getattr(instance, nameOfTheFileField)})


# Connect model Category to renameFileToIDofObject, so that we will be able to change the name
# of the picture during the creating of the object OR during the modification
# of the existing one(meaning: uploading a new picture)
post_save.connect(
    receiver=partial(renameFileToIDofObject,
                     name_of_filefield_to_use='picture'),
    sender=Category,
    dispatch_uid='update_file_name_category',
    weak=False
)

# Connect model SubCategory to renameFileToIDofObject, so that we will be able to change the name
# of the picture during the creating of the object OR during the modification
# of the existing one(meaning: uploading a new picture)
post_save.connect(
    receiver=partial(renameFileToIDofObject,
                     name_of_filefield_to_use='picture'),
    sender=SubCategory,
    dispatch_uid='update_file_name_subcategory',
    weak=False
)

# Connect model Card to renameFileToIDofObject, so that we will be able to change the name
# of the mp3 file during the creating of the object OR during the modification
# of the existing one(meaning: uploading an mp3 file)
post_save.connect(
    receiver=partial(renameFileToIDofObject,
                     name_of_filefield_to_use='pronunciation'),
    sender=Card,
    dispatch_uid='update_file_name_card',
    weak=False
)
