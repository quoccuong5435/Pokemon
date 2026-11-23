"""Downloads all 974+ Pokemon 3D models from Pokemon-3D-api/assets into a local archive."""
import concurrent.futures
import json
import os
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(os.path.dirname(HERE))
OUT_DIR = os.path.join(WORK, "imports", "pokemon_3d_all")
os.makedirs(OUT_DIR, exist_ok=True)

API_URL = "https://api.github.com/repos/Pokemon-3D-api/assets/contents/models/opt/regular"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def main():
    print(f"[download] Fetching file list from GitHub API: {API_URL}")
    req = urllib.request.Request(API_URL, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        items = json.loads(resp.read().decode("utf-8"))

    print(f"[download] Found {len(items)} models to download. Target directory: {OUT_DIR}")

    tasks = []
    for it in items:
        name = it["name"]
        download_url = it["download_url"]
        target_path = os.path.join(OUT_DIR, name)
        tasks.append((name, download_url, target_path, it.get("size", 0)))

    completed = 0
    total = len(tasks)
    total_bytes = 0
    start_time = time.time()

    def download_one(task):
        name, url, dest, size = task
        if os.path.isfile(dest) and os.path.getsize(dest) > 0:
            return name, os.path.getsize(dest), True
        for attempt in range(3):
            try:
                r = urllib.request.Request(url, headers=HEADERS)
                with urllib.request.urlopen(r, timeout=20) as res:
                    data = res.read()
                with open(dest, "wb") as fp:
                    fp.write(data)
                return name, len(data), False
            except Exception as e:
                time.sleep(1)
        raise RuntimeError(f"Failed to download {name} after 3 attempts")

    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
        futures = {pool.submit(download_one, t): t for t in tasks}
        for f in concurrent.futures.as_completed(futures):
            try:
                nm, sz, cached = f.result()
                completed += 1
                total_bytes += sz
                if completed % 100 == 0 or completed == total:
                    elapsed = time.time() - start_time
                    mb = total_bytes / 1048576.0
                    print(f"[download] Progress: {completed}/{total} ({completed*100//total}%) - {mb:.1f} MB downloaded in {elapsed:.1f}s")
            except Exception as e:
                print(f"[download] Error: {e}")

    total_time = time.time() - start_time
    final_files = [f for f in os.listdir(OUT_DIR) if f.endswith(".glb")]
    final_mb = sum(os.path.getsize(os.path.join(OUT_DIR, f)) for f in final_files) / 1048576.0
    print(f"[download] DONE! Successfully downloaded {len(final_files)} models ({final_mb:.1f} MB) in {total_time:.1f} seconds!")

if __name__ == "__main__":
    main()
