from mitmproxy import http


class StarUML:
    def request(self, flow: http.HTTPFlow):
        if flow.request.url == "http://staruml.io/license/validate":
            flow.response = http.HTTPResponse.make(200)
