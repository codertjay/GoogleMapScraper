import csv
import operator
from functools import reduce

from django.db.models import Q
from django.http import HttpResponse

from map_scrapers.models import History, SearchInfo
from .tasks import create_item_task


def get_social_percent(user, social):
    social_count = History.objects.filter(user=user,
                                          social_media_links__icontains=social).count()
    total_count = History.objects.all().count()
    if social_count == 0:
        social_count = 1
    progress = (social_count / total_count) * 100
    return round(progress, 1)


def export_search_info_user_csv(search_info_id):
    """
    this returns the full info of all the product in csv format
    :return:
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="History.csv"'
    writer = csv.writer(response)

    # Get a list of all fields of the model
    fields = [f.name for f in History._meta.fields]
    fields = [f.name for f in History._meta.fields if f.name not in ['user', 'search_info']]

    # Write the header row
    writer.writerow(fields)
    search_info = SearchInfo.objects.filter(id=search_info_id).first()
    if not search_info:
        return response
    # Write the data rows
    for obj in search_info.history_set.all():
        row = [getattr(obj, f) for f in fields]
        writer.writerow(row)
    return response


def export_user_csv(user):
    """
    this returns the full info of all the product in csv format
    :return:
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="History.csv"'
    writer = csv.writer(response)

    # Get a list of all fields of the model
    fields = [f.name for f in History._meta.fields if f.name not in ['user', 'search_info']]

    # Write the header row
    writer.writerow(fields)

    # Write the data rows
    for obj in History.objects.all(user=user):
        row = [getattr(obj, f) for f in fields]
        writer.writerow(row)
    return response


def export_all_csv():
    """
    this returns the full info of all the product in csv format
    :return:
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="History.csv"'
    writer = csv.writer(response)

    # Get a list of all fields of the model
    fields = [f.name for f in History._meta.fields]

    # Write the header row
    writer.writerow(fields)

    # Write the data rows
    for obj in History.objects.all():
        row = [getattr(obj, f) for f in fields]
        writer.writerow(row)
    return response


def query_items(query, item):
    """
    this query list is used to filter item more of like a custom query the return the query set
    :param query:
    :param item:
    :return:
    """
    query_list = []
    query_list += query.split()
    query_list = sorted(query_list, key=lambda x: x[-1])
    query = reduce(
        operator.or_,
        (Q(business_name=x) |
         Q(email__icontains=x) |
         Q(full_address__icontains=x) |
         Q(business_name__in=[x]) for x in query_list)
    )
    object_list = item.filter(query).distinct()
    return object_list


def read_search_csv(search_csv, user_id):
    """this is used to update and read items """
    # making it a task to enable updating faster
    decoded_file = search_csv.read().decode('utf-8').splitlines()
    create_item_task.delay(decoded_file, user_id)
