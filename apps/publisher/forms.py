from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
# from captcha.fields import ReCaptchaField
from django import forms


# If you don't do this you cannot use Bootstrap CSS
class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=30,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'username'}))
    password = forms.CharField(label="Password", max_length=30,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'password'}))


class RegisterForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-Mail'}),
                             required=True)
    # captcha = ReCaptchaField(attrs={'theme': 'blackglass'})
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


class PublicationForm(forms.Form):
    doi = forms.CharField(label="Doi", widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'DOI'}))
    isbn = forms.CharField(label="Isbn", widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'isbn'}))
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'title'}))
    url = forms.CharField(label="Url", widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'URL'}))
    page = forms.CharField(label="Page", widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'page'}))
    publisher = forms.CharField(label="Publisher", widget=forms.TextInput(attrs={'class': 'form-control',
                                                                                 'name': 'publisher'}))
    # status = models.IntegerField(choices=PUBLICATION_STATUS_CHOICE, default=0)
    # authors = models.ManyToManyField(Author)
    # publication_date = models.DateField()
    # url = models.URLField()
    # doi = models.TextField()

    # example data object:
    # u'DOI': u'10.1002/0470841559.ch1',
    # u'ISBN': [u'http://id.crossref.org/isbn/0471975141',
    #           u'http://id.crossref.org/isbn/0470841559'],
    # u'URL': u'http://dx.doi.org/10.1002/0470841559.ch1',
    # u'container-title': u'Internetworking LANs and WANs',
    # u'created': {u'date-parts': [[2003, 4, 2]],
    #              u'date-time': u'2003-04-02T18:18:49Z',
    #              u'timestamp': 1049307529000},
    # u'deposited': {u'date-parts': [[2013, 12, 16]],
    #                u'date-time': u'2013-12-16T23:08:32Z',
    #                u'timestamp': 1387235312000},
    # u'indexed': {u'date-parts': [[2015, 12, 24]],
    #              u'date-time': u'2015-12-24T19:52:16Z',
    #              u'timestamp': 1450986736947},
    # u'issued': {u'date-parts': [[None]]},
    # u'member': u'http://id.crossref.org/member/311',
    # u'page': u'1-30',
    # u'prefix': u'http://id.crossref.org/prefix/10.1002',
    # u'publisher': u'Wiley-Blackwell',
    # u'reference-count': 0,
    # u'score': 1.0,
    # u'source': u'CrossRef',
    # u'subtitle': [],
    # u'title': u'Network Concepts',
    # u'type': u'book-chapter'}
