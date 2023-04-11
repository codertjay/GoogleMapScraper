import csv
import operator
from functools import reduce

from django.db.models import Q
from django.http import HttpResponse

from map_scrapers.models import History
from textblob import TextBlob
from .tasks import get_all_place, create_item_task


def export_user_csv(user):
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
