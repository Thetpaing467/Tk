import tempfile
import time
import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
import tiktok_api as tt

st.set_page_config(page_title="TikTok Auto Post", page_icon="🎵")
st.title("🎵 TikTok Poster (Germany)")
st.caption(f"Berlin time: {datetime.now(ZoneInfo('Europe/Berlin')):%Y-%m-%d %H:%M}")

# --- Token ---
try:
    token = tt.refresh_access_token(
        st.secrets["TIKTOK_CLIENT_KEY"],
        st.secrets["TIKTOK_CLIENT_SECRET"],
        st.secrets["TIKTOK_REFRESH_TOKEN"],
    )
except Exception as e:
    st.error(f"Token error: {e}")
    st.stop()

video = st.file_uploader("Video (mp4)", type=["mp4"])
caption = st.text_area("Caption", "Guten Tag! #deutschland #fyp", max_chars=2200)
privacy = st.selectbox("Privacy", ["PUBLIC_TO_EVERYONE", "SELF_ONLY"])

if st.button("Post now", disabled=video is None):
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp.write(video.read())
        path = tmp.name
    with st.spinner("Uploading..."):
        try:
            pid = tt.post_video(token, path, caption, privacy)
            for _ in range(20):
                status = tt.get_status(token, pid)
                if status in ("PUBLISH_COMPLETE", "FAILED"):
                    break
                time.sleep(5)
            (st.success if status == "PUBLISH_COMPLETE" else st.error)(f"Status: {status}")
        except Exception as e:
            st.error(f"Error: {e}")
