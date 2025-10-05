from django import forms
from .models import ClubPost

class ClubPostForm(forms.ModelForm):
    class Meta:
        model = ClubPost
        fields = ["title", "content"]
