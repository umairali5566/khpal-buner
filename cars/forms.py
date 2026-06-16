from django import forms
from django.contrib.auth.models import User
from cars.models import Car, CarImage, Inquiry, DealerProfile, City

class DealerProfileForm(forms.ModelForm):
    class Meta:
        model = DealerProfile
        fields = ['shop_name', 'owner_name', 'profile_picture', 'phone', 'whatsapp', 'address', 'city', 'google_maps_link']
        widgets = {
            'shop_name': forms.TextInput(attrs={'class': 'form-control'}),
            'owner_name': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.Select(attrs={'class': 'form-select'}),
            'google_maps_link': forms.URLInput(attrs={'class': 'form-control'}),
        }

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['brand', 'model', 'year', 'color', 'price', 'mileage', 'fuel_type', 'transmission', 'description', 'city']
        widgets = {
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'mileage': forms.NumberInput(attrs={'class': 'form-control'}),
            'fuel_type': forms.Select(attrs={'class': 'form-select'}),
            'transmission': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'city': forms.Select(attrs={'class': 'form-select'}),
        }

class CarImageForm(forms.ModelForm):
    class Meta:
        model = CarImage
        fields = ['image', 'is_primary']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

CarImageFormSet = forms.modelformset_factory(CarImage, form=CarImageForm, extra=3, can_delete=True)

class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ['name', 'phone', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Phone'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Your Message'}),
        }

class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Current Password'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'}), label='New Password')
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'}), label='Confirm Password')

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('new_password1') != cleaned_data.get('new_password2'):
            raise forms.ValidationError("Passwords don't match")
        return cleaned_data

class SearchForm(forms.Form):
    brand = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Brand', 'class': 'form-control'}))
    model = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Model', 'class': 'form-control'}))
    year = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'placeholder': 'Year', 'class': 'form-control'}))
    color = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Color', 'class': 'form-control'}))
    city = forms.ModelChoiceField(queryset=City.objects.all(), required=False, empty_label='City', widget=forms.Select(attrs={'class': 'form-select', 'aria-label': 'City'}))
    min_price = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'placeholder': 'Min Price', 'class': 'form-control'}))
    max_price = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'placeholder': 'Max Price', 'class': 'form-control'}))
    fuel_type = forms.ChoiceField(choices=[('', 'Fuel Type')] + Car.FUEL_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select', 'aria-label': 'Fuel type'}))
    transmission = forms.ChoiceField(choices=[('', 'Transmission')] + Car.TRANSMISSION_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select', 'aria-label': 'Transmission'}))

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}))
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Phone'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Your Message'}))
