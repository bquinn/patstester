from django import forms

class Buyer_SendOrderForm(forms.Form):
    agency_id = forms.CharField(label='Buyer Agency ID', max_length=100)
    company_id = forms.CharField(label='Buyer Client ID', max_length=100)
    person_id = forms.CharField(label='Buyer Person ID', max_length=100)
    payload = forms.CharField(label='Payload', max_length=5000, widget=forms.Textarea)

class ConfigurationForm(forms.Form):
    agency_id = forms.CharField(label='Agency ID', max_length=100)
    agency_api_key = forms.CharField(label='Agency API Key', max_length=100)
    agency_user_id = forms.CharField(label='Agency User ID', max_length=100)
    agency_company_id = forms.CharField(label='Agency Company ID', max_length=100)
    agency_person_id = forms.CharField(label='Agency Person ID', max_length=100)
    publisher_id = forms.CharField(label='Publisher ID', max_length=100)
    publisher_api_key = forms.CharField(label='Publisher API Key', max_length=100)
