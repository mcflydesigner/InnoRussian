from django.shortcuts import render
from django.views import View
from django.views.generic.list import ListView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import (Q, F, Case, When, PositiveIntegerField)
from django.http import Http404
from django.db import models
from ordered_set import OrderedSet

from .models import ArrayPosition
from .decorators import login_require_or_401
from .models import (Category,
                     SubCategory,
                     Favourite,
                     Card,
                     TypesOfCard)


class IndexPageView(View):
    """ Main page of the webapp """

    def get(self, request):
        return render(request, 'core/index.html')


class CategoryListView(ListView):
    """
        List of all categories
    """
    model = Category
    paginate_by = 6

    template_name = 'core/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        # GET parameter for the local search on the page
        q = extract_and_trip_question(self.request.GET)

        # If the local search is needed, just do it
        queryset = super().get_queryset()
        result = search_among_queryset(queryset, q,
                                       filter_dict={'name__icontains': q})

        # Generate temporary context to pass the following parameters to
        # the function 'get_context_data'
        self.request.tmpcontext = {
            'q': q
        }

        return result

    def get_context_data(self, *, object_list=None, **kwargs):
        # Generate the context for the template
        context = super().get_context_data(**kwargs)

        context.update(self.request.tmpcontext)
        context.update(generate_tmpcontext_for_search(self.request.tmpcontext['q'],
                                                      'Among categories...'))
        return context


class SubCategoryListView(ListView):
    """
        List of all subcategories for a given category
    """
    model = SubCategory
    paginate_by = 6

    template_name = 'core/subcategory_list.html'
    context_object_name = 'subcategories'

    def get_queryset(self):
        # We need to be sure that category with `cat_id` exists
        # before extracting subcategories for a given category
        cat_id = self.kwargs.get('cat_id', None)

        if not Category.objects.filter(pk=cat_id).exists():
            # If there is no such category,
            # we cannot find corresponding subcategories
            raise Http404("Such category doesn't exist")

        # GET parameter for the local search on the page
        q = extract_and_trip_question(self.request.GET)

        # Get cards which belong to the specified category
        queryset = SubCategory.objects.filter(categoryId=cat_id)
        # If the local search is needed, just do it
        result = search_among_queryset(queryset, q,
                                       filter_dict={'name__icontains': q})

        # Generate temporary context to pass the following parameters to
        # the function 'get_context_data'
        self.request.tmpcontext = {
            'q': q,
            'cat_id': cat_id,
        }

        return result

    def get_context_data(self, *, object_list=None, **kwargs):
        # Generate the context for the template
        context = super().get_context_data(**kwargs)
        context.update(self.request.tmpcontext)

        categoryName = Category.objects.filter(pk=self.request.tmpcontext['cat_id']).first().name
        placeholder = 'Among ' + categoryName.lower() + '...'

        context.update({'placeholder': placeholder,
                        'categoryName': categoryName})
        context.update(generate_tmpcontext_for_search(self.request.tmpcontext['q'],
                                                      placeholder))
        return context


""" 
    Options for user to sort the cards on the page with cards, possible options:
    1) 'DD' - cards that are showed by the ID of the cards in decreasing order
    2) 'W'- firstly show card which have type `word`, all remaining cards sort using 'DD'
    3) 'D'- firstly show card which have type `dialogue`, all remaining cards sort using 'DD'
    4) 'S'- firstly show card which have type `sentence`, all remaining cards sort using 'DD'
"""
SORTING_CARD_OPTIONS = [('DD', 'Default')] + TypesOfCard.choices


