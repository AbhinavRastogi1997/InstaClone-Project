# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
from django.db import models
import uuid



#Creating a model to store user information
class UserModel(models.Model):
  email = models.EmailField()
  name = models.CharField(max_length=120)
  username = models.CharField(max_length=120)
  password = models.CharField(max_length=40)
  created_on = models.DateTimeField(auto_now_add=True)
  updated_on = models.DateTimeField(auto_now=True)

#Creating a model to store the session token and other relevant feilds
class SessionToken(models.Model):
  user = models.ForeignKey(UserModel)
  session_token=models.CharField(max_length=255)
  created_on = models.DateTimeField(auto_now_add=True)
  is_valid = models.BooleanField(default=True)


  def create_token(self):
    self.session_token=uuid.uuid4()

#Creating a model to store the posts and various other relevant feilds
class PostModel(models.Model):
  user = models.ForeignKey(UserModel)
  image = models.FileField(upload_to='user_images')
  image_url = models.CharField(max_length=255)
  caption = models.CharField(max_length=240)
  points=models.IntegerField(default=0)
  created_on = models.DateTimeField(auto_now_add=True)
  updated_on = models.DateTimeField(auto_now=True)
  has_liked = False

  @property
  def like_count(self):
    return len(LikeModel.objects.filter(post=self))

  @property
  def comment_count(self):
    return len(CommentModel.objects.filter(post=self))




#Creating the model to store the likes
class LikeModel(models.Model):
  user=models.ForeignKey(UserModel)
  post=models.ForeignKey(PostModel)
  created_on = models.DateTimeField(auto_now_add=True)
  updated_on = models.DateTimeField(auto_now=True)

#Creating a model to store the comments
class CommentModel(models.Model):
  user = models.ForeignKey(UserModel)
  post = models.ForeignKey(PostModel)
  comment_text = models.CharField(max_length=555)
  created_on = models.DateTimeField(auto_now_add=True)
  updated_on = models.DateTimeField(auto_now=True)
  has_upvoted = False

  @property
  def upvotecount(self):
    return len(UpvoteModel.objects.filter(comment=self))

#Creating a model to store the Upvotes
class UpvoteModel(models.Model):
  user=models.ForeignKey(UserModel)
  comment=models.ForeignKey(CommentModel)
  created_on = models.DateTimeField(auto_now_add=True)
  updated_on = models.DateTimeField(auto_now=True)



