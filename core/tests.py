import tempfile
from io import BytesIO
from django.db import transaction
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.utils import IntegrityError

from .decorators import for_all_methods
from .models import (Category,
                     SubCategory,
                     Card,
                     TypesOfCard,
                     Favourite)


@for_all_methods(override_settings(MEDIA_ROOT=tempfile.TemporaryDirectory(prefix='mediatest').name))
class CoreTests(TestCase):
    def test_create_category(self):
        image_file = SimpleUploadedFile('icon.svg', BytesIO().getvalue())
        # Create a category
        cat1 = Category.objects.create(name='Test category', picture=image_file)
        cat1.save()
        self.assertEqual(cat1.name, 'Test category')
        self.assertEqual(cat1.picture, f'categories/pictures/{cat1.id}.svg')
        with transaction.atomic():
            # name must be unique
            self.assertRaises(IntegrityError, Category.objects.create, name='Test category',
                              picture=image_file)

    def test_create_subcategory(self):
        image_file = SimpleUploadedFile('icon.svg', BytesIO().getvalue())
        # Create a subcategory
        subcat = SubCategory.objects.create(name='Test subcategory',
                                            picture=image_file)
        # Create a temp category for tests
        cat1 = Category.objects.create(name='Test category 1', picture=image_file)
        # Link the subcategory with a temp category
        subcat.categoryId.add(cat1)
        subcat.save()
        self.assertEqual(subcat.name, 'Test subcategory')
        self.assertEqual(subcat.picture, f'subcategories/pictures/{subcat.id}.svg')
        self.assertEqual(list(subcat.categoryId.all()), [cat1])
        with transaction.atomic():
            # name must be unique
            self.assertRaises(IntegrityError, SubCategory.objects.create, name='Test subcategory',
                              picture=image_file)

        # Create one more temporary category
        cat2 = Category.objects.create(name='Test category 2', picture=image_file)
        subcat.categoryId.add(cat1)  # Repeating must not duplicate the object
        subcat.categoryId.add(cat2)
        self.assertEqual(list(subcat.categoryId.all()), [cat1, cat2])

    def test_create_cards(self):
        # Create a card without specifying the file with pronunciation(.mp3)
        card1 = Card(content='Dialogue 1',
                     type=TypesOfCard.choices[1][0])
        card1.save()
        self.assertEqual(card1.content, 'Dialogue 1')
        self.assertEqual(card1.type, TypesOfCard.choices[1][0])

        image_file = SimpleUploadedFile('img.svg', BytesIO().getvalue())
        subcat1 = SubCategory.objects.create(name='Test subcategory 1',
                                             picture=image_file)
        card1.subCategoryId.add(subcat1)
        self.assertEqual(list(card1.subCategoryId.all()), [subcat1])
        subcat2 = SubCategory.objects.create(name='Test subcategory 2',
                                             picture=image_file)
        card1.subCategoryId.add(subcat1)  # Repeating must not duplicate the object
        card1.subCategoryId.add(subcat2)
        self.assertEqual(list(card1.subCategoryId.all()), [subcat1, subcat2])

        # Create a card with the file with pronunciation(.mp3) and corresponding translit
        voice_file = SimpleUploadedFile('voice.mp3', BytesIO().getvalue())
        card2 = Card(content='Word 2',
                     type=TypesOfCard.choices[0][0],
                     pronunciation=voice_file,
                     translit_of_pronunciation='Test translit')
        card2.save()
        self.assertEqual(card2.content, 'Word 2')
        self.assertEqual(card2.type, TypesOfCard.choices[0][0])
        self.assertEqual(card2.pronunciation, f'cards/sounds/{card2.id}.mp3')
        self.assertEqual(card2.translit_of_pronunciation, 'Test translit')

    def test_favourite_cards(self):
        # Create a temp user
        User = get_user_model()
        user = User.objects.create_user(email='normal@user.com', password='foo')
        # Create a temp card
        card = Card(content='Dialogue 1',
                    type=TypesOfCard.choices[1][0])
        card.save()
        # Create a favourite card
        favourite = Favourite.objects.create(card=card,
                                             owner=user)
        favourite.save()
        self.assertEqual(favourite.owner, user)
        self.assertEqual(favourite.card, card)
        self.assertNotEqual(favourite.data_added, None)

