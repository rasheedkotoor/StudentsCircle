from django.urls import path
from django.views.generic import TemplateView

from .views import AdminHomeView, UnionRegister, UnionsListView,  UnionDetailView, add_page_admin

app_name = 'adminn'

urlpatterns = [
    path('', AdminHomeView.as_view(), name='home'),
    path('union_register/', UnionRegister.as_view(), name='union_register'),
    path('union_list/', UnionsListView.as_view(), name='union_list'),
    path('union_details/<int:pk>', UnionDetailView.as_view(), name='union_details'),

    path('add_page_admin/', add_page_admin, name='add_page_admin'),

]

