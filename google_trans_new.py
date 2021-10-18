# coding:utf-8
# author LuShan
# version : 1.1.9
import json, requests, random, re
from urllib.parse import quote
import urllib3
import logging
from constant import LANGUAGES, DEFAULT_SERVICE_URLS

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URLS_SUFFIX = [re.search('translate.google.(.*)', url.strip()).group(1) for url in DEFAULT_SERVICE_URLS]
URL_SUFFIX_DEFAULT = 'cn'


headers = {
    "Referer": "https://translate.google.cn/",
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0',
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
    "Origin": "https://translate.google.cn",
    "Connection": "close",
    "X-Same-Domain": "1",
    "X-Goog-BatchExecute-Bgr": "[\";gpy4nNHQAAYjKaoDIylf7BBZqYb4OtYmACkAIwj8RqVE6iZklU4oHZZSOOQrKiEM0LAQLxmMCUJIenl-tJxc286fah8AAABTTwAAAB51AQcXAGdmC4AEd-xL7Czop-ohtTTa4UUs4QslH2Li7pe7MTB6C3otIopZ0qL3VjERdayByKLbNNpalHN-5YtBmHAoGbgbAtNjZA7Y-tBeJn9tPwKApUGDaa21BMSxKdENNdGiBA97NewLtDLChAIhyWnHci4wD_wBoEaf000EmXoujikHC-KZKQI07AVy2N6i6AV54So6-HiNUUFwPEYlGiv-DnLWMbdLyoGLUOHLzrb7RrG5d_o3aiKajhGEa-0XtkKohCa0nIFNu8G9s2VL-o1L6O9i35LvZs8cHpDOkQgqHbxkQupYdHzfiFxkCrz11CO_bR4ldHzJ3zvUYdi62OGt6lX62dhJFh28pIJGDImZQmzJYADG95Low8mTPth6kcunNiXxyaQU2Q_IsqRb-zjdwwSplvsHai5OOFGJ7XV6Hkj9Kkyjy5bfmX5K48nFUqno6S-47opZvjGJS3F7I8IEoIsxZx6UiYB7BgvExvIKmChYUx8mEQGNARZ2AqyASxfihR5g7qGxyea-1eUS_fJpoiCEGb1jEaKEeVn8oV-X0xDyK_zuRm3zl1M4_r14AjC6-SXo-xHczKnfIxH2KUqiDrfOvezhpPfsObf6qNzJOFbQuXVR_I_e5GpS4pVYbMYDbDW3iDML0XA-DXJiYB56cu9m17g7NmJhXpM-lU1VLYwAyir6ky3wMEQ2k4Nyf3Bk4jlNV1qqA3-BbSEGt5GDepJurL7uyYJ85pTR84isFzoT8iazqIRNXa25acIwJ82v1_oVepiBs8PcctOnUhwwVe64YqEIEcg_cSj39p1Amoma9NsTuDui7rdkxeHvQH0GSfa-aUz0DP7eFAyr9T727oiUBoSarE3KQE44y6M\",null,null,44,null,null,null,0,\"2\"]"
}

class google_new_transError(Exception):
    """Exception that uses context to present a meaningful error message"""

    def __init__(self, msg=None, **kwargs):
        self.tts = kwargs.pop('tts', None)
        self.rsp = kwargs.pop('response', None)
        if msg:
            self.msg = msg
        elif self.tts is not None:
            self.msg = self.infer_msg(self.tts, self.rsp)
        else:
            self.msg = None
        super(google_new_transError, self).__init__(self.msg)

    def infer_msg(self, tts, rsp=None):
        cause = "Unknown"

        if rsp is None:
            premise = "Failed to connect"

            return "{}. Probable cause: {}".format(premise, "timeout")
            # if tts.tld != 'com':
            #     host = _translate_url(tld=tts.tld)
            #     cause = "Host '{}' is not reachable".format(host)

        else:
            status = rsp.status_code
            reason = rsp.reason

            premise = "{:d} ({}) from TTS API".format(status, reason)

            if status == 403:
                cause = "Bad token or upstream API changes"
            elif status == 200 and not tts.lang_check:
                cause = "No audio stream in response. Unsupported language '%s'" % self.tts.lang
            elif status >= 500:
                cause = "Uptream API error. Try again later."

        return "{}. Probable cause: {}".format(premise, cause)


