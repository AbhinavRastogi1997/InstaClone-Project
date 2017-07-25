"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

#importing various views from myapp.views
from myapp.views import SignUp_view
from myapp.views import login_view
from myapp.views import post_view
from myapp.views import feed_view
from myapp.views import like_view
from myapp.views import comment_view
from myapp.views import upvote_view
from myapp.views import userpost_view
from myapp.views import logout_view

#Creating various urls
urlpatterns = [
    url('logout/',logout_view),
    url('userpost/',userpost_view),
    url('upvote/',upvote_view),
    url('comment/',comment_view),
    url('like/',like_view),
    url('feed/',feed_view),
    url('posts/',post_view),
    url('login/', login_view),
    url('',SignUp_view)

]
