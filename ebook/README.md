# E-book

## 使用函式庫
- [Highlight Within Textarea](https://lonekorean.github.io/highlight-within-textarea/)

## Google 小姐 Web API
- Web API 網址：[https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=zh-TW&q=你的自訂文字](https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=zh-TW&q=你的自訂文字)
- 將文字進行 url encode 網頁：[https://www.onlinewebtoolkit.com/url-encode-decode](https://www.onlinewebtoolkit.com/url-encode-decode)
- 在 Terminal 使用 curl 指令下載 mp3:
  ```bash
  curl -X GET "https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=zh-TW&q=%E4%BD%A0%E7%9A%84%E8%87%AA%E8%A8%82%E6%96%87%E5%AD%97" -o ./test.mp3
  ```
- tl=zh-TW 的其它設定：[https://gist.github.com/JT5D/a2fdfefa80124a06f5a9](https://gist.github.com/JT5D/a2fdfefa80124a06f5a9)
- 可以參考這個範例 [https://github.com/telunyang/python_basics/blob/master/cases/multimedia/google_lady.py](https://github.com/telunyang/python_basics/blob/master/cases/multimedia/google_lady.py)