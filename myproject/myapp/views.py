# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta, datetime
from django.utils import timezone


# Create your views here.
#importing various django builtin functions,models and forms
from django.shortcuts import render,redirect
from forms import SignUp_form,Login_form,Post_form,Like_form,Comment_form,Upvote_form,Userpost_form
from models import UserModel,SessionToken,PostModel,LikeModel,CommentModel,UpvoteModel
from django.contrib.auth.hashers import make_password,check_password
from myproject.settings import BASE_DIR

#importing the clarifai module
from clarifai.rest import ClarifaiApp
API_KEY='cc0a3d1823a8451da412642e6ba8c932' #Access Token for using the Clarifai API

#importing sendgrid module
import  sendgrid
SG_API_KEY='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' #Access Token for using the Sendgrid API

#imoorting  Imagur module
from imgurpython import ImgurClient
CLIENT_ID='af85e35148e525b'
CLIENT_SECRET='93a2f3f397076f1ab4a634a16bc9becf36c0acc2'

#The SignUp view
def SignUp_view(request):
    if request.method == "POST":
        form = SignUp_form(request.POST)
        if form.is_valid():#extracting user information
            username = form.cleaned_data['username']
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # saving data to DB
            user = UserModel(name=name, password=make_password(password), email=email, username=username)
            user.save()

            #using sendgrid api to send emails
            my_client = sendgrid.SendGridAPIClient(apikey=SG_API_KEY)

            payload = {
                "personalizations": [
                    {
                        "to": [
                            {
                                "email": user.email
                            }
                        ],
                        "subject": 'Welcome Message'
                    }
                ],
                "from": {
                    "email": 'abhinavrastogidtuite@gmail.com',
                    "name": 'Upload To Win'
                },
                "content": [
                    {
                        "type": "text/html",
                        "value": "Welcome %s! Login to Upload Pictures & Win Points!"%(user.name)
                    }
                ]
            }

            my_client.client.mail.send.post(request_body=payload)

            return render(request , 'success.html')
    else:
        form= SignUp_form()
    return render(request,'index.html',{'form':form})

#Defining the login view
def login_view(request):

    if request.method == "POST":
        form = Login_form(request.POST)
        if form.is_valid():#extracting the information typed by the user
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = UserModel.objects.filter(username=username).first()
            if user:
                if not check_password(password,user.password):
                    message="The Password is incorrect! Please try Again."
                    return render(request, 'login.html', {'form':form , 'message':message})
                else:#creating the session token for the user
                    token=SessionToken(user=user)
                    token.create_token()
                    token.save()
                    response = redirect('/feed/')
                    response.set_cookie(key='session_token',value=token.session_token)
                    return response

            else:
                message="This user does not exist! Please try Again."
                return render(request, 'login.html', {'form': form, 'message': message})



    else:
        form=Login_form()
        return render(request, 'login.html', {'form':form})

#Defining the post view
def post_view(request):
    user=check_validation(request)
    if user:

        if request.method =="POST":

            form = Post_form(request.POST,request.FILES)
            if form.is_valid():#extraction information related to posts
                image = form.cleaned_data.get('image')
                caption = form.cleaned_data.get('caption')

                post = PostModel(image=image,caption=caption,user=user)
                post.save()#saving data to database
                path = str(BASE_DIR +"/"+ post.image.url)
                client= ImgurClient(CLIENT_ID,CLIENT_SECRET)
                post.image_url=client.upload_from_path(path,anon=True)['link']
                post.save()

                 #Using the Clarifai API
                app = ClarifaiApp(api_key=API_KEY)
                model = app.models.get('logo')
                response = model.predict_by_url(url=post.image_url)
                if response["status"]['code'] == 10000:
                    if len(response["outputs"][0]['data']):
                        value = response["outputs"][0]['data']["regions"][0]["data"]["concepts"][0]["value"]
                        if value < 0.1:
                            points = 0
                        elif value < 0.2:
                            points = 1
                        elif value < 0.3:
                            points = 2
                        elif value < 0.4:
                            points = 3
                        elif value < 0.5:
                            points = 4
                        elif value < 0.6:
                            points = 5
                        elif value < 0.7:
                            points = 6
                        elif value < 0.8:
                            points = 7
                        elif value < 0.9:
                            points = 8
                        elif value < 0.99:
                            points = 9
                        else:
                            points = 10

                        post.points=points
                        post.save()

                    else:
                        post.points=0
                        post.save()

                return redirect('/feed/')


        else:
            form=Post_form()

        return render(request,'post.html',{'form':form})

    else:
        return redirect('/login/')

