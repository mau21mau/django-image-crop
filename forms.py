from django import forms
from core.models import New

class TesteForm(forms.ModelForm):
    #foo = forms.ModelChoiceField(Foo.objects, widget=CustomWidget())

    class Meta:
        model = New

    def __init__(self, *args, **kwargs):
        super(TesteForm, self).__init__(*args, **kwargs)
        self.fields['img'].widget.form_instance = self