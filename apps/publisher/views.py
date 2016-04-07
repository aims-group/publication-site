from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader, Context
from django.contrib.auth.decorators import login_required

@login_required()
def index(request):
    return render(request, 'site/search.html')

# def register(request):
#     # Register new user
#     def register(request):
#         context = RequestContext(request)
#         registered = False
#         if request.method == 'POST':
#             form = RegisterForm(data=request.POST)
#             if form.is_valid():
#                 user = form.save()
#                 try:
#                     group = Group.objects.get(name="Default")
#                     user.groups.add(group)
#                 except Group.DoesNotExist:
#                     # Don't do anything, no default set up
#                     pass
#
#                 user.save()
#                 registered = True
#                 user = authenticate(
#                     username=request.POST['username'], password=request.POST['password'])
#                 if user:
#                     login(request, user)
#                     messages.success(
#                         request, 'User: ' + request.POST['username'] + ' successfully created an account and logged in')
#             else:
#                 print form.errors
#         else:
#             site = get_current_site(request)
#             form = RegisterForm()
#             context = {
#                 'form': form,
#                 'site': site,
#                 'site_name':,
#             }