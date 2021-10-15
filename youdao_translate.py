import urllib.parse
import json
import urllib.request

def youdao_translate(text):
    url = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule&sessionFrom=http://fanyi.youdao.com/'
    # 有道翻译查询入口
    data = {  # 表单数据
        'i': text,
        'from': 'AUTO',
        'to': 'AUTO',
        'smartresult': 'dict',
        'client': 'fanyideskweb',
        'doctype': 'json',
        'version': '2.1',
        'keyfrom': 'fanyi.web',
        'action': 'FY_BY_CLICKBUTTION',
        'typoResult': 'false'
    }

    data = urllib.parse.urlencode(data).encode('utf-8')
    # 对POST数据进行编码

    response = urllib.request.urlopen(url, data)
    # 发出POST请求并获取HTTP响应

    html = response.read().decode('utf-8')
    # 获取网页内容，并进行解码解码

    target = json.loads(html)
    # json解析

    translateResult = target['translateResult'][0]
    ans = ""
    for i in range(len(translateResult)):
        ans = ans + translateResult[i]['tgt']
    return ans



if __name__ == '__main__':
    text = "B. Git Repository We assume in this section that the reader uses LATEX and BIBTEX. The main idea consists in having a single repository for all the scientific texts: theses, reports, articles, letters, reviews, and miscellaneous documents. Fig. 5 illustrates the recommended basic structure for a repository holding several LATEX files (or projects), along with their associated data and code. Every directory may contain specific subdirectories. For instance, Data may contain CSV, text, and other directories with specific data files. Note that there is a single BIBTEX file (with extension .bib in the Common directory). BIBTEX references can be split into several files, but these files should be common to all projects. This avoids outdated and redundant bibliographic databases."
    ans = youdao_translate(text)
    print(ans)