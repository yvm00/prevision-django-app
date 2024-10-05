from django import forms


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()


class ForecastForm(forms.Form):
    FREQ = (
        ('D', 'Дни'),
        ('M', 'Месяцы'),
        ('Y', 'Года'),
    )

    uploaded_file_url = forms.CharField(widget=forms.TextInput)
    frequency = forms.CharField(widget=forms.Select)
    period = forms.CharField(widget=forms.TextInput)
    dates = forms.CharField(widget=forms.Select)
    values = forms.CharField(widget=forms.Select)

