from django.urls import path
from django.views.generic import TemplateView
from .views import UnionDetailView, MyUnionDetailView, UnionAdminView, union_join_req

app_name = 'union'

urlpatterns = [
    path('details/<int:pk>', UnionDetailView.as_view(), name='details'),
    path('my_union', MyUnionDetailView.as_view(), name='my_union'),
    path('union_admin', UnionAdminView.as_view(), name='union_admin'),
    path('join_req/', union_join_req, name='union_join_req'),

]