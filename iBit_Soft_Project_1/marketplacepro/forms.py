from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    CATEGORY_CHOICES = [
        ('None', 'None'),
        ('Phone', 'Phone'),
        ('Laptop', 'Laptop'),
        ('Consoles', 'Consoles'),
    ]

    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        initial='None',
        widget=forms.Select(attrs={'class': 'form-control', 'style': 'width: 200px; display: block; margin: 0 auto;'})
    )

    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'price', 'stock', 'image']


class DateSelectionForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Select a date")