class CardListView(ListView):
    """
        List of all cards for a given subcategory
    """
    model = Card
    paginate_by = 10

    template_name = 'core/card_list.html'
    context_object_name = 'cards'

    def get_queryset(self):
        # We need to be sure that subcategory with the given ID exists
        # before extracting cards
        subcat_id = self.kwargs.get('subcat_id', None)
        # Extract sorting GET parameter for the order of the cards
        sort_param = self.request.GET.get('sort', SORTING_CARD_OPTIONS[0][0])

        if not Card.objects.filter(subCategoryId=subcat_id).exists():
            # If there is no such subcategory,
            # we cannot find corresponding cards
            raise Http404("Such subcategory doesn't exist")

        # Get cards which belong to the specified subcategory
        result = Card.objects.filter(subCategoryId=subcat_id)

        # GET parameter for the local search on the page
        q = extract_and_trip_question(self.request.GET)

        # If the local search is needed, just do it among content of the cards
        if q:
            result = filter_cards_by_q(result, q)
        # If we need to change the order of the cards, simply do it
        result, sorted_by = sort_cards_by_param(result, sort_param)

        # Generate temporary context to pass the following parameters to
        # the function 'get_context_data'
        self.request.tmpcontext = {
            'q': q,
            'subcat_id': subcat_id,
            'sorted_by': sorted_by,
        }

        if self.request.user.is_authenticated:
            # If the user is authenticated, we need to unite the cards
            # which belong to the given subcategory with cards which are
            # in the user's collection(their favourites)
            favourites = Favourite.objects.filter(owner=self.request.user)
            cards = union_favourites_and_cards(favourites, result)
            return cards

        # If the user is not authenticated, just return all cards
        return result

    def get_context_data(self, *, object_list=None, **kwargs):
        # Generate the context for the template
        context = super().get_context_data()
        context.update(self.request.tmpcontext)

        subcat_id = self.request.tmpcontext['subcat_id']
        subCategoryName = SubCategory.objects.get(pk=subcat_id).name
        placeholder = 'Among ' + subCategoryName.lower() + '...'

        context.update({'subCategoryName': subCategoryName})
        context.update(generate_tmpcontext_for_search(self.request.tmpcontext['q'],
                                                      placeholder))
        context.update(generate_tmpcontext_sorting(self.request.tmpcontext['sorted_by'],
                                                   SORTING_CARD_OPTIONS,
                                                   subCategoryName=subCategoryName,
                                                   subcat_id=subcat_id))

        return context


def find_sorting_method(sort_param, *, options) -> (str, str):
    """ Function to determine the sorting method on the page """
    for sorting_method in options:
        if sort_param == sorting_method[0]:
            # If the value from GET parameter is in the list of possible
            # values, just return the sorting method
            sorted_by = sorting_method
            break
    else:
        # Otherwise, return the default method for sorting
        sorted_by = options[0]

    return sorted_by


def sort_cards_by_param(queryset, sort_param) -> (list, (str, str)):
    """
        Function to sort cards by a given sorting parameter
    """
    # Initially, determine the sorting parameter
    sorted_by = find_sorting_method(sort_param, options=SORTING_CARD_OPTIONS)

    if sorted_by != SORTING_CARD_OPTIONS[0]:
        # If the queryset is not sorted according to the sorting parameter,
        # then sort by the parameter
        result = queryset.annotate(
            relevancy=(Case(When(Q(type=sort_param), then=1), When(~Q(type=sort_param), then=2),
                            output_field=PositiveIntegerField())
                       )).order_by('relevancy', '-id')
    else:
        # The queryset is already sorted according to the sorting parameter,
        # so, just return it
        result = queryset

    return result, sorted_by


def filter_cards_by_q(queryset, q):
    """ Function to sort cards according to the value of q """
    res = queryset.filter(Q(content__icontains=q) |
                          Q(translit_of_pronunciation__icontains=q))

    return res


def generate_tmpcontext_sorting(sorted_by, sort_options, **kwargs):
    """ Function to generate a temporary context for sorting of cards """
    tmpcontext = {
        'sorted_by': sorted_by,
        'sort_options': sort_options
    }

    for key, val in kwargs.items():
        tmpcontext[key] = val

    return tmpcontext


def union_favourites_and_cards(favourites, cards):
    """
        Function to unite user's favourites cards with a queryset of cards
    """
    # Using sets due to the fact that time complexity is O(1)
    # to check that an element is in the set
    favourites_set = set()
    resulting_cards = cards.all()

    for favour in favourites:
        favourites_set.add(favour.card.id)

    for card in resulting_cards:
        # Add new field to the card with the flag
        # to indicate is a card user's favourite or not
        if card.id in favourites_set:
            card.favourite = True
        else:
            card.favourite = False

    return resulting_cards


