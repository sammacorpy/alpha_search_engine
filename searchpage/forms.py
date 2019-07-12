from django import forms
from datetime import datetime 

class todoform(forms.Form):
    query=forms.CharField(max_length=10000,widget=forms.TextInput(attrs={'placeholder':"Enter task title"}))