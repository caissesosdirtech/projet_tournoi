from django import forms
from .models import Reclamation
from equipes.models import Equipe

from django import forms
from .models import Reclamation

from django import forms
from .models import Reclamation


from django import forms
from .models import Reclamation, ReclamationCommentaire


from django import forms
from .models import Reclamation


from django import forms
from .models import Reclamation


# FORMULAIRE UTILISATEUR
class ReclamationForm(forms.ModelForm):

    class Meta:

        model = Reclamation

        fields = [

            'equipe',

            'type_reclamation',

            'description',

            'fichier_joint'

        ]

        widgets = {

            'description': forms.Textarea(attrs={

                'rows': 5,

                'placeholder':
                'Décrivez précisément votre recours...'

            }),

        }


# FORMULAIRE COMMISSION
class DecisionReclamationForm(forms.ModelForm):

    class Meta:

        model = Reclamation

        fields = [

            'statut',

            'decision_commission',

            'commentaire_admin',

            'document_final'

        ]

        widgets = {

            'commentaire_admin': forms.Textarea(attrs={

                'rows': 4,

                'placeholder':
                'Décision officielle de la commission...'

            }),

        }

class DecisionReclamationForm(forms.ModelForm):
    class Meta:
        model = Reclamation
        fields = ['statut','decision_commission','commentaire_admin','document_final'
        ]


class CommentaireForm(forms.ModelForm):
    class Meta:
        model = ReclamationCommentaire
        fields = ['message']

class DecisionReclamationForm(forms.ModelForm):

    class Meta:

        model = Reclamation

        fields = [

            'statut',

            'decision_commission',

            'commentaire_admin',

            'document_final'

        ]

        widgets = {

            'commentaire_admin': forms.Textarea(attrs={

                'rows': 4,

                'placeholder':
                'Décision officielle de la commission...'

            }),

        }