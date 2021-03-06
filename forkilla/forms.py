from django import forms

from .models import Reservation, Review

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ["day", "time_slot", "num_people"]

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["text", "rating"]
"""
class ComparatorForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["price_average", "city", "category"]
"""


