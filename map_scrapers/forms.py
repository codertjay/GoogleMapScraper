from django import forms
from .models import History


class HistoryUpdateForm(forms.ModelForm):
    class Meta:
        model = History
        fields = "__all__"
