from django.db import models
from django.utils.timezone import now
from django.core.validators import FileExtensionValidator
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db.models import (Func, Value, CharField, IntegerField)

from .shortcuts import upload_to


"""
    Models of core app.
    The architecture is done in the following way.
    An user accesses the content sequentially:
    Category -> Subcategory -> List of words
"""


class Category(models.Model):
    """
        The model for categories
    """
    name = models.CharField('Name', max_length=55, unique=True)
    # Here we use FileField instead of ImageField to allow only .svg extension for images.
    picture = models.FileField('Picture', upload_to=upload_to('categories/pictures/'),
                               validators=[FileExtensionValidator(allowed_extensions=['svg'])])

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['id']

    def __str__(self):
        return self.name + '(' + str(self.id) + ')'


class SubCategory(models.Model):
    """
        The model for subcategories which are connected
        with the corresponding categories. One subcategory can be connected
        to different categories(many to many relationship).
    """
    categoryId = models.ManyToManyField(Category)
    name = models.CharField('Name', max_length=55, unique=True)
    # Here we use FileField instead of ImageField to allow only .svg extension for images.
    picture = models.FileField('Picture', upload_to=upload_to('subcategories/pictures/'),
                               validators=[FileExtensionValidator(allowed_extensions=['svg'])])

    class Meta:
        verbose_name_plural = 'subcategories'
        ordering = ['id']

    def __str__(self):
        return self.name + '(' + str(self.id) + ')'


class TypesOfCard(models.TextChoices):
    """ Each card must have a type for the convenience of the user(sorting) """

    WORD = 'W', 'Word'
    DIALOGUE = 'D', 'Dialogue'
    SENTENCE = 'S', 'Sentence'


class Card(models.Model):
    """
        Model for the cards with the content.
        The card can be connected to different categories at
        the same time(many to many relationship)
    """
    subCategoryId = models.ManyToManyField(SubCategory)
    content = models.TextField('Content')
    # The card must have exactly one type out of TypesOfCard
    type = models.CharField(max_length=1, choices=TypesOfCard.choices,
                            default=TypesOfCard.WORD)
    # notes = models.CharField('Notes', blank=True, max_length=255)
    # Pronunciation for the card is optional
    pronunciation = models.FileField('Pronunciation', upload_to=upload_to('cards/sounds/'),
                                     validators=[FileExtensionValidator(allowed_extensions=['mp3'])],
                                     null=True, blank=True)
    # Translit of pronunciation is optional
    translit_of_pronunciation = models.TextField('Translit of pronunciation', null=True, blank=True)

    class Meta:
        ordering = ['-pk']

    def __str__(self):
        return self.content + '(' + str(self.id) + ')'


class Favourite(models.Model):
    """
        Model for user's favourite cards.
    """
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    # For sorting by `default`
    data_added = models.DateTimeField(default=now)

    class Meta:
        ordering = ['-data_added']

    def __str__(self):
        return 'card ' + str(self.card.id) + ' -> user ' + str(self.owner.id) + \
               ' (' + str(self.id) + ') '


class ArrayPosition(Func):
    """
        Class to solve one of the Django's problems.
        This class is used for filtering(user's sorting option) the cards.
    """
    function = 'array_position'

    def __init__(self, items, *expressions, **extra):
        if isinstance(items[0], int):
            base_field = IntegerField()
        else:
            base_field = CharField(max_length=max(len(i) for i in items))
        first_arg = Value(list(items), output_field=ArrayField(base_field))
        expressions = (first_arg,) + expressions
        super().__init__(*expressions, **extra)