class google_translator:
    '''
    You can use 108 language in target and source,details view LANGUAGES.
    Target language: like 'en'、'zh'、'th'...

    :param url_suffix: The source text(s) to be translated. Batch translation is supported via sequence input.
                       The value should be one of the url_suffix listed in : `DEFAULT_SERVICE_URLS`
    :type url_suffix: UTF-8 :class:`str`; :class:`unicode`; string sequence (list, tuple, iterator, generator)

    :param text: The source text(s) to be translated.
    :type text: UTF-8 :class:`str`; :class:`unicode`;

    :param lang_tgt: The language to translate the source text into.
                     The value should be one of the language codes listed in : `LANGUAGES`
    :type lang_tgt: :class:`str`; :class:`unicode`

    :param lang_src: The language of the source text.
                    The value should be one of the language codes listed in :const:`googletrans.LANGUAGES`
                    If a language is not specified,
                    the system will attempt to identify the source language automatically.
    :type lang_src: :class:`str`; :class:`unicode`

    :param timeout: Timeout Will be used for every request.
    :type timeout: number or a double of numbers

    :param proxies: proxies Will be used for every request.
    :type proxies: class : dict; like: {'http': 'http:171.112.169.47:19934/', 'https': 'https:171.112.169.47:19934/'}

    '''

    def __init__(self, url_suffix="cn", timeout=5, proxies=None):
        self.proxies = proxies
        if url_suffix not in URLS_SUFFIX:
            self.url_suffix = URL_SUFFIX_DEFAULT
        else:
            self.url_suffix = url_suffix
        url_base = "https://translate.google.{}".format(self.url_suffix)
        self.url = url_base + "/_/TranslateWebserverUi/data/batchexecute"
        self.timeout = timeout

    def _package_rpc(self, text, lang_src='auto', lang_tgt='auto'):
        ##https://translate.google.cn/_/TranslateWebserverUi/data/batchexecute?rpcids=QShL0&f.sid=3167531912345882768&bl=boq_translate-webserver_20211013.12_p0&hl=zh-CN&soc-app=1&soc-platform=1&soc-device=1&_reqid=737790&rt=c
        GOOGLE_TTS_RPC = ["MkEWBc"]
        parameter = [[text.strip(), "auto", "zh-CN", True], [None]]
        # print(parameter)
        # [['we didn’t clutter the pseudocode with these steps.', 'en', 'zh-CN', True], [None]]
        escaped_parameter = json.dumps(parameter, separators=(',', ':'))
        # print(escaped_parameter)
        # [["we didn\u2019t clutter the pseudocode with these steps.","en","zh-CN",true],[null]]
        rpc = [[[random.choice(GOOGLE_TTS_RPC), escaped_parameter, None, "generic"]]]
        # print(rpc)
        #f.req: [[["AVdN8","[\"h\",\"en\",\"zh-CN\"]",null,"generic"]]]

        espaced_rpc = json.dumps(rpc, separators=(',', ':'))
        # text_urldecode = quote(text.strip())
        # print(espaced_rpc)
        # [[["MkEWBc","[[\"h\",\"en\",\"zh-CN\",true],[null]]",null,"generic"]]]
        # should be [[["MkEWBc","[[\"g\",\"auto\",\"zh-CN\",true],[null]]",null,"generic"]]]&
        # [[["MkEWBc","[[\"we didn't clutter the pseudocode with these steps.\",\"auto\",\"zh-CN\",true],[null]]",null,"generic"]]]
        # [[["MkEWBc","[[\"we didn’t clutter the pseudocode with these steps.\",\"auto\",\"zh-CN\",true],[null]]",null,"generic"]]]&
        freq_initial = "f.req={}&".format(quote(espaced_rpc))
        # print(freq_initial)
        freq = freq_initial
        return freq

    def translate(self, text, lang_tgt='auto', lang_src='auto', pronounce=False):
        try:
            lang_src = LANGUAGES[lang_src]
        except:
            lang_src = 'auto'
        try:
            lang_tgt = LANGUAGES[lang_tgt]
        except:
            lang_tgt = 'auto'
        text = str(text)
        if len(text) >= 5000:
            return "Warning: Can only detect less than 5000 characters"
        if len(text) == 0:
            return ""
        # headers = {
        #     "Referer": "http://translate.google.{}/".format(self.url_suffix),
        #     "User-Agent": 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6',
        #     "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
        # }
        freq = self._package_rpc(text, lang_src, lang_tgt)
        # print(self.url)
        # print(freq)
        #f.req=%5B%5B%5B%22MkEWBc%22%2C%22%5B%5B%5C%22we%20didn%5C%5Cu2019t%20clutter%20the%20pseudocode%20with%20these%20steps.%5C%22%2C%5C%22english%5C%22%2C%5C%22chinese%20%28simplified%29%5C%22%2Ctrue%5D%2C%5B1%5D%5D%22%2Cnull%2C%22generic%22%5D%5D%5D&
        #https://translate.google.cn/_/TranslateWebserverUi/data/batchexecute?rpcids=QShL0&f.sid=3167531912345882768&bl=boq_translate-webserver_20211013.12_p0&hl=zh-CN&soc-app=1&soc-platform=1&soc-device=1&_reqid=737790&rt=c
        #https://translate.google.cn/_/TranslateWebserverUi/data/batchexecute?rpcids
        #https://translate.google.cn/_/TranslateWebserverUi/data/batchexecute
        response = requests.Request(method='POST',
                                    url=self.url,
                                    data=freq,
                                    headers=headers,
                                    )
        try:
            if self.proxies == None or type(self.proxies) != dict:
                self.proxies = {}
            with requests.Session() as s:
                s.proxies = self.proxies
                r = s.send(request=response.prepare(),
                           verify=False,
                           timeout=self.timeout)

            for line in r.iter_lines(chunk_size=1024):
                decoded_line = line.decode('utf-8')
                if "MkEWBc" in decoded_line:
                    try:
                        response = decoded_line
                        response = json.loads(response)
                        response = list(response)
                        response = json.loads(response[0][2])
                        response_ = list(response)
                        response = response_[1][0]
                        if len(response) == 1:
                            if len(response[0]) > 5:
                                sentences = response[0][5]
                            else: ## only url
                                sentences = response[0][0]
                                if pronounce == False:
                                    return sentences
                                elif pronounce == True:
                                    return [sentences,None,None]
                            translate_text = ""
                            for sentence in sentences:
                                sentence = sentence[0]
                                translate_text += sentence.strip() + ' '
                            translate_text = translate_text
                            if pronounce == False:
                                return translate_text
                            elif pronounce == True:
                                pronounce_src = (response_[0][0])
                                pronounce_tgt = (response_[1][0][0][1])
                                return [translate_text, pronounce_src, pronounce_tgt]
                        elif len(response) == 2:
                            sentences = []
                            for i in response:
                                sentences.append(i[0])
                            if pronounce == False:
                                return sentences
                            elif pronounce == True:
                                pronounce_src = (response_[0][0])
                                pronounce_tgt = (response_[1][0][0][1])
                                return [sentences, pronounce_src, pronounce_tgt]
                    except Exception as e:
                        raise e
            r.raise_for_status()
        except requests.exceptions.ConnectTimeout as e:
            raise e
        except requests.exceptions.HTTPError as e:
            # Request successful, bad response
            raise google_new_transError(tts=self, response=r)
        except requests.exceptions.RequestException as e:
            # Request failed
            raise google_new_transError(tts=self)

    def detect(self, text):
        text = str(text)
        if len(text) >= 5000:
            return log.debug("Warning: Can only detect less than 5000 characters")
        if len(text) == 0:
            return ""
        headers = {
            "Referer": "https://translate.google.{}/".format(self.url_suffix),
            "User-Agent": 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6',
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
        }
        freq = self._package_rpc(text)
        response = requests.Request(method='POST',
                                    url=self.url,
                                    data=freq,
                                    headers=headers)
        try:
            if self.proxies == None or type(self.proxies) != dict:
                self.proxies = {}
            with requests.Session() as s:
                s.proxies = self.proxies
                r = s.send(request=response.prepare(),
                           verify=False,
                           timeout=self.timeout)

            for line in r.iter_lines(chunk_size=1024):
                decoded_line = line.decode('utf-8')
                if "MkEWBc" in decoded_line:
                    # regex_str = r"\[\[\"wrb.fr\",\"MkEWBc\",\"\[\[(.*).*?,\[\[\["
                    try:
                        # data_got = re.search(regex_str,decoded_line).group(1)
                        response = (decoded_line)
                        response = json.loads(response)
                        response = list(response)
                        response = json.loads(response[0][2])
                        response = list(response)
                        detect_lang = response[0][2]
                    except Exception:
                        raise Exception
                    # data_got = data_got.split('\\\"]')[0]
                    return [detect_lang, LANGUAGES[detect_lang.lower()]]
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Request successful, bad response
            log.debug(str(e))
            raise google_new_transError(tts=self, response=r)
        except requests.exceptions.RequestException as e:
            # Request failed
            log.debug(str(e))
            raise google_new_transError(tts=self)


if __name__ == '__main__':
    ans = google_translator().translate("pseudocode", lang_src="en", lang_tgt='zh-cn')
    ans = google_translator().translate("we didn't clutter the pseudocode with these steps.", lang_tgt="zh-CN")
    # ans = google_translator().translate("h", lang_src="en", lang_tgt='zh-cn')
    print(ans)