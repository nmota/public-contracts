from datetime import timedelta, date
import collections

from django.db.models import Count

from deputies import models


def get_time_in_office_distribution():

    data = []

    # build the set of values
    for deputy in models.Deputy.objects.all():
        total_time = timedelta(0)
        for mandate in deputy.mandate_set.all().values('date_end', 'date_start'):
            date_end = mandate['date_end']
            date_start = mandate['date_start']

            if date_end is None:
                date_end = date.today()

            total_time += date_end - date_start

        if total_time:
            data.append({'id': deputy.id, 'total': total_time.days})

    # create the histogram
    bin_size = 50  # bin of 50 days; 50 just because it looks good enough

    cumulative = []
    bin = 0
    while True:
        cumulative.append({'min': (1 + bin)*bin_size, 'count': 0})

        for datum in data:
            if datum['total'] >= cumulative[bin]['min']:
                cumulative[bin]['count'] += 1

        if cumulative[bin]['count'] == 0:
            cumulative.remove(cumulative[bin])
            break

        bin += 1

    return cumulative


def get_mandates_in_office_distribution():

    deputies = models.Deputy.objects.all().annotate(count=Count('mandate__id'))

    # build histogram
    count = 0
    histogram = collections.defaultdict(int)
    for deputy in deputies:
        histogram[deputy.count] += 1
        count += 1

    data = []
    for x in histogram:
        data.append({'mandates': x, 'count': histogram[x]})

    return data
