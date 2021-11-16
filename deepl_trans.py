from deepl.api import translate_en_to_zh

def deepl_trans(text):
    ans = translate_en_to_zh(text)
    return ans

if __name__ == '__main__':
    text = "we didn't clutter the pseudocode with these steps."
    ans = deepl_trans(text)
    print(ans)