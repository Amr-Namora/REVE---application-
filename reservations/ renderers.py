# renderers.py
from rest_framework.renderers import JSONRenderer
import json


class CustomJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        ret = json.dumps(data, ensure_ascii=False)
        if isinstance(ret, str):
            return ret.encode(self.charset)
        return ret

