from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from captcha.fields import ReCaptchaField

from models import Experiment, Frequency, Keyword, Model, Variable, Project, Funding, Author, Publication, Book, Conference, Journal, Magazine, Poster, Presentation, TechnicalReport, Other, JournalOptions
# from captcha.fields import ReCaptchaField
import pdb

# If you don't do this you cannot use Bootstrap CSS
class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=30,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'username'}))
    password = forms.CharField(label="Password", max_length=30,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'password'}))


class RegisterForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-Mail'}),
                             required=True)
    captcha = ReCaptchaField(attrs={'theme': 'clean'})
    password1 = forms.CharField(label="Password",
                                widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    password2 = forms.CharField(label="Confirm Password",
                                widget=forms.PasswordInput(
                                    attrs={'class': 'form-control', 'placeholder': 'Verify Password'}))

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'User Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-Mail'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
        }


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control typeahead-a author-name'}),
            'institution': forms.TextInput(attrs={'class': 'form-control author-inst'}),
        }

AuthorFormSetBase = forms.modelformset_factory(Author, fields=["name", "institution"], form=AuthorForm, can_delete=True, extra=1)

class AuthorFormSet(AuthorFormSetBase):
    pass


class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ['status', 'doi', 'title', 'url', 'project_number', 'task_number', 'publication_date', 'abstract']
        widgets = {
            'doi': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'url': forms.TextInput(attrs={'class': 'form-control'}),
            # 'status': forms.TextInput(attrs={'class': 'form-control'}),
            'project_number': forms.TextInput(attrs={'class': 'form-control'}),
            'task_number': forms.TextInput(attrs={'class': 'form-control'}),
            'publication_date': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "mm/dd/yyyy"}),
            'abstract': forms.TextInput(attrs={'class': 'form-control'}),
        }


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'
        exclude = ['publication_id']
        widgets = {
            'book_name': forms.TextInput(attrs={'class': 'form-control'}),
            'chapter_title': forms.TextInput(attrs={'class': 'form-control'}),
            'start_page': forms.TextInput(attrs={'class': 'form-control'}),
            'end_page': forms.TextInput(attrs={'class': 'form-control'}),
            'editor': forms.TextInput(attrs={'class': 'form-control'}),
            'city_of_publication': forms.TextInput(attrs={'class': 'form-control'}),
            'publisher': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ConferenceForm(forms.ModelForm):
    class Meta:
        model = Conference
        fields = '__all__'
        exclude = ['publication_id']
        widgets = {
            'conference_name': forms.TextInput(attrs={'class': 'form-control'}),
            'conference_serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'event_location': forms.TextInput(attrs={'class': 'form-control'}),
            'start_page': forms.TextInput(attrs={'class': 'form-control'}),
            'end_page': forms.TextInput(attrs={'class': 'form-control'}),
            'editor': forms.TextInput(attrs={'class': 'form-control'}),
            'city_of_publication': forms.TextInput(attrs={'class': 'form-control'}),
            'publisher': forms.TextInput(attrs={'class': 'form-control'}),
        }


class JournalForm(forms.ModelForm):
    class Meta:
        model = Journal
        fields = '__all__'
        exclude = ['publication_id']
        widgets = {
            'journal_name': forms.TextInput(attrs={'class': 'form-control'}),
            'editor': forms.TextInput(attrs={'class': 'form-control'}),
            'volume_number': forms.TextInput(attrs={'class': 'form-control'}),
            'article_number': forms.TextInput(attrs={'class': 'form-control'}),
            'start_page': forms.TextInput(attrs={'class': 'form-control'}),
            'end_page': forms.TextInput(attrs={'class': 'form-control'}),
        }


class MagazineForm(forms.ModelForm):
    class Meta:
        model = Magazine
        fields = '__all__'
        exclude = ['publication_id']
        widgets = {
            'magazine_name': forms.TextInput(attrs={'class': 'form-control'}),
            'editor': forms.TextInput(attrs={'class': 'form-control'}),
            'volume_number': forms.TextInput(attrs={'class': 'form-control'}),
            'article_number': forms.TextInput(attrs={'class': 'form-control'}),
            'start_page': forms.TextInput(attrs={'class': 'form-control'}),
            'end_page': forms.TextInput(attrs={'class': 'form-control'}),
        }


class PosterForm(forms.ModelForm):
    class Meta:
        model = Poster
        fields = '__all__'
        exclude = ['publication_id']
        widgets = {
            'poster_title': forms.TextInput(attrs={'class': 'form-control'}),
            'event': forms.TextInput(attrs={'class': 'form-control'}),
        }


class PresentationForm(forms.ModelForm):
    class Meta:
        model = Presentation
        fields = '__all__'
        exclude = ['publication_id']
        widgets = {
            'presentation_title': forms.TextInput(attrs={'class': 'form-control'}),
            'event': forms.TextInput(attrs={'class': 'form-control'}),
        }


class TechnicalReportForm(forms.ModelForm):
    class Meta:
        model = TechnicalReport
        fields = '__all__'
        exclude = ['publication_id']
        widgets = {
            'report_number': forms.TextInput(attrs={'class': 'form-control'}),
            'editor': forms.TextInput(attrs={'class': 'form-control'}),
            'issuer': forms.TextInput(attrs={'class': 'form-control'}),
        }


class OtherForm(forms.ModelForm):
    class Meta:
        model = Other
        fields = '__all__'
        exclude = ['publication_id']
        widgets = {
            'other_pub': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ExperimentForm(forms.ModelForm):
    experiment = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=Experiment.objects.all())
    # The ensemble inputs are located in the doi.js file. Getting the same behavior with django is a ton more work.

    def __init__(self, *args, **kwargs):
        queryset = kwargs.pop('queryset', None)
        super(ExperimentForm, self).__init__(*args, **kwargs)
        self.fields['experiment'].queryset = queryset

    class Meta:
        model = Experiment
        fields = '__all__'
        exclude = ['experiment']


class FrequencyForm(forms.ModelForm):
    frequency = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=Frequency.objects.all())

    def __init__(self, *args, **kwargs):
        queryset = kwargs.pop('queryset', None)
        super(FrequencyForm, self).__init__(*args, **kwargs)
        self.fields['frequency'].queryset = queryset

    class Meta:
        model = Frequency
        fields = '__all__'
        exclude = ['frequency']


class KeywordForm(forms.ModelForm):

    keyword = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=Keyword.objects.all())

    def __init__(self, *args, **kwargs):
        queryset = kwargs.pop('queryset', None)
        super(KeywordForm, self).__init__(*args, **kwargs)
        self.fields['keyword'].queryset = queryset

    class Meta:
        model = Keyword
        fields = '__all__'
        exclude = ['keyword']


class ModelForm(forms.ModelForm):
    model = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=Model.objects.all())

    def __init__(self, *args, **kwargs):
        queryset = kwargs.pop('queryset', None)
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['model'].queryset = queryset

    class Meta:
        model = Model
        fields = '__all__'
        exclude = ['model']


class VariableForm(forms.ModelForm):
    variable = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=Variable.objects.all())

    def __init__(self, *args, **kwargs):
        queryset = kwargs.pop('queryset', None)
        super(VariableForm, self).__init__(*args, **kwargs)
        self.fields['variable'].queryset = queryset

    class Meta:
        model = Variable
        fields = '__all__'
        exclude = ['variable']


