""" This file includes utilities."""

import time


def get_epoch_time(to_string=False):
    """
    return epoch time
    :param to_string: Boolean, True means convert to String
    :return:
    """
    seconds = int(time.time())
    if to_string:
        return str(seconds)
    return seconds


def slugify_name(string_):
    """
    Convert given string into slugify
    :param string_: String
    :return: String
    """
    if string_:
        slugify_str = '_'.join(string_.split(' '))
        return slugify_str
    return string_


def boolean(value):
    """Parse the string ``"true"`` or ``"false"`` as a boolean (case
    insensitive). Also accepts ``"1"`` and ``"0"`` as ``True``/``False``
    (respectively). If the input is from the request JSON body, the type is
    already a native python boolean, and will be passed through without
    further parsing.
    """
    if isinstance(value, bool):
        return value

    if value is None:
        raise ValueError("boolean type must be non-null")
    value = str(value).lower()
    if value in ('true', 'yes', '1', 1):
        return True
    if value in ('false', 'no', '0', 0, ''):
        return False
    raise ValueError("Invalid literal for boolean(): {0}".format(value))


def parse_email(obj):
    return obj.replace(" ", "").lower()


def query_datatable_by_args_transaction(kwargs, model, query_object, ORDER_COLUMN_CHOICES, search_function):
    """
    :param dict kwargs: request param from datatable
    :param obj model: on which you want to perform action
    :param obj query_object: contains the query to filter database
    :param choices ORDER_COLUMN_CHOICES: all columns on datatable
    :param function search_function: customize function to perform search
    :rtype: dict
    """

    try:

        # start_date = kwargs.get('start_date')
        # try:
        #     start_date = datetime.strptime(str(start_date), '%Y-%m-%dT%H:%M')
        # except:
        #     start_date = datetime.strptime(str(start_date), '%Y/%m/%d %H:%M')
        #
        # # start_date = start_date - timedelta(hours=5)
        # end_date = kwargs.get('end_date')
        #
        # try:
        #     end_date = datetime.strptime(str(end_date), '%Y-%m-%dT%H:%M')
        # except:
        #     end_date = datetime.strptime(str(end_date), '%Y/%m/%d %H:%M')
        # end_date = end_date - timedelta(hours=5)
        # print(start_date)
        # print(end_date)
        # type = int(kwargs.get('status'))

        draw = int(kwargs.get('draw', 0))
        #  start
        start = int(kwargs.get('start', 0))
        #  length (limit)
        length = int(kwargs.get('length', 0))
        # data search
        search_value = kwargs.get('search[value]')
        order_column = kwargs.get('order[0][column]', 0)
        order = kwargs.get('order[0][dir]', None)

        order_column = ORDER_COLUMN_CHOICES[order_column]
        # for asc we want latest record first
        if order == 'asc':
            order_column = f'-{order_column}'

        # if type ==
        queryset = model.objects.filter(query_object)
        # Set record total
        total = queryset.count()

        # this is value that uer type in search box or user select from deopdown
        if search_value:
            queryset = search_function(queryset, search_value, kwargs)
        try:
            count = queryset.count()
        except:
            count = 0

        try:
            queryset = queryset.order_by('-id')[start:start + length]
        except:
            queryset = queryset.order_by(order_column)[start:start + length]
        return {
            'items': queryset,
            'count': count,
            'total': total,
            'draw': draw
        }
    except Exception as e:
        return {
            'exception': e,
            'items': [],
            'count': 0,
            'total': 0,
            'draw': 0
        }
