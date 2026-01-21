import requests
import os

url = 'https://cdn-media.huggingface.co/frpc-gradio-0.2/frpc_windows_amd64.exe'
dest = os.path.expanduser('~/.gradio/frpc_windows_amd64_v0.2')

print(f"Downloading frpc from {url}...")
try:
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    with open(dest, 'wb') as f:
        f.write(r.content)
    print(f"Successfully downloaded to {dest}")
except Exception as e:
    print(f"Download failed: {e}")
