import json


class lazyDecoder(json.JSONDecoder):
    def decode(self, s, **kwargs):

        return super().decode(s.replace('\\', '\\\\'), **kwargs)