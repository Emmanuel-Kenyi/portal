from django import forms
from .models import ClubPost, Club

class ClubPostForm(forms.ModelForm):
    class Meta:
        model = ClubPost
        fields = ["title", "content"]

class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter club name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter club description', 'rows': 4}),
        }
