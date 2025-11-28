from django import forms
from .qr_utils import QRGenerator


class QRForm(forms.Form):
    text = forms.CharField(
        label='Текст или ссылка для QR-кода',
        max_length=1000,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Введите текст или ссылку...'
        })
    )

    size = forms.ChoiceField(
        label='Размер QR-кода',
        choices=[
            ('200', 'Маленький (200x200)'),
            ('300', 'Средний (300x300)'),
            ('400', 'Большой (400x400)'),
        ],
        initial='300',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    format_type = forms.ChoiceField(
        label='Формат файла',
        choices=[(key, value) for key, value in QRGenerator.get_supported_formats().items()],
        initial='PNG',
        widget=forms.Select(attrs={'class': 'form-select'})
    )