import requests
from django.contrib.auth.decorators import login_required

from accounts.models import Student, Union, User, MemberRequest, FriendRequest
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.handlers.wsgi import WSGIRequest
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView, DetailView
from student.forms import CreatePostForm
from student.models import Post
from student.views import UserHomeView


# Create your views here.


class UnionDetailView(DetailView):
    model = User
    template_name = 'union/union_detail.html'

    def get_context_data(self, **kwargs):
        context = super(UnionDetailView, self).get_context_data(**kwargs)
        user = self.request.user
        username = kwargs['object']
        union = User.objects.get(username=username)
        last_post = union.pk
        post = Post.objects.filter(user=union.pk).order_by('-created').first()

        context['user'] = user
        context['post'] = post
        context['union'] = union
        return context


class MyUnionDetailView(LoginRequiredMixin, View):
    template_name = 'union/my_union.html'

    def get(self, request: WSGIRequest) -> HttpResponse:
        union = request.user.student.union
        members = Student.objects.filter(union=union.pk)
        union_post = Post.objects.filter(user=union.pk)

        context = {"union": union, "members": members, "union_post": union_post}
        return render(request, self.template_name, context)


class UnionAdminView(LoginRequiredMixin, View):
    template_name = 'union/union_admin_panel.html'

    def get(self, request: WSGIRequest) -> HttpResponse:
        post_form = CreatePostForm()
        union = request.user.student.union
        members = Student.objects.filter(union=union)
        member_requests = FriendRequest.objects.filter(to_user=union.user)

        context = {"union": union, "post_form": post_form, "members": members, 'member_requests': member_requests}
        return render(request, self.template_name, context)

    def post(self, request: WSGIRequest) -> HttpResponse:
        post_form = CreatePostForm(request.POST, request.FILES)
        union = request.user.student.union.user

        if post_form.is_valid():
            obj = post_form.save(commit=False)
            obj.user = union
            obj.save()
            return redirect('union:my_union')

        context = {"post_form": CreatePostForm()}
        return render(request, self.template_name, context)


@login_required(login_url='/accounts/login')
def union_join_req(request):
    union_id = request.POST['union_id']
    user_id = request.POST['user_id']
    value = request.POST['value']
    user = get_object_or_404(User, id=user_id)
    union = get_object_or_404(Union, user=union_id)

    if value == 'Accept':
        j_request = FriendRequest.objects.filter(
            from_user=user_id,
            to_user=union_id).first()
        user.is_verified = True
        user.student.union = union
        user.save()
        user.student.save()
        j_request.delete()
        return JsonResponse('Remove', safe=False)
    elif value == 'Reject':
        j_request = FriendRequest.objects.filter(
            from_user=user_id,
            to_user=union_id).first()
        j_request.delete()
        return JsonResponse('false', safe=False)
    elif value == 'Remove':
        user.student.union.remove(union_id)
        return JsonResponse('false', safe=False)
