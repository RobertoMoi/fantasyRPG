from datetime import date, time

"""Questo metodo ci serve particolarmente nella view gamedev_home per poter serializzare un oggetto da passare in un 
altra vista, tutto ciò è permesso appunto da questa funzione che attraverso java script serializza un oggetto e lo
restituisce in forma di dizionario"""


def serialize(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, date):
        serial = obj.isoformat()
        return serial

    if isinstance(obj, time):
        serial = obj.isoformat()
        return serial

    return obj.__dict__
