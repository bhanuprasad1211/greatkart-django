from django import forms
from .models import Accounts,UserProfile
class RegistrationForm(forms.ModelForm) :
    password=forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Enter password'
    }))
    conform_password=forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Conform Password'
    }))
    class Meta :
        model = Accounts
        fields=['first_name','last_name','phone_number','email','password']
    def __init__(self,*args,**kwargs) :
        super(RegistrationForm,self).__init__(*args,**kwargs)
        self.fields['first_name'].widget.attrs['placeholder']='Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder']='Enter Last Name'
        self.fields['phone_number'].widget.attrs['placeholder']='Enter Phone Number'
        self.fields['email'].widget.attrs['placeholder']='Enter Email Address'
        for field in self.fields :
            self.fields[field].widget.attrs['class']='form-control'
            #self.fields[field].widget.attrs['placeholder']=f'Enter {' '.join(field.split('_'))}'
    def clean(self):
        cleaned_data=super(RegistrationForm,self).clean()
        password=cleaned_data.get('password')
        conform_password=cleaned_data.get('conform_password')
        if password!=conform_password :
            raise forms.ValidationError(
                'passwords not matched!'
            )
        
class UserForm(forms.ModelForm) :
    class Meta :
        model=Accounts
        fields=('first_name','last_name','phone_number')
    def __init__(self,*args,**kwargs) :
        super(UserForm,self).__init__(*args,**kwargs)
        for field in self.fields :
            self.fields[field].widget.attrs['class']='form-control'
class UserProfileForm(forms.ModelForm) :
    
    profile_picture=forms.ImageField(required=False,error_messages={'invalid':("Image fields only")},widget=forms.FileInput)#to remove current profile picture heading in edit profile section
    class Meta :
        model=UserProfile
        fields=('address_line_1','address_line_2','city','state','country','profile_picture')
    def __init__(self,*args,**kwargs) :
        super(UserProfileForm,self).__init__(*args,**kwargs)
        for field in self.fields :
            self.fields[field].widget.attrs['class']='form-control'