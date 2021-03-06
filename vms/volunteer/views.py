# standard library
import os

# third party
from braces.views import LoginRequiredMixin

# Django
from django.conf import settings
# from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from wsgiref.util  import FileWrapper
from django.urls import reverse, reverse_lazy
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic import ListView, View
from django.views.generic.edit import FormView, UpdateView
from django.utils.decorators import method_decorator

# local Django
from administrator.utils import admin_required
from event.services import get_signed_up_events_for_volunteer
from job.services import get_signed_up_jobs_for_volunteer
from organization.services import get_organization_by_id, get_organizations_ordered_by_name
from shift.services import get_volunteer_report, calculate_total_report_hours
from volunteer.forms import ReportForm, SearchVolunteerForm, VolunteerForm
from volunteer.models import Volunteer
from volunteer.services import (delete_volunteer_resume, search_volunteers,
                                get_volunteer_resume_file_url, has_resume_file,
                                get_volunteer_by_id)
from volunteer.validation import validate_file
from volunteer.utils import vol_id_check
from vms.utils import check_correct_volunteer


@login_required
def download_resume(request, volunteer_id):
    user = request.user
    if int(user.volunteer.id) == int(volunteer_id):
        if request.method == 'POST':
            basename = get_volunteer_resume_file_url(volunteer_id)
            if basename:
                filename = settings.MEDIA_ROOT + basename
                print(settings.MEDIA_ROOT)
                print(basename)
                print(filename)
               # wrapper = FileWrapper(filename)
                response = HttpResponse(content_type='application/force-download')
                response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filename)
                response['Content-Length'] = os.path.getsize(filename)
                return response
            else:
                raise Http404
    else:
        return HttpResponse(status=403)


@login_required
def delete_resume(request, volunteer_id):
    user = request.user
    if int(user.volunteer.id) == int(volunteer_id):
        if request.method == 'POST':
            try:
                delete_volunteer_resume(volunteer_id)
                return HttpResponseRedirect(
                    reverse('volunteer:profile', args=(volunteer_id, )))
            except:
                raise Http404
    else:
        return HttpResponse(status=403)


'''
 The View to edit Volunteer Profile
'''


class VolunteerUpdateView(LoginRequiredMixin, UpdateView, FormView):
    @method_decorator(check_correct_volunteer)
    def dispatch(self, *args, **kwargs):
        return super(VolunteerUpdateView, self).dispatch(*args, **kwargs)

    form_class = VolunteerForm
    template_name = 'volunteer/edit.html'
    success_url = reverse_lazy('volunteer:profile')

    def get_context_data(self, **kwargs):
        context = super(VolunteerUpdateView,self).get_context_data(**kwargs)
        organization_list = get_organizations_ordered_by_name()
        context['organization_list'] = organization_list
        return context

    def get_object(self, queryset=None):
        volunteer_id = self.kwargs['volunteer_id']
        obj = Volunteer.objects.get(pk=volunteer_id)
        return obj

    def form_valid(self, form):
        volunteer_id = self.kwargs['volunteer_id']
        volunteer = get_volunteer_by_id(volunteer_id)
        organization_list = get_organizations_ordered_by_name()
        if 'resume_file' in self.request.FILES:
            my_file = form.cleaned_data['resume_file']
            if validate_file(my_file):
                # delete an old uploaded resume if it exists
                has_file = has_resume_file(volunteer_id)
                if has_file:
                    try:
                        delete_volunteer_resume(volunteer_id)
                    except:
                        raise Http404
            else:
                return render(
                    self.request, 'volunteer/edit.html', {
                        'form': form,
                        'organization_list': organization_list,
                        'volunteer': volunteer,
                        'resume_invalid': True,
                    })

        volunteer_to_edit = form.save(commit=False)

        organization_id = self.request.POST.get('organization_name')
        organization = get_organization_by_id(organization_id)
        if organization:
            volunteer_to_edit.organization = organization
        else:
            volunteer_to_edit.organization = None

        # update the volunteer
        volunteer_to_edit.save()
        return HttpResponseRedirect(
            reverse('volunteer:profile', args=(volunteer_id, )))


'''
  The view to display Volunteer profile.
  It uses DetailView which is a generic class-based views are designed to display data.
'''


class ProfileView(LoginRequiredMixin, DetailView):
    template_name = 'volunteer/profile.html'

    @method_decorator(check_correct_volunteer)
    @method_decorator(vol_id_check)
    def dispatch(self, *args, **kwargs):
        return super(ProfileView, self).dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        volunteer_id = self.kwargs['volunteer_id']
        obj = Volunteer.objects.get(id=self.kwargs['volunteer_id'])
        return obj


'''
  The view generates Report.
  GenerateReportView calls two other views(ShowFormView, ShowReportListView) within it.
'''


class GenerateReportView(LoginRequiredMixin, View):
    @method_decorator(check_correct_volunteer)
    @method_decorator(vol_id_check)
    def dispatch(self, *args, **kwargs):
        return super(GenerateReportView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        view = ShowFormView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = ShowReportListView.as_view()
        return view(request, *args, **kwargs)


class ShowFormView(LoginRequiredMixin, FormView):
    """
    Displays the form
    """
    model = Volunteer
    form_class = ReportForm
    template_name = "volunteer/report.html"

    def get(self, request, *args, **kwargs):
        volunteer_id = self.kwargs['volunteer_id']
        event_list = get_signed_up_events_for_volunteer(volunteer_id)
        job_list = get_signed_up_jobs_for_volunteer(volunteer_id)

        return render(request, 'volunteer/report.html', {
            'event_list': event_list,
            'job_list':job_list,
        })


class ShowReportListView(LoginRequiredMixin, ListView):
    """
    Generate the report using ListView
    """
    template_name = "volunteer/report.html"

    def post(self, request, *args, **kwargs):
        volunteer_id = self.kwargs['volunteer_id']
        event_list = get_signed_up_events_for_volunteer(volunteer_id)
        job_list = get_signed_up_jobs_for_volunteer(volunteer_id)
        event_name = self.request.POST['event_name']
        job_name = self.request.POST['job_name']
        start_date = self.request.POST['start_date']
        end_date = self.request.POST['end_date']
        report_list = get_volunteer_report(volunteer_id, event_name, job_name,
                                           start_date, end_date)
        total_hours = calculate_total_report_hours(report_list)
        return render(
            request, 'volunteer/report.html', {
                'report_list': report_list,
                'total_hours': total_hours,
                'notification': True,
                'job_list': job_list,
                'event_list': event_list,
                'selected_event': event_name,
                'selected_job': job_name
            })


@login_required
@admin_required
def search(request):
    organizations_list = []
    if request.method == 'POST':
        form = SearchVolunteerForm(request.POST)
        if form.is_valid():

            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            country = form.cleaned_data['country']
            organization = form.cleaned_data['organization']
            organizations_list = get_organizations_ordered_by_name()

            search_result_list = search_volunteers(
                first_name, last_name, city, state, country, organization)
            return render(
                request, 'volunteer/search.html', {
                    'organizations_list': organizations_list,
                    'form': form,
                    'has_searched': True,
                    'search_result_list': search_result_list
                })
    else:
        organizations_list = get_organizations_ordered_by_name()
        form = SearchVolunteerForm()

    return render(
        request, 'volunteer/search.html', {
            'organizations_list': organizations_list,
            'form': form,
            'has_searched': False
        })
