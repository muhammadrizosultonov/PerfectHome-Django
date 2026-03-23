import re
from django import forms
from .models import OrderRequest


UZ_PHONE_REGEX = re.compile(r'^\+?998[\s-]?\d{2}[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}$')


class OrderRequestForm(forms.ModelForm):
    class Meta:
        model = OrderRequest
        fields = ["name", "phone", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "w-full border rounded px-3 py-2"}),
            "phone": forms.TextInput(attrs={"class": "w-full border rounded px-3 py-2", "type": "tel"}),
            "message": forms.Textarea(attrs={"rows": 4, "class": "w-full border rounded px-3 py-2"}),
        }

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()
        if not UZ_PHONE_REGEX.match(phone):
            raise forms.ValidationError("Telefon raqam +998XX XXX XX XX formatida bo‘lishi kerak.")

        digits = re.sub(r"\D", "", phone)
        if not digits.startswith("998") or len(digits) != 12:
            raise forms.ValidationError("Telefon raqam +998XX XXX XX XX formatida bo‘lishi kerak.")

        return f"+{digits}"
