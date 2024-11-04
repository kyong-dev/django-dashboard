from django.utils import timezone


def get_start_of_today():
    return get_start_of_date(timezone.now())


def get_start_of_date(date):
    return date.replace(hour=0, minute=0, second=0, microsecond=0)


def timezone_convert(datetime_at):
    return timezone.localtime(datetime_at).strftime("%Y-%m-%d %H:%M:%S")
