from django import forms

from .models import Comment

class Comments(forms.Form):
    comment = forms.CharField(max_length=5000)

class CommentForm(forms.ModelForm):
	class Meta:
		model = Comment
		fields = [
            'userProfile',
            'content',
            'date'

		]