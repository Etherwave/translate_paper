# translate_paper

这个项目了有百度翻译，有道翻译，谷歌翻译和deepl翻译的一些代码，暂时也没有整理。

之前好用的是google翻译，但是他加了一个X-Goog-BatchExecute-Bgr的cookie，我模拟不出来（不太懂js），没有这个参数，会导致翻译的不太正确，例如“we didn't clutter the pseudocode with these steps.”这个句子。正确的翻译应该是："我们没有在伪代码中加入这些步骤。" 但是没有正确的参数的时候google会翻译成： “我们并没有将伪偶像杂交与这些步骤混淆。 ”。

蹲一个大佬来解决这个问题，我实在是搞不定。。s

然后找到了另一个对deepl翻译python实现调用的项目，这里感谢该项目的作者，项目地址：[https://github.com/ptrstn/deepl-translate](https://github.com/ptrstn/deepl-translate)

这里就仅仅是加了个界面，你只需要把pdf论文的文字复制进来即可

之后或许会考虑直接读取论文的内容直接翻译

注：本项目仅供学习使用，请不要用于商业用途。