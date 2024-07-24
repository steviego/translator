import streamlit as st
import requests
from openai import OpenAI

# DeepL 번역 함수 정의
def translate_with_deepl(api_key: str, text: str, source_lang: str, target_lang: str) -> str:
    url = "https://api-free.deepl.com/v2/translate"
    params = {
        "auth_key": api_key,
        "text": text,
        "target_lang": target_lang
    }
    if source_lang != "auto":
        params["source_lang"] = source_lang

    try:
        response = requests.post(url, data=params)
        response.raise_for_status()
        data = response.json()
        if "translations" in data and len(data["translations"]) > 0:
            return data["translations"][0]["text"]
        else:
            st.error(f"Unexpected API response structure: {data}")
            return "Translation failed due to unexpected API response."
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {str(e)}")
        return f"Translation failed: {str(e)}"
    except ValueError as e:
        st.error(f"Failed to parse API response: {str(e)}")
        return "Translation failed due to API response parsing error."
    except KeyError as e:
        st.error(f"Unexpected API response structure: {str(e)}")
        return "Translation failed due to unexpected API response structure."

# GPT 번역 함수 정의
def translate_with_gpt(api_key: str, model: str, text: str, source_lang: str, target_lang: str) -> str:
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": f"Translate the following text from {source_lang} to {target_lang}"},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content.strip()

# 언어 옵션 정의
LANGUAGE_OPTIONS = {
    "auto": "Auto Detect",
    "EN": "English",
    "KO": "Korean",
    "FR": "French",
    "DE": "German",
    "ES": "Spanish",
    "JA": "Japanese",
    "ZH": "Chinese"
}

# Streamlit 앱 설정
st.set_page_config(page_title="CMDSPACE Translator", layout="wide")
st.title("CMDSPACE Translator")
st.markdown("Created by [Yohan Koo](https://litt.ly/cmds)")
st.header("DeepL 및 GPT 번역기")

# 사이드바에 API 키 입력받기
st.sidebar.header("API 설정")
deepl_api_key = st.sidebar.text_input("DeepL API 키 입력", type="password")
gpt_api_key = st.sidebar.text_input("GPT API 키 입력", type="password")

# GPT 모델 선택
gpt_model = st.sidebar.selectbox("GPT 모델 선택", ["gpt-3.5-turbo-0125", "gpt-4", "gpt-4-turbo-preview"])

# 결과에 넣을 API 선택 (체크박스 리스트)
st.sidebar.header("결과에 넣을 API 선택")
api_choices = []
if st.sidebar.checkbox("DeepL"):
    api_choices.append("DeepL")
if st.sidebar.checkbox("GPT"):
    api_choices.append("GPT")

# 번역할 텍스트 입력
text_input = st.text_area("번역할 텍스트를 입력하세요")

# 파일 업로드
uploaded_file = st.file_uploader("파일 업로드", type=["txt"])
if uploaded_file is not None:
    text_input = uploaded_file.read().decode("utf-8")

# 원본 언어 선택
source_lang = st.selectbox("원본 언어 선택", 
                           options=list(LANGUAGE_OPTIONS.keys()), 
                           format_func=lambda x: f"{x} - {LANGUAGE_OPTIONS[x]}")

# 번역 대상 언어 선택
target_lang = st.selectbox("번역할 언어 선택", 
                           options=[lang for lang in LANGUAGE_OPTIONS.keys() if lang != "auto"], 
                           format_func=lambda x: f"{x} - {LANGUAGE_OPTIONS[x]}")

# 번역 실행
if st.button("번역"):
    if text_input:
        results = {}
        
        if "DeepL" in api_choices and deepl_api_key:
            with st.spinner("DeepL로 번역 중..."):
                translated_text_deepl = translate_with_deepl(deepl_api_key, text_input, source_lang, target_lang)
                results["DeepL Ver."] = translated_text_deepl
        
        if "GPT" in api_choices and gpt_api_key:
            with st.spinner(f"GPT ({gpt_model})로 번역 중..."):
                translated_text_gpt = translate_with_gpt(gpt_api_key, gpt_model, text_input, source_lang, target_lang)
                results[f"GPT ({gpt_model}) Ver."] = translated_text_gpt
        
        if results:
            st.subheader("번역 결과")
            for key, value in results.items():
                with st.expander(f"**{key}**", expanded=True):
                    st.code(value, language="markdown")
                    st.markdown("---")
        else:
            st.warning("API 키를 입력하고, 결과에 넣을 API를 선택하세요.")
    else:
        st.warning("번역할 텍스트를 입력하세요.")

# 사용 안내 추가
st.markdown("---")
st.markdown("""
### 사용 방법
1. 사이드바에서 사용할 번역 API를 선택하고 해당 API 키를 입력하세요.
2. 번역할 텍스트를 입력하거나 텍스트 파일을 업로드하세요.
3. 원본 언어와 번역할 언어를 선택하세요.
4. '번역' 버튼을 클릭하세요.
5. 결과를 확인하고 코드 블록 오른쪽 상단의 복사 아이콘을 클릭하여 결과를 클립보드에 복사하세요.
""")