#Defining the Feed view
def feed_view(request):
    user=check_validation(request)

    if user:
        posts = PostModel.objects.all().order_by('-created_on')

        for post in posts:
            existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()

            if existing_like:
                post.has_liked = True

        Comments=CommentModel.objects.all()

        for comment in Comments:
            existing_upvote=UpvoteModel.objects.filter(comment_id=comment.id,user=user)
            if existing_upvote:
                comment.has_upvoted=True

        #Calculating the total score of the user
        total=PostModel.objects.filter(user=user)
        sum=0
        score=0
        while sum!=len(total):
            score+=total[sum].points
            sum=sum+1

        usernames=UserModel.objects.all()

        return render(request, 'feed.html', {'posts': posts , 'user':user.username ,'usernames':usernames,'Comments':Comments, 'total_points':score })

    else:
        return redirect('/login/')

#Defining the Like View
def like_view(request):
    user = check_validation(request)
    if user and request.method=="POST":
        form = Like_form(request.POST)
        if form.is_valid():#extracting the post id of the post which the user liked
            post_id = form.cleaned_data.get('post').id
            existing_like = LikeModel.objects.filter(post_id=post_id ,user=user)

            if not existing_like:
                like=LikeModel.objects.create(post_id=post_id ,user=user)
                like.save()#saving to db

                #Using sendgrid API to send emails
                my_client = sendgrid.SendGridAPIClient(apikey=SG_API_KEY)

                payload = {
                    "personalizations": [
                        {
                            "to": [
                                {
                                    "email": like.post.user.email
                                }
                            ],
                            "subject": 'Like Message'
                        }
                    ],
                    "from": {
                        "email": 'abhinavrastogidtuite@gmail.com',
                        "name": 'Upload To Win'
                    },
                    "content": [
                        {
                            "type": "text/html",
                            "value": "Your post (#%s) has been liked by %s :)"%(like.post.caption,user.username)
                        }
                    ]
                }

                my_client.client.mail.send.post(request_body=payload)
            else:
                existing_like.delete()

        return redirect('/feed/')
    else:
        return redirect('/login/')

#Defining the Comment View
def comment_view(request):
    user = check_validation(request)
    if user and request.method=='POST':
        form=Comment_form(request.POST)
        if form.is_valid():#extracting data related to comments
            post_id = form.cleaned_data.get('post').id
            comment_text = form.cleaned_data.get('comment_text')
            comment = CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text)
            comment.save() #saving comments to db

            # Using the sengrid API to send emails
            my_client = sendgrid.SendGridAPIClient(apikey=SG_API_KEY)

            payload = {
                "personalizations": [
                    {
                        "to": [
                            {
                                "email": comment.post.user.email
                            }
                        ],
                        "subject": 'Comment Message'
                    }
                ],
                "from": {
                    "email": 'abhinavrastogidtuite@gmail.com',
                    "name": 'Upload To Win'
                },
                "content": [
                    {
                        "type": "text/html",
                        "value": "%s commented on your post(# %s) :)" % (user.username , comment.post.caption)
                    }
                ]
            }

            my_client.client.mail.send.post(request_body=payload)

            return redirect('/feed/')
        else:
            return redirect('/feed/')


    else:
        return redirect('login/')

#Defining the Upvote View
def upvote_view(request):
    user=check_validation(request)
    if user and request.method=="POST":
        form=Upvote_form(request.POST)
        if form.is_valid():#extracting the comment id of the comment that was upvoted by the user
            comment_id=form.cleaned_data.get('comment').id
            existing_upvote=UpvoteModel.objects.filter(comment_id=comment_id,user=user)

            if existing_upvote:
                existing_upvote.delete() #deleting the upvote if it already exists
            else:
                UpvoteModel.objects.create(comment_id=comment_id, user=user) #saving the upvote to the db


        return redirect('/feed/')

    else:
        return redirect('/feed/')

#Defining the Userpost View
def userpost_view(request):
    user=check_validation(request)
    if user and request.method=="POST":
        form=Userpost_form(request.POST)
        if form.is_valid():#extracting the username from the search bar in the feed view
            username=form.cleaned_data.get('username')
            user2=UserModel.objects.filter(username=username)
            if user2:
                posts=PostModel.objects.filter(user=user2)

                total = PostModel.objects.filter(user=user2)
                sum = 0
                score = 0 #Claculating the total score of the particular user
                while sum!=len(total):
                    score += total[sum].points
                    sum=sum+1


                return render(request,'user_post.html',{'posts':posts , 'username':username , 'total_points':score})

            else:
                return redirect('/feed/')
    else:
        return redirect('/feed/')

#Defining the LogOut view
def logout_view(request):
    user=check_validation(request)
    if user:
        response = redirect('/login/')
        response.delete_cookie(key='session_token')#Deleting the cookie to log the user out.
        return response
    else:
        return redirect('/feed/')

#Defining the function to check user authentication
def check_validation(request):
    if request.COOKIES.get('session_token'):
        session=SessionToken.objects.filter(session_token=request.COOKIES.get("session_token")).first()
        if session:
            time_to_live= session.created_on + timedelta(days=1)

            if time_to_live>timezone.now():
                return session.user

    else:
        return None