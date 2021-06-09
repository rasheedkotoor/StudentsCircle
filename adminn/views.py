from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from accounts.models import Student, Union, User, PageAdmin
from accounts.forms import UnionSignUpForm
from student.models import Post, Comment, SubComment, Like
from student.models import Post
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView, DetailView


# Create your views here.


class AdminHomeView(TemplateView):
    template_name = "admin/home.html"

    def get_context_data(self, *args, **kwargs):
        context = super(AdminHomeView, self).get_context_data(**kwargs)
        context['students'] = User.objects.filter(is_union=False, is_superuser=False)
        context['unions'] = User.objects.filter(is_union=True)
        context['posts'] = Post.objects.all()
        context['comments'] = Comment.objects.all()
        return context


class UnionRegister(CreateView):
    model = User
    form_class = UnionSignUpForm
    template_name = 'accounts/union_register.html'

    def form_valid(self, form):
        user = form.save()
        return redirect('/adminn/union_list/')


class UnionsListView(TemplateView):
    template_name = "admin/union_list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(UnionsListView, self).get_context_data(**kwargs)
        context['unions'] = User.objects.filter(is_union=True)

        # for uni in unions:
        #     uni.members = uni.friends
        #     print(uni.members, "--------------------------------------")
        #     context['members'] = uni.members
        return context


class UnionDetailView(DetailView):
    model = User
    template_name = 'admin/union_details.html'


@login_required(login_url='/accounts/login')
def add_page_admin(request):
    page = request.POST['page']
    admin = request.POST['admin']
    union = User.objects.get(username=page)
    if User.objects.filter(username=admin).exists():
        user = User.objects.get(username=admin)
        new_admin, created = PageAdmin.objects.get_or_create(page=union, admin=user)
        user.is_staff = True
        user.is_verified = True
        user.student.union = union.union
        user.save()
        return JsonResponse('true', safe=False)
    else:
        print("somthidsn wronge")
        return JsonResponse('false', safe=False)

