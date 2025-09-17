from shared.models import Event


def get_event_date(event: Event):
    return event.timestamp.strftime('%Y-%m-%d')