class FavouriteView(ListView):
    """
        List with all user's favourite cards
    """
    model = Favourite
    paginate_by = 10

    template_name = 'core/favourite_list.html'
    context_object_name = 'cards'

    def get_queryset(self):
        # GET parameter for the local search on the page
        q = extract_and_trip_question(self.request.GET)
        # Get all favourite cards which belongs to the user
        favourites = Favourite.objects.select_related('card').filter(owner=self.request.user)
        # Extract sorting GET parameter for the order of the cards
        sort_param = self.request.GET.get('sort', 'DD')

        # Generate temporary context to pass the following parameters to
        # the function 'get_context_data'
        self.request.tmpcontext = {
            'q': q,
            'sorted_by': None,
        }

        if not favourites:
            # If user doesn't have any favourite cards, then just
            # return an empty queryset
            return favourites

        # Default sorting of the cards
        card_ids = favourites.values_list('card__id', flat=True)
        result = Card.objects.filter(pk__in=card_ids). \
            annotate(ordering=ArrayPosition(card_ids, F('pk'),
                                            output_field=PositiveIntegerField())).order_by('ordering')

        # If the local search is needed, just do it among content of the cards
        if q:
            result = filter_cards_by_q(result, q)

        # If we need to change the order of the cards, simply do it
        result, sorted_by = sort_cards_by_param(result, sort_param)
        self.request.tmpcontext['sorted_by'] = sorted_by

        # We need to mark all cards as favourites
        result = union_favourites_and_cards(favourites, result)

        return result

    def get_context_data(self, *, object_list=None, **kwargs):
        # Generate the context for the template
        context = super().get_context_data()
        context.update(self.request.tmpcontext)
        placeholder = 'Among favourites...'

        context.update(generate_tmpcontext_for_search(self.request.tmpcontext['q'], placeholder))
        context.update(generate_tmpcontext_sorting(self.request.tmpcontext['sorted_by'],
                                                   SORTING_CARD_OPTIONS))

        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


def search_among_queryset(queryset, q, *, filter_dict):
    """ Function to perform filter on the given queryset """
    if q:
        # If q is not None, filter by it
        result = queryset.filter(**filter_dict)
    else:
        # If q is None, no need to filter, simply return queryset
        result = queryset

    return result


def generate_tmpcontext_for_search(q, placeholder):
    """ Function to generate context for the search """
    tmpcontext = {
        'searchPlaceholder': placeholder,
        'q': q
    }

    return tmpcontext


class FavouritesControlView(View):
    """
        View to add to / remove from user's favourite collection of cards.
    """

    def post(self, request, **kwargs):
        """ Method to add a card to user's favourite collection """
        response = {}

        # Check that the card with the provided id exists
        card = self._validate_card_id(request, **kwargs)
        if not card:
            # Otherwise, return error
            return self._return_error(request, response)

        # Check that card already is in user's collection
        if Favourite.objects.filter(card=card,
                                    owner=request.user).exists():
            # The card was already added before, return error
            return self._return_error(request, response)

        # Otherwise, add the card to user's collection
        new_favourite_card = Favourite(card=card,
                                       owner=request.user)
        new_favourite_card.save()

        # Return successful JSON response
        return JsonResponse(response, status=200)

    def delete(self, request, **kwargs):
        """ Method to remove a card from user's favourite collection """
        response = {}

        # Check that the card with the provided id exists
        card = self._validate_card_id(request, **kwargs)
        if not card:
            # Otherwise, return error
            return self._return_error(request, response)

        # Find favourite card's object
        favourite_card = Favourite.objects.filter(card=card,
                                                  owner=request.user).first()

        if not favourite_card:
            # The card was already removed before or was not in user's favourites,
            # so, return error
            return self._return_error(request, response, status=410)

        # Otherwise, remove the card successfully
        favourite_card = favourite_card.delete()

        # Return successful JSON response
        return JsonResponse(response, status=200)

    def _validate_card_id(self, request, **kwargs):
        """ Method to check that card with the provided id exists """
        card_id = kwargs.get('card_id', None)

        if not Card.objects.filter(pk=card_id).exists():
            # If the card doesn't exists, return None
            return None

        # Otherwise, such card exists, simply return it
        return Card.objects.filter(pk=card_id).first()

    def _return_error(self, request, response, status=409):
        """ Method which returns JSON response with the rror """
        response['error'] = 'Sorry, an unknown error occurred.'
        return JsonResponse(response, status=status)

    @method_decorator(login_require_or_401)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class TypesOfSearchSortingOptions(models.TextChoices):
    """
        Sorting options for the content of the global search view.
        Meaning of each one:
        1) 'DF' - default sorting, initially show all blocks for which we found something,
        all remaining ones show at the end
        2) 'CR' - firstly show all cards, then show remaining ones using 'DF'
        3) 'CT' - firstly show all categories, then show remaining ones using 'DF'
        4) 'SB' - firstly show all subcategories, then show remaining ones using 'DF'
    """
    DEFAULT = 'DF', 'Default'
    CARDS = 'CR', 'Cards'
    CATEGORIES = 'CT', 'Categories'
    SUBCATEGORIES = 'SB', 'Subcategories'


