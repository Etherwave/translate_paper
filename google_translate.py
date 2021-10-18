from google_trans_new import google_translator

def google_translate(text):
    translator = google_translator()
    try:
        ans = translator.translate(text, lang_tgt='zh')
    except:
        ans = "something is wrong!"
    return ans


if __name__ == '__main__':
    ans = google_translate("""Since
both variants can be easily integrated into the presented algorithms,
we didn’t clutter the pseudocode with these steps.""")
    print(ans)