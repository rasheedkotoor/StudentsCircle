import base64

from django.contrib import messages
from django.core.files.base import ContentFile
from django.db.models import OuterRef, Exists
from django.views.decorators.csrf import csrf_exempt

from accounts.models import Student, Union, User, FriendRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, DetailView, UpdateView, TemplateView

from .models import Post, Comment, SubComment, Like, Room, Message
from .forms import CreatePostForm, ProfileUpdateForm1, ProfileUpdateForm2


# Create your views here.


class UserHomeView(LoginRequiredMixin, View):
    template_name = 'student/studenthome.html'

    def get(self, request: WSGIRequest) -> HttpResponse:
        post_form = CreatePostForm()
        student = User.objects.filter(is_union=False, is_superuser=False).exclude(pk=request.user.pk)
        union = User.objects.filter(is_union=True)
        post = Post.objects.all()
        my_post = Post.objects.filter(user=request.user)
        friends = request.user.user_set.all()
        sent_friend_requests = FriendRequest.objects.filter(from_user=request.user)
        rec_friend_requests = FriendRequest.objects.filter(to_user=request.user)
        lu = request.user
        po = ''
        for po in post:
            po.liked = Like.objects.filter(user=lu, post=po) and True or False

        context = {"post_form": post_form, 'student': student, 'union': union,
                   'po': po, 'post': post, 'sent_friend_requests': sent_friend_requests,
                   'rec_friend_requests': rec_friend_requests, 'friends': friends}

        return render(request, self.template_name, context)

    def post(self, request: WSGIRequest) -> HttpResponse:
        post_form = CreatePostForm(request.POST, request.FILES)
        if not post_form.is_valid():
            messages.warning(self.request, 'Enter some text or Choose any file')
            return redirect('student:home')
        elif post_form.is_valid():
            obj = post_form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect('student:home')


@login_required(login_url='/accounts/login')
def add_comment(request):
    if request.POST['comment'] == '':
        return JsonResponse('error', safe=False)
    else:
        cmnt = request.POST['comment']
        post_id = request.POST['postid']
        post = Post.objects.get(pk=post_id)
        new_cmnt = Comment.objects.create(user=request.user, post=post, comment=cmnt)
        return JsonResponse('added', safe=False)


@login_required(login_url='/accounts/login')
def add_like(request):
    post_id = request.POST['postid']
    post = Post.objects.get(pk=post_id)
    new_like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        return JsonResponse('Liked', safe=False)
    else:
        return JsonResponse('Liked', safe=False)


class ProfileView(LoginRequiredMixin, View):
    template_name = "student/profile.html"

    def get(self, request: WSGIRequest) -> HttpResponse:
        me = Student.objects.get(user=request.user)
        p_form1 = ProfileUpdateForm1(instance=request.user)
        p_form2 = ProfileUpdateForm2(instance=me)

        context = {'p_form1': p_form1, 'p_form2': p_form2, 'me': me}
        return render(request, self.template_name, context)

    def post(self, request: WSGIRequest) -> HttpResponse:
        me = Student.objects.get(user=request.user)
        p_form2 = ProfileUpdateForm2(request.POST, instance=me)

        if p_form2.is_valid():
            p2 = p_form2.save(commit=False)
            p2.user = request.user
            p2.save()
            return redirect('student:profile')

        context = {"post_form": CreatePostForm()}
        return render(request, self.template_name, context)


@login_required(login_url='/accounts/login')
def edit_fullname(request):
    f_name = request.POST['first_name']
    l_name = request.POST['last_name']
    user_id = request.POST['user_id']
    me = User.objects.get(id=user_id)
    me.first_name = f_name
    me.last_name = l_name
    me.save()
    return JsonResponse('true', safe=False)


@login_required(login_url='/accounts/login')
def edit_profile_data(request):
    data = request.POST['editing_value']
    differ = request.POST['differ']
    user_id = request.POST['user_id']
    me = Student.objects.get(pk=user_id)
    us_me = User.objects.get(pk=user_id)

    if differ == 'bio':
        me.bio = data
        me.save()
        return JsonResponse('true', safe=False)
    elif differ == 'birthday':
        me.birth_date = data
        me.save()
        return JsonResponse('true', safe=False)
    elif differ == 'phone_number':
        us_me.phone_number = data
        us_me.save()
        return JsonResponse('true', safe=False)
    elif differ == 'location':
        me.location = data
        me.save()
        return JsonResponse('true', safe=False)
    elif differ == 'hobbies':
        me.hobbies = data
        me.save()
        return JsonResponse('true', safe=False)
    elif differ == 'interests':
        me.interests.append(data)
        me.save()
        return JsonResponse('true', safe=False)


class Timeline(LoginRequiredMixin, View):
    template_name = "student/timeline.html"

    def get(self, request: WSGIRequest) -> HttpResponse:
        me = request.user
        try:
            my_posts = Post.objects.filter(user=me)
        except:
            pass
        context = {'me': me, 'my_posts': my_posts}
        return render(request, self.template_name, context)


class Friends(LoginRequiredMixin, View):
    template_name = "student/friends.html"

    def get(self, request: WSGIRequest) -> HttpResponse:
        me = request.user

        friends = me.friends.all()

        context = {'me': me, 'friends': friends}
        return render(request, self.template_name, context)


class Unions(LoginRequiredMixin, View):
    template_name = "student/unions.html"

    def get(self, request: WSGIRequest) -> HttpResponse:
        me = request.user
        unions = User.objects.filter(is_union=True)
        try:
            my_union = me.student_set.union
        except:
            my_union = "not verified by a union"
        context = {'me': me, 'unions': unions, 'my_union': my_union}
        return render(request, self.template_name, context)


@login_required(login_url='/accounts/login')
def select_my_union(request):
    pk = request.POST['union']
    union = User.objects.get(pk=pk)
    if FriendRequest.objects.filter(from_user=request.user).exists():
        return JsonResponse('false', safe=False)
    else:
        f_request = FriendRequest.objects.create(
            from_user=request.user,
            to_user=union
        )
        return JsonResponse('true', safe=False)


@login_required(login_url='/accounts/login')
def upload_pp(request):
    pp = request.POST['profile_pic']
    user = request.user
    format, imgstr = pp.split(';base64,')
    ext = format.split('/')[-1]
    img = ContentFile(base64.b64decode(imgstr), name=user.username + '.' + ext)
    user.student.profile_img = img
    user.student.save()
    return redirect('student:profile')


@login_required(login_url='/accounts/login')
def chat_room(request, pk):
    user1 = request.user
    friends = user1.friends.all()
    if User.objects.filter(pk=pk).exists():
        user2 = User.objects.get(pk=pk)
        if Room.objects.filter(user2=user1, user1=user2).exists():
            room = Room.objects.get(user2=user1, user1=user2)
        else:
            room, created = Room.objects.get_or_create(user1=user1, user2=user2)
        messages_order = Message.objects.filter(room=room).order_by('-id')[:9]
        messages = reversed(messages_order)
        context = {'room': room, 'user1': user1, 'user2': user2, 'friends': friends, 'messages': messages}
        return render(request, 'student/chat.html', context)
    else:
        return redirect('student:friends')

