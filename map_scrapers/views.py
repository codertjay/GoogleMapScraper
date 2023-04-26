# Create your views here.
import base64
import csv

import requests
from decouple import config
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView

from map_scrapers.forms import HistoryUpdateForm
from map_scrapers.models import History, SearchInfo
from map_scrapers.tasks import get_all_place, proxies, api_key
from map_scrapers.utils import export_user_csv, query_items, export_all_csv, export_search_info_user_csv, \
    get_social_percent


class SearchDashboardView(LoginRequiredMixin, View):
    """
    this is used to get the search dashboard
    """

    def get(self, request):
        context = {
            "total_searches": SearchInfo.objects.filter(user=self.request.user).count(),
            "search_infos": SearchInfo.objects.filter(user=self.request.user)[:5],
            "total_emails": History.objects.filter(user=self.request.user, email__contains="@").count(),
            "all_twitter_count": get_social_percent(user=self.request.user, social="www.twitter.com"),
            "all_linkedin_count": get_social_percent(self.request.user,
                                                     "www.LinkedIn.com"),
            "all_youtube_count": get_social_percent(self.request.user,
                                                    "www.Youtube.com"),
            "all_instagram_count": get_social_percent(self.request.user,
                                                      "www.Instagram.com"),

        }

        return render(request, "search_dashboard.html", context)


def search_api(request):
    print("access here")
    query = request.GET.get('query')
    category = request.GET.get('category')
    search_info = SearchInfo.objects.create(
        user=request.user,
        platform="Google Map",
        keyword=category,
        location=query.replace("[", "").replace('"', "").replace("]", "")
    )
    get_all_place.delay(query, category, request.user.id, search_info.id)
    # Get the single place
    return JsonResponse({"status": "ok", "id": search_info.id})


def place_detail(request):
    """
    this is used to get a place detail and returns the info
    :param request:
    :return:
    """
    query = request.GET.get('query')
    # Get the single place
    url = f'https://maps.googleapis.com/maps/api/place/textsearch/json?key={api_key}&query={query}'
    response = requests.get(url, proxies=proxies)
    if not response.status_code == 200:
        return JsonResponse(status=400)
    data = response.json().get("results")[0]

    if data.get("photos"):
        photo_reference = data.get('photos')[0].get('photo_reference')
        image_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={api_key}"
        response = requests.get(image_url, allow_redirects=True)

        if response.status_code == 200:
            image_data = response.content
            image_b64 = base64.b64encode(image_data).decode('utf-8')
            data["photo"] = f"data:image/jpeg;base64,{image_b64}"
        else:
            data["photo"] = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSX1mtYL8f3jCPWwGO9yCiCJlbi8LikmuJMew"

    return JsonResponse(data)


def autocomplete_api(request):
    """
    this is used to show the auto  complete suggestion for the frontend
    :param request:
    :return:
    """
    query = request.GET.get('query')
    type = request.GET.get('type')
    # Replace YOUR_API_KEY with your actual API key and YOUR_PROXY_URL with your proxy URL
    api_key = config("GOOGLE_MAP_API_KEY")

    if type:
        url = f'https://maps.googleapis.com/maps/api/place/autocomplete/json?key={api_key}&input={query}&types=establishment'
    else:
        url = f'https://maps.googleapis.com/maps/api/place/autocomplete/json?key={api_key}&input={query}'
    # Make the request using the proxy dictionary
    response = requests.get(url, proxies=proxies)
    # Return the response as a JSON object
    return JsonResponse(response.json())


@login_required
def map_view(request):
    """
    this shows the map itself
    :param request:
    :return:
    """
    # Replace YOUR_API_KEY with your actual Google Maps API key
    api_key = config("GOOGLE_MAP_API_KEY")
    context = {'api_key': api_key}
    return render(request, 'map.html', context)


class SearchInfoListView(LoginRequiredMixin, ListView):
    queryset = SearchInfo.objects.all()
    template_name = "search_info.html"
    paginate_by = 50

    def get_queryset(self):
        """
        Return the list of items for this view.

        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.
        """
        queryset = self.queryset.filter(user=self.request.user)
        return queryset


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
        id = self.kwargs['id']
        query = self.request.GET.get('search')
        username = self.request.GET.get('username')

        search_info = get_object_or_404(SearchInfo, id=id)
        queryset = search_info.history_set.all()
        ordering = self.get_ordering()
        if query:
            queryset = query_items(item=queryset, query=query)
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)
        if username:
            queryset = queryset.filter(user__username=username)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Overiding context data
        :param kwargs:
        :return:
        """
        context = super().get_context_data(**kwargs)
        context['item_form'] = HistoryUpdateForm()
        context["users"] = User.objects.all()
        context["search_info_id"] = self.kwargs['id']
        context["search_info"] = SearchInfo.objects.filter(id=self.kwargs['id']).first()
        return context


class AdminHistoryListView(LoginRequiredMixin, ListView):
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
        username = self.request.GET.get('username')

        queryset = self.queryset.filter()
        ordering = self.get_ordering()
        if query:
            queryset = query_items(item=queryset, query=query)
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)
        if username:
            queryset = queryset.filter(user__username=username)

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


class ExportSearchInfoCSV(LoginRequiredMixin, View):

    def get(self, request, **kwargs):
        csv = export_search_info_user_csv(self.kwargs['id'])
        return csv


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
