import secrets
from urllib.parse import urlencode
import requests
import streamlit as st

st.title("TikTok Token ယူရန်")

KEY = st.secrets["TIKTOK_CLIENT_KEY"]
SECRET = st.secrets["TIKTOK_CLIENT_SECRET"]
REDIRECT = st.secrets["REDIRECT_URI"]  # သင့် Streamlit app URL (https://xxx.streamlit.app/)

code = st.query_params.get("code")

if not code:
    params = {
        "client_key": KEY,
        "scope": "user.info.basic,video.publish",
        "response_type": "code",
        "redirect_uri": REDIRECT,
        "state": secrets.token_urlsafe(8),
    }
    url = "https://www.tiktok.com/v2/auth/authorize/?" + urlencode(params)
    st.link_button("TikTok နဲ့ ခွင့်ပြုမယ်", url)
else:
    r = requests.post(
        "https://open.tiktokapis.com/v2/oauth/token/",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "client_key": KEY,
            "client_secret": SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT,
        },
    )
    data = r.json()
    if "refresh_token" in data:
        st.success("အောင်မြင်ပါပြီ။ အောက်က refresh token ကို copy ကူးပါ။")
        st.code(data["refresh_token"])
        st.warning("ဒီ token ကို ဘယ်သူ့ကိုမှ မပေးပါနဲ့။ Secrets ထဲပဲ ထည့်ပါ။")
    else:
        st.error(data)
