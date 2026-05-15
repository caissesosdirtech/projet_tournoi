from django import forms
from .models import InfoTournoi

class InfoTournoiForm(forms.ModelForm):
    class Meta:
        model = InfoTournoi
        fields = ['titre', 'contenu', 'priorite', 'equipe']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre'}),
            'contenu': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Contenu'}),
            'priorite': forms.Select(attrs={'class': 'form-control'}),
            'equipe': forms.Select(attrs={'class': 'form-control'}),
        }