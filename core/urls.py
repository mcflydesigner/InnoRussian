from django.urls import path
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

from .views import (IndexPageView,
                    CategoryListView,
                    SubCategoryListView,
                    FavouriteView,
                    FavouritesControlView,
                    SearchResultView,
                    CardListView)

app_name = 'core'

urlpatterns = [
    path('', IndexPageView.as_view(), name='main'),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('images/favicon.ico'))),
    path('dashboard/category/', CategoryListView.as_view(),
         name='category-list'),
    path('dashboard/category/<int:cat_id>/', SubCategoryListView.as_view(),
         name='subcategory-list'),
    path('dashboard/category/<int:subcat_id>/card/', CardListView.as_view(),
         name='card-list'),
    path('dashboard/favourite/', FavouriteView.as_view(), name='favourite'),
    path('dashboard/favourite/add/<int:card_id>/', FavouritesControlView.as_view(),
         name='favourite-add'),
    path('dashboard/favourite/del/<int:card_id>/', FavouritesControlView.as_view(),
         name='favourite-del'),
    path('dashboard/search/', SearchResultView.as_view(), name='search'),
]