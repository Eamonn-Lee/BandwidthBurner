import requests
import threading
import time

"""
Bandwidth burner with threading
"""

url = "https://nbg1-speed.hetzner.com/10GB.bin" # target download

N_THREADS = 32
CHUNK_SIZE = 1024 * 1024  # 1 mb
MAX_MB_PER_THREAD = 200  # prevent threads from going too crazy

# per thread
def burn(t_id):
    headers = {'User-Agent': 'Mozilla/5.0'}

    while True:
        print(f"[thread-{t_id}] burning: {url}")
        try:
            start_time = time.time()

            # request stream
            r = requests.get(url, stream=True, headers=headers, timeout=15)

            if r.status_code != 200:
                print(f"[thread-{t_id}] FAIL: {r.status_code}")
                time.sleep(5)
                continue

            total_bytes = 0
            last_print_time = time.time()

            # stream chunk
            for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    total_bytes += len(chunk)

                    now = time.time()
                    if now - last_print_time > 2:   # 2sec updates
                        burned_mb = total_bytes / (1024 * 1024)
                        print(f"[thread-{t_id}] burnt {burned_mb:.2f} MB", end='\r')
                        last_print_time = now


            elapsed = time.time() - start_time
            total_mb = total_bytes / (1024 * 1024)
            print(f"\n[thread-{t_id}] burnt {total_mb:.2f} MB in {elapsed:.2f} sec ({total_mb / elapsed:.2f} MB/s)")

        except requests.exceptions.RequestException as e:   # catchall
            print(f"[thread-{t_id}] burn failed: {e}")
            time.sleep(5)

threads = []
for i in range(N_THREADS):
    t = threading.Thread(target=burn, args=(i + 1,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()
