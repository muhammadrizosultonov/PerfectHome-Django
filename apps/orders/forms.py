from django import forms
from .models import OrderRequest


class OrderRequestForm(forms.ModelForm):
    class Meta:
        model = OrderRequest
        fields = ["name", "phone", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "w-full border rounded px-3 py-2"}),
            "phone": forms.TextInput(attrs={"class": "w-full border rounded px-3 py-2", "type": "tel"}),
            "message": forms.Textarea(attrs={"rows": 4, "class": "w-full border rounded px-3 py-2"}),
        }
