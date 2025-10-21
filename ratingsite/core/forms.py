from django import forms

class TokenLoginForm(forms.Form):
    token = forms.CharField(
        max_length=64,
        widget=forms.TextInput(attrs={"placeholder": "Enter your token"})
    )

class RateForm(forms.Form):
    appearance_score = forms.IntegerField(min_value=1, max_value=10)
    personality_score = forms.IntegerField(min_value=1, max_value=10)
    item_id = forms.IntegerField(widget=forms.HiddenInput)