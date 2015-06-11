from django import forms

class Buyer_SendOrderForm(forms.Form):
    agency_id = forms.CharField(label='Buyer Agency ID', max_length=100)
    company_id = forms.CharField(label='Buyer Client ID', max_length=100)
    person_id = forms.CharField(label='Buyer Person ID', max_length=100)
    payload = forms.CharField(label='Payload', max_length=5000, widget=forms.Textarea)

