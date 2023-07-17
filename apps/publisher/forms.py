from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django_registration.forms import RegistrationFormUniqueEmail
from django_registration.backends.one_step.views import RegistrationView
from django.contrib.auth.models import User
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django.core.exceptions import ValidationError
from django.db.models.functions import Lower

from .models import Activity, Experiment, Frequency, Keyword, Model, Realm, Variable, Project, Funding, Author, Publication, Book, Conference, Journal, Magazine, Poster, Presentation, TechnicalReport, Other, JournalOptions
# from captcha.fields import ReCaptchaField

# Advanced Search form helper functions. 
# Django will try to execute these statements before migrations are run, unless they are wrapped in a function like below
# Projects are not listed here because it is a modelmultiplechoice field
def get_asf_activities():
    return [(x,x) for x in Activity.objects.all().order_by(Lower("activity")).values_list('activity', flat=True).distinct()]

def get_asf_experiments():
    return [(x,x) for x in Experiment.objects.all().order_by(Lower("experiment")).values_list('experiment', flat=True).distinct()]

def get_asf_frequencies():
    return [(x,x) for x in Frequency.objects.all().order_by(Lower("frequency")).values_list('frequency', flat=True).distinct()]

def get_asf_keywords():
    return [(x,x) for x in Keyword.objects.all().order_by(Lower("keyword")).values_list("keyword", flat=True).distinct()]

def get_asf_models():
    return [(x,x) for x in Model.objects.all().order_by(Lower("model")).values_list("model", flat=True).distinct()]

def get_asf_realms():
    return [(x,x) for x in Realm.objects.all().order_by(Lower("realm")).values_list("realm", flat=True).distinct()]
    
def get_asf_variables():
    return [(x,x) for x in Variable.objects.all().order_by(Lower("variable")).values_list("variable", flat=True).distinct()]

# If you don't do this you cannot use Bootstrap CSS
class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=30,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'username'}))
    password = forms.CharField(label="Password", max_length=30,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'passwrd', 'autocomplete': 'off'}))


class RegistrationForm(RegistrationFormUniqueEmail):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-Mail'}),
                             required=True)
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox(attrs={'data-theme': 'light'}))
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
            print(e)
            self.pub_id = 0
        super(PublicationForm, self).__init__(*args, **kwargs)
        self.fields['doi'].required = False
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
    journal_name = forms.ModelChoiceField(queryset=JournalOptions.objects.all().order_by('journal_name'), empty_label="N/A", widget=forms.Select(attrs={'class': 'form-control'}))

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
        if queryset:
            self.fields['experiment'].queryset = queryset.order_by(Lower('experiment'))
        else:
            self.fields['experiment'].queryset = queryset

    class Meta:
        model = Experiment
        fields = '__all__'
        exclude = ['experiment']


class ActivityForm(forms.ModelForm):
    activity = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=Activity.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        queryset = kwargs.pop('queryset', None)
        super(ActivityForm, self).__init__(*args, **kwargs)
        if queryset:
            self.fields['activity'].queryset = queryset.order_by(Lower('activity'))
        else:
            self.fields['activity'].queryset = queryset

    class Meta:
        model = Activity
        fields = '__all__'
        exclude = ['activity']


class FrequencyForm(forms.ModelForm):
    frequency = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=Frequency.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        queryset = kwargs.pop('queryset', None)
        super(FrequencyForm, self).__init__(*args, **kwargs)
        if queryset:
            self.fields['frequency'].queryset = queryset.order_by(Lower('frequency'))
        else:
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
        if queryset:
            self.fields['keyword'].queryset = queryset.order_by(Lower('keyword'))
        else:
            self.fields['keyword'].queryset = queryset

    class Meta:
        model = Keyword
        fields = '__all__'
        exclude = ['keyword']


class ModelForm(forms.ModelForm):
    model = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=Model.objects.all(), required=False, label='Source')

    def __init__(self, *args, **kwargs):
        queryset = kwargs.pop('queryset', None)
        super(ModelForm, self).__init__(*args, **kwargs)
        if queryset:
            self.fields['model'].queryset = queryset.order_by(Lower('model'))
        else:
            self.fields['model'].queryset = queryset

    class Meta:
        model = Model
        fields = '__all__'
        exclude = ['model']


class RealmForm(forms.ModelForm):
    realm = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=Realm.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        queryset = kwargs.pop('queryset', None)
        super(RealmForm, self).__init__(*args, **kwargs)
        if queryset:
            self.fields['realm'].queryset = queryset.order_by(Lower('realm'))
        else:
            self.fields['realm'].queryset = queryset

    class Meta:
        model = Realm
        fields = '__all__'
        exclude = ['realm']


class VariableForm(forms.ModelForm):
    variable = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=Variable.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        queryset = kwargs.pop('queryset', None)
        super(VariableForm, self).__init__(*args, **kwargs)
        if queryset:
            self.fields['variable'].queryset = queryset.order_by(Lower('variable'))
        else:
            self.fields['variable'].queryset = queryset

    class Meta:
        model = Variable
        fields = '__all__'
        exclude = ['variable']

class AdvancedSearchForm(forms.Form):
    doi = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control search-input'}), required=False)
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control search-input'}), required=False)
    author = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control search-input'}), required=False)
    date_start = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control search-input'}), required=False)
    date_end = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control search-input'}), required=False)

    #Queryset and choices are populated by helper function at the top of this file
    project = forms.ModelMultipleChoiceField(
        queryset=Project.objects.all().order_by(Lower("project")),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'search-input'}), required=False)
    activity = forms.MultipleChoiceField(
        choices=get_asf_activities,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'search-input'}), required=False)
    experiment = forms.MultipleChoiceField(
        choices=get_asf_experiments,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'search-input'}), required=False)
    frequency = forms.MultipleChoiceField(
        choices=get_asf_frequencies,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'search-input'}), required=False)
    keyword = forms.MultipleChoiceField(
        choices=get_asf_keywords,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'search-input'}), required=False)
    model = forms.MultipleChoiceField(
        choices=get_asf_models,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'search-input'}), required=False)
    realm = forms.MultipleChoiceField(
        choices=get_asf_realms,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'search-input'}), required=False)
    variable= forms.MultipleChoiceField(
        choices=get_asf_variables,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'search-input'}), required=False)

class DoiBatchForm(forms.Form):
    dois = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows':20}))