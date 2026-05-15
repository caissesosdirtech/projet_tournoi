from django import forms
from .models import Reclamation
from equipes.models import Equipe

class ReclamationForm(forms.ModelForm):

    class Meta:
        model = Reclamation
        fields = ['equipe', 'type_reclamation', 'description', 'fichier_joint']

        widgets = {
            'equipe': forms.Select(attrs={'class': 'form-control'}),
            'type_reclamation': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Décrivez votre réclamation...'
            }),
            'fichier_joint': forms.FileInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Tous obligatoires sauf description
        self.fields['equipe'].required = True
        self.fields['type_reclamation'].required = True
        self.fields['fichier_joint'].required = True
        self.fields['description'].required = False

        # Charger les équipes existantes
        self.fields['equipe'].queryset = Equipe.objects.all()

class DecisionReclamationForm(forms.ModelForm):
    class Meta:
        model = Reclamation
        fields = ['statut', 'decision', 'document_final']
        widgets = {
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'decision': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Commentaire / décision'}),
            'document_final': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }       