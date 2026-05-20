from django import forms
from .models import Reclamation
from equipes.models import Equipe

from django import forms
from .models import Reclamation

from django import forms
from .models import Reclamation


from django import forms
from .models import Reclamation, ReclamationCommentaire


class ReclamationForm(forms.ModelForm):
    class Meta:
        model = Reclamation
        fields = ['equipe', 'type_reclamation', 'description', 'fichier_joint']


class DecisionReclamationForm(forms.ModelForm):
    class Meta:
        model = Reclamation
        fields = ['statut', 'decision', 'document_final']


class CommentaireForm(forms.ModelForm):
    class Meta:
        model = ReclamationCommentaire
        fields = ['message']

class DecisionReclamationForm(forms.ModelForm):

    class Meta:
        model = Reclamation
        fields = ['statut', 'decision', 'document_final']
        widgets = {
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'decision': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Commentaire / décision'}),
            'document_final': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }       