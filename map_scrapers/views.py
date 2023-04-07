# Create your views here.
import csv

import requests
from decouple import config
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView

from map_scrapers.forms import HistoryUpdateForm
from map_scrapers.models import History
from map_scrapers.permissions import StaffAndLoginRequiredMixin
from map_scrapers.utils import export_user_csv, query_items, export_all_csv, read_search_csv
from map_scrapers.tasks import get_all_place, proxies, api_key


def search_api(request):
    print("access here")
    query = request.GET.get('query')
    category = request.GET.get('category')

    get_all_place.delay(query, category, request.user.id)
    # Get the single place
    return JsonResponse({"status": "ok"})


def place_detail(request):
    print("access detail")
    query = request.GET.get('query')
    # Get the single place
    url = f'https://maps.googleapis.com/maps/api/place/textsearch/json?key={api_key}&query={query}'
    response = requests.get(url, proxies=proxies)

    return JsonResponse(response.json())


def autocomplete_api(request):
    print("access here")
    query = request.GET.get('query')
    country_codes = request.GET.getlist('country_code')  # Use getlist to get an array of values

    # Replace YOUR_API_KEY with your actual API key and YOUR_PROXY_URL with your proxy URL
    api_key = config("GOOGLE_MAP_API_KEY")

    # Build the request URL with the appropriate parameters
    #
    url = f'https://maps.googleapis.com/maps/api/place/autocomplete/json?key={api_key}&input={query}&types=(regions)'
    if country_codes:  # If country codes were provided, join them with a pipe to create the components parameter
        components = 'country:' + '|'.join(country_codes)
        url += f'&components={components}'
    # Make the request using the proxy dictionary
    response = requests.get(url, proxies=proxies)
    # Return the response as a JSON object
    return JsonResponse(response.json())


@login_required
def map_view(request):
    # Replace YOUR_API_KEY with your actual Google Maps API key
    api_key = config("GOOGLE_MAP_API_KEY")
    context = {'api_key': api_key}
    return render(request, 'map.html', context)


class HistoryListView(LoginRequiredMixin, ListView):
    queryset = History.objects.all()
    template_name = "history.html"
    paginate_by = 50

    def get_queryset(self):
        """
        Return the list of items for this view.

        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.
        """
        query = self.request.GET.get('search')

        queryset = self.queryset.filter(user=self.request.user)
        ordering = self.get_ordering()
        if query:
            queryset = query_items(item=queryset, query=query)
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Overiding context data
        :param kwargs:
        :return:
        """
        context = super().get_context_data(**kwargs)
        context['item_form'] = HistoryUpdateForm()
        return context


class AdminHistoryListView(StaffAndLoginRequiredMixin, ListView):
    queryset = History.objects.all()
    template_name = "history.html"
    paginate_by = 20

    def get_queryset(self):
        """
        Return the list of items for this view.

        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.
        """
        query = self.request.GET.get('search')

        queryset = self.queryset.filter()
        ordering = self.get_ordering()
        if query:
            queryset = query_items(item=queryset, query=query)
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Overiding context data
        :param kwargs:
        :return:
        """
        context = super().get_context_data(**kwargs)
        context['item_form'] = HistoryUpdateForm()
        return context


class HistoryUpdateView(LoginRequiredMixin, View):
    """
    this is used to update the history
    """

    def post(self, request):
        item_id = self.request.POST.get("id_history")
        if not item_id:
            return redirect("history_list")
        history = History.objects.filter(id=item_id).first()
        if not history:
            return redirect("history_list")
        form = HistoryUpdateForm(self.request.POST, instance=history)
        if form.is_valid():
            form.save()
        return redirect("history_list")


class HistoryDeleteView(LoginRequiredMixin, View):
    """
    this is used to delete a History
    """

    def post(self, request):
        item_id = request.POST.get("history_id")
        if item_id:
            history = History.objects.filter(user=self.request.user, id=item_id).first()
            if history:
                history.delete()
        return redirect("history_list")


class DownloadUserCSVView(LoginRequiredMixin, View):
    """
    This is used to export the product to csv and return it to the frontend
    """

    def get(self, request):
        # The get request
        csv = export_user_csv(user=self.request.user)
        return csv


class DownloadAllCSVView(LoginRequiredMixin, View):
    """
    This is used to export the product to csv and return it to the frontend
    """

    def get(self, request):
        # The get request
        if self.request.user.is_staff or self.request.user.is_superuser:
            csv = export_all_csv()
        else:
            csv = export_user_csv(user=self.request.user)
        return csv


class SearchWithCSV(LoginRequiredMixin, View):
    """
    Search all data with csv
    """

    def get(self, request):
        return render(request, "search.html")

    def post(self, request):
        csv = request.FILES.get("csv")
        if not csv:
            return redirect("search_with_csv")
        read_search_csv(csv, self.request.user.id)
        messages.info(request, "Searching params ..")
        return redirect("search_with_csv")


@login_required
def get_csv_sample(request):
    """
    this is a csv example

    :param request:
    :return:
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="History.csv"'
    writer = csv.writer(response)
    writer.writerow(
        ["query", 'category'])
    writer.writerow([
        "Lagos Nigeria", "hotel, lodging, banks"
    ])
    return response
