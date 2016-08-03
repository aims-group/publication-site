from django import forms
from django.contrib.auth.forms import AuthenticationForm
from registration.forms import RegistrationFormUniqueEmail
from registration.backends.simple.views import RegistrationView
from django.contrib.auth.models import User
from captcha.fields import ReCaptchaField
from django.core.exceptions import ValidationError

from models import Experiment, Frequency, Keyword, Model, Variable, Project, Funding, Author, Publication, Book, Conference, Journal, Magazine, Poster, Presentation, TechnicalReport, Other, JournalOptions
# from captcha.fields import ReCaptchaField


# If you don't do this you cannot use Bootstrap CSS
class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=30,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'username'}))
    password = forms.CharField(label="Password", max_length=30,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'passwrd', 'autocomplete': 'off'}))


class RegistrationForm(RegistrationFormUniqueEmail):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-Mail'}),
                             required=True)
    captcha = ReCaptchaField(attrs={'theme': 'clean'})
    password1 = forms.CharField(label="Password",
                                widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password', 'autocomplete': 'off'}))
    password2 = forms.CharField(label="Confirm Password",
                                widget=forms.PasswordInput(
                                    attrs={'class': 'form-control', 'placeholder': 'Verify Password', 'autocomplete': 'off'}))

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'User Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-Mail'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
        }


class RegistrationViewUniqueEmail(RegistrationView):
    form_class = RegistrationForm


class AuthorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AuthorForm, self).__init__(*args, **kwargs)
        self.fields['institution'].required = False

    class Meta:
        model = Author
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control typeahead-a author-name'}),
            'institution': forms.TextInput(attrs={'class': 'form-control author-inst'}),
        }

AuthorFormSetBase = forms.modelformset_factory(Author, fields=["name", "institution"], form=AuthorForm, can_delete=True, extra=0, min_num=1, validate_min=True)


class AuthorFormSet(AuthorFormSetBase):
    pass


class PublicationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        try:
            self.pub_id = int(kwargs.pop('pub_id', 0))
        except Exception as e:
            print e
            self.pub_id = 0
        super(PublicationForm, self).__init__(*args, **kwargs)
        self.fields['doi'].required = True
        self.fields['url'].required = False
        self.fields['project_number'].required = False
        self.fields['task_number'].required = False
        self.fields['abstract'].required = False

    def clean_doi(self):
        doi = self.cleaned_data['doi'].lower()  # Lowercase all input
        if doi.startswith('doi:'):
            doi = doi[4:].strip()  # Remove user entered prefix we don't want and excess whitespace
        else:
            doi = doi.strip()  # If there isn't a prefix, just remove whitespace
        pub = Publication.objects.filter(doi__icontains=doi)  # do a case insensitive search for a matching DOI. Use contains since some have 'doi: 10.'
        if pub.exists() and pub.first().id != int(self.pub_id):  # Check that the doi is new, or that we are editing
            raise ValidationError("Doi already exists")
        return doi

    def clean_title(self):
        title = self.cleaned_data['title']
        pub = Publication.objects.filter(title__iexact=title)  # do a case insensitive search for a matching DOI
        if pub.exists() and pub.first().id != int(self.pub_id):  # Check that the doi is new, or that we are editing
            raise ValidationError("Title already exists")
        return title

    def clean(self):
        data = super(PublicationForm, self).clean()
        if data.get('status') != 0 and 'doi' in self.errors:  # Only require a doi for published articles
            del self.errors['doi']
        return data

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

    def __init__(self, *args, **kwargs):
        super(BookForm, self).__init__(*args, **kwargs)
        self.fields['book_name'].required = True
        self.fields['chapter_title'].required = False
        self.fields['start_page'].required = False
        self.fields['end_page'].required = False
        self.fields['editor'].required = False
        self.fields['city_of_publication'].required = False
        self.fields['publisher'].required = False

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

    def __init__(self, *args, **kwargs):
        super(ConferenceForm, self).__init__(*args, **kwargs)
        self.fields['conference_name'].required = True
        self.fields['conference_serial_number'].required = False
        self.fields['event_location'].required = False
        self.fields['start_page'].required = False
        self.fields['end_page'].required = False
        self.fields['editor'].required = False
        self.fields['city_of_publication'].required = False
        self.fields['publisher'].required = False

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
    journal_name = forms.ModelChoiceField(queryset=JournalOptions.objects.all(), empty_label="N/A", widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(JournalForm, self).__init__(*args, **kwargs)
        pass

    class Meta:
        model = Journal
        fields = '__all__'
        exclude = ['publication_id']
        widgets = {
            'volume_number': forms.TextInput(attrs={'class': 'form-control'}),
            'article_number': forms.TextInput(attrs={'class': 'form-control'}),
            'start_page': forms.TextInput(attrs={'class': 'form-control'}),
            'end_page': forms.TextInput(attrs={'class': 'form-control'}),
        }


class MagazineForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(MagazineForm, self).__init__(*args, **kwargs)
        self.fields['editor'].required = False
        self.fields['volume_number'].required = False
        self.fields['article_number'].required = False
        self.fields['start_page'].required = False
        self.fields['end_page'].required = False

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
    experiment = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=Experiment.objects.all(), required=False)
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
    frequency = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=Frequency.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        queryset = kwargs.pop('queryset', None)
        super(FrequencyForm, self).__init__(*args, **kwargs)
        self.fields['frequency'].queryset = queryset

    class Meta:
        model = Frequency
        fields = '__all__'
        exclude = ['frequency']


class KeywordForm(forms.ModelForm):

    keyword = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=Keyword.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        queryset = kwargs.pop('queryset', None)
        super(KeywordForm, self).__init__(*args, **kwargs)
        self.fields['keyword'].queryset = queryset

    class Meta:
        model = Keyword
        fields = '__all__'
        exclude = ['keyword']


class ModelForm(forms.ModelForm):
    model = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=Model.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        queryset = kwargs.pop('queryset', None)
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['model'].queryset = queryset

    class Meta:
        model = Model
        fields = '__all__'
        exclude = ['model']


class VariableForm(forms.ModelForm):
    variable = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=Variable.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        queryset = kwargs.pop('queryset', None)
        super(VariableForm, self).__init__(*args, **kwargs)
        self.fields['variable'].queryset = queryset

    class Meta:
        model = Variable
        fields = '__all__'
        exclude = ['variable']
