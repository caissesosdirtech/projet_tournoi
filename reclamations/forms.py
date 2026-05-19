from django import forms
from .models import Reclamation
from equipes.models import Equipe

from django import forms
from .models import Reclamation

class ReclamationForm(forms.ModelForm):

    class Meta:
        model = Reclamation
        fields = '__all__'

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # champ obligatoire
        self.fields['fichier_joint'].required = True

        # message personnalisé
        self.fields['fichier_joint'].error_messages = {
            'required': "⚠ Veuillez joindre un fichier justificatif."
        }

class DecisionReclamationForm(forms.ModelForm):
    class Meta:
        model = Reclamation
        fields = ['statut', 'decision', 'document_final']
        widgets = {
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'decision': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Commentaire / décision'}),
            'document_final': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }       