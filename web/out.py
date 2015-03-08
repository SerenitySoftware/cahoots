from datetime import date, datetime
from cahoots.result import ParseResult
import simplejson


class CahootsEncoder(simplejson.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, ParseResult):
            return {
                'type': obj.type,
                'subtype': obj.subtype,
                'confidence': obj.confidence,
                'value': obj.result_value,
                'data': obj.data
            }

        return super(CahootsEncoder, self).default(obj)


def encode(data, level=0, indent=True):
    return simplejson.dumps(data, indent=4, cls=CahootsEncoder)