class SearchResultView(View):
    """
        Global search view
    """

    def get(self, request):
        # GET parameter for the global search
        filter_by = extract_and_trip_question(self.request.GET, defaultVal='')
        # Extract sorting GET parameter for the order of the content
        sort_param = request.GET.get('sort', default=TypesOfSearchSortingOptions.DEFAULT)
        # Determine the required sorting method(should be sort_param)
        sorted_by = find_sorting_method(sort_param, options=TypesOfSearchSortingOptions.choices)

        # Set up the context for the template
        context = {
            'q': filter_by,
        }

        if sorted_by[0] == TypesOfSearchSortingOptions.DEFAULT:
            # If the sorting is default, we will be adding blocks to the set
            # as we find content for a given filter_by
            q_found = OrderedSet()
        else:
            # If the sorting is not default, the first shown block must be
            # as was request by the user, so, our first element in the set will
            # be sorted_by
            q_found = OrderedSet([sorted_by])

        if filter_by:
            # Start search among categories
            categories = \
                Category.objects.filter(name__icontains=filter_by)
            if categories:
                # If we find something, add category block to the set
                # and add content to the context
                q_found.add(TypesOfSearchSortingOptions.choices[2])
                context['categories'] = categories

            # Search among subcategories
            subcategories = \
                SubCategory.objects.filter(name__icontains=filter_by)
            if subcategories:
                # If we find something, add subcategory block to the set
                # and add content to the context
                context['subcategories'] = subcategories
                q_found.add(TypesOfSearchSortingOptions.choices[3])

            # Search among cards
            cards = Card.objects.filter(Q(content__icontains=filter_by) |
                                        Q(translit_of_pronunciation__icontains=filter_by))
            if cards:
                # If we find something, add card block to the set
                # and add content to the context
                q_found.add(TypesOfSearchSortingOptions.choices[1])

            if request.user.is_authenticated:
                # If the user is authenticated, we need to unite the cards
                # which belong to the given subcategory with cards which are
                # in the user's collection(their favourites)
                favourites = Favourite.objects.filter(owner=request.user)
                context['cards'] = union_favourites_and_cards(favourites, cards)
            else:
                # If the user is not authenticated, just add all pure cards
                context['cards'] = cards

        # Set with all sorting of order choices except the default one
        q_all = set()
        q_all.update(TypesOfSearchSortingOptions.choices)
        q_all.remove(TypesOfSearchSortingOptions.choices[0])

        # q_found contains blocks for which we found some content
        context['q_found'] = q_found
        # q_notfound contains blocks for which we didn't find any content
        context['q_notfound'] = q_all.difference(q_found)
        context['sorted_by'] = sorted_by
        context.update(generate_tmpcontext_sorting(sorted_by, TypesOfSearchSortingOptions.choices))

        return render(request, 'core/search_list.html', context=context)


def extract_and_trip_question(requestData, paramName='q', defaultVal=None):
    """ Function which simply takes the parameter and strip it(remove spaces around) """
    q = requestData.get(paramName, defaultVal)
    if q:
        q = q.strip()

    return q
