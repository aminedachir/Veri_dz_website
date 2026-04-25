from django import forms
from news.models import Article


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('title', 'content', 'source_url', 'category', 'image')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'vd-form-control', 'placeholder': 'Titre de l\'article…'}),
            'content': forms.Textarea(attrs={'class': 'vd-form-control', 'rows': 10, 'placeholder': 'Contenu de l\'article…'}),
            'source_url': forms.URLInput(attrs={'class': 'vd-form-control', 'placeholder': 'https://…'}),
            'category': forms.Select(attrs={'class': 'vd-form-control'}),
        }
