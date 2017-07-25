from django import forms


from models import UserModel,PostModel,LikeModel,CommentModel,UpvoteModel

#Creating the Signup form
class SignUp_form(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ['email', 'username', 'name', 'password']

#Creating the Login form
class Login_form(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ['username','password']
#Creating the Post form
class Post_form(forms.ModelForm):
    class Meta:
        model = PostModel
        fields = ['image','caption']
#Creating the Like form
class Like_form(forms.ModelForm):
    class Meta:
        model = LikeModel
        fields = ['post']
#Creating the Comment form
class Comment_form(forms.ModelForm):
    class Meta:
        model = CommentModel
        fields = ['post','comment_text']
#Creating the Upvote form
class Upvote_form(forms.ModelForm):
    class Meta:
        model = UpvoteModel
        fields = ['comment']
#Creating the UserPost form
class Userpost_form(forms.ModelForm):
    class Meta:
        model =  UserModel
        fields = ['username']
