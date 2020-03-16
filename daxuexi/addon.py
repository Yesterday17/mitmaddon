import re
from mitmproxy import http

user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/7.0.8(0x17000820) NetType/WIFI Language/zh_CN'


class daxuexi:
    def __init__(self):
        # 修改使得 iPad 也可以使用
        self.regex_modify_url = re.compile(
            '(.+?h5\.cyol\.com/special/daxuexi(?:all|/daxuexiall)?.*/)index(\.(?:html|php))')
        self.regex_modify_response = re.compile('h5\.cyol\.com/special/daxuexi(?:/daxuexiall)?.*/a?m\.(?:html|php)')

        # 替换微信分享标题
        self.regex_score = re.compile("'([^']+完成[^']+)'")
        self.regex_inject = re.compile("'([^']+学习[^']+)'")

        # 动画跳转到结束
        self.regex_end = re.compile('setTimeout\(function\(\) {(?:.|\n)+?\}, 1000\);')

    def request(self, flow: http.HTTPFlow):
        if flow.request.host.__eq__('h5.cyol.com'):
            # 统一替换为 iOS UserAgent
            flow.request.headers['User-Agent'] = user_agent

            # 将所有的页面重定向到移动端浏览页面
            match = self.regex_modify_url.search(flow.request.url)
            if match is not None:
                flow.request.url = match.group(1) + 'm' + match.group(2)

    def response(self, flow: http.HTTPFlow):
        if self.regex_modify_response.search(flow.request.url) is not None:
            body = flow.response.text
            body = body.replace('iPad', 'mitm')  # 绕过 iPad UserAgent 检测

            title = ''
            for match in self.regex_score.finditer(body):
                if match.group(1).__contains__('满分') or match.group(1).__contains__('优秀'):
                    title = "'" + match.group(1) + "'"  # 取其最高分
                    break

            if title != '':
                body = self.regex_inject.sub(title, body)  # 替换所有分享标题

            # 直接过场到结束
            append = '<script>'
            for match in self.regex_end.finditer(body):
                append = match.group(0)
            append = '\n<script>\n' + append + '\n</script>'

            flow.response.text = body + append
