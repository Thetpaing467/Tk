import os
import requests

BASE = "https://open.tiktokapis.com/v2"
CHUNK = 10 * 1024 * 1024  # 10 MB


def refresh_access_token(client_key, client_secret, refresh_token):
    r = requests.post(
        f"{BASE}/oauth/token/",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "client_key": client_key,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
    )
    r.raise_for_status()
    return r.json()["access_token"]


def _headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=UTF-8",
    }


def creator_info(token):
    r = requests.post(f"{BASE}/post/publish/creator_info/query/", headers=_headers(token))
    r.raise_for_status()
    return r.json()["data"]


def post_video(token, video_path, caption, privacy=None):
    options = creator_info(token)["privacy_level_options"]
    if privacy not in options:
        privacy = "PUBLIC_TO_EVERYONE" if "PUBLIC_TO_EVERYONE" in options else options[0]

    size = os.path.getsize(video_path)
    total = max(1, size // CHUNK)
    body = {
        "post_info": {"title": caption, "privacy_level": privacy},
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": size,
            "chunk_size": min(CHUNK, size),
            "total_chunk_count": total,
        },
    }
    r = requests.post(f"{BASE}/post/publish/video/init/", headers=_headers(token), json=body)
    r.raise_for_status()
    data = r.json()["data"]

    with open(video_path, "rb") as f:
        for i in range(total):
            start = i * CHUNK
            end = size - 1 if i == total - 1 else start + CHUNK - 1
            f.seek(start)
            chunk = f.read(end - start + 1)
            up = requests.put(
                data["upload_url"],
                headers={
                    "Content-Type": "video/mp4",
                    "Content-Length": str(len(chunk)),
                    "Content-Range": f"bytes {start}-{end}/{size}",
                },
                data=chunk,
            )
            if up.status_code not in (200, 201, 206):
                raise RuntimeError(f"Upload failed: {up.status_code} {up.text}")
    return data["publish_id"]


def get_status(token, publish_id):
    r = requests.post(
        f"{BASE}/post/publish/status/fetch/",
        headers=_headers(token),
        json={"publish_id": publish_id},
    )
    r.raise_for_status()
    return r.json()["data"]["status"]
