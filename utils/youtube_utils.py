import time
from utils.upload import upload_to_youtube

def upload_with_retry(output_path, caption, full_description, all_tags, max_retries=100, retry_wait=60*30):
    upload_success = False
    retries = 0
    while not upload_success and retries < max_retries:
        try:
            upload_to_youtube(output_path, caption, full_description, all_tags)
            upload_success = True
        except Exception as e:
            if 'uploadLimitExceeded' in str(e):
                print('[WARN] YouTube upload limit reached. Waiting before retrying...')
                time.sleep(retry_wait)
                retries += 1
            else:
                print(f'[ERROR] Upload failed: {e}')
                break
