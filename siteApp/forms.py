from django import forms
from django.contrib.auth.models import User
from siteApp.models import BaseModel, CommentModel, JobModel, PollModel, PollOptionModel, StoryModel, UserModel
from django.forms import ModelForm


class BaseForm(ModelForm):
    
    class Meta:
        modal = BaseModel
        fields = ["type"]

    def pre_save(self):
        new_obj = self.save(commit=False)
        new_obj.source_id =  new_obj.id
        
        new_obj.by = UserModel.objects.get_or_create(
            source_id="Anonymous-User", 
            site_created=True
        )[0]

        return new_obj


class StoryForm(BaseForm):

    class Meta(BaseForm.Meta):
        model = StoryModel
        fields = BaseForm.Meta.fields + ["url", "title"]


class JobForm(BaseForm):

    class Meta(BaseForm.Meta):
        model = JobModel
        fields = BaseForm.Meta.fields + ["text", "title", "url"]


class CommentForm(BaseForm):

    class Meta(BaseForm.Meta):
        model = CommentModel
        fields = BaseForm.Meta.fields + ["text"]


class PollForm(BaseForm):

    class Meta(BaseForm.Meta):
        model = PollModel
        fields = BaseForm.Meta.fields + ["text", "title"]


class PollOptionForm(BaseForm):

    class Meta(BaseForm.Meta):
        model = PollOptionModel
        fields = BaseForm.Meta.fields + ["title"]


class UserSubscriptionForm(forms.ModelForm):
    password = forms.PasswordInput(
        write_only=True, 
        required=True, 
        min_length=7,
        max_length=50
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class UserLoginForm(forms.ModelForm): 
    password = forms.PasswordInput(
        write_only=True, 
        required=True, 
        min_length=7,
        max_length=50
    )

    class Meta:
        model = User
        fields = ['email', 'password']



