# -*- coding: utf-8 -*-
#
# ex.)
# python getimg.py --acct="kiritan,kiri_bot01,sun_pillar"
# python getimg.py --hashtag="きりぼっとギャグ,ジェバンニチャレンジ"

from mastodon import Mastodon
import re, os, json, random, unicodedata, signal, sys, requests
from time import sleep
from pprint  import pprint as pp
import argparse

SAVE_DIR = "media/"

url_ins = open("instance.txt").read()  # https://friends.nico/ とか

mastodon = Mastodon(
    access_token='user.secret',
    api_base_url=url_ins)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hashtag", type=str, default=None)
    parser.add_argument("--acct", type=str, default=None)
    args = parser.parse_args()
    return args


def save_image(filename, image):

    with open(filename, "wb") as fout:
        fout.write(image)

def download_image(url, timeout=10):
    response = requests.get(url, allow_redirects=True, timeout=timeout)
    if response.status_code != 200:
        error = Exception("HTTP status: " + response.status_code)
        raise error

    content_type = response.headers["content-type"]
    if 'image' not in content_type:
        error = Exception("Content-Type: " + content_type)
        raise error

    return response.content

if __name__ == '__main__':
    args = get_args()
    # ハッシュタグ指定かユーザID指定のどちらか一方だけ。両方指定されたらハッシュタグ優先
    if args.hashtag:
        terms_for_dirname = args.hashtag.split(",")
        terms_for_search = args.hashtag.split(",")
        func = mastodon.timeline_hashtag
    elif args.acct:
        terms_for_dirname = args.acct.split(",")
        terms_for_search = []
        # ID を username へ
        for acct in terms_for_dirname:
            sleep(2)
            users = mastodon.account_search(acct)
            # pp(users)
            for user in users:
                if user['acct'] == acct:
                    terms_for_search.append(user["id"])
                    break

        func = mastodon.account_statuses
    else:
        exit()

    for dirname, term in zip(terms_for_dirname, terms_for_search):
        save_dir = os.path.join(SAVE_DIR, dirname)
        os.makedirs(save_dir, exist_ok=True)

        max_id = None
        
        while True:
            sleep(2)
            statuses = func(term, max_id=max_id, only_media=True)
            # pp(statuses)
            if len(statuses) == 0:
                break

            for status in statuses:
                max_id=status["id"]
                for media in status["media_attachments"]:
                    url = media["url"]
                    file_extension = os.path.splitext(url)[-1]
                    if file_extension.lower() in ('.jpg', '.jpeg', '.gif', '.png', '.bmp'):
                        img_path = os.path.join(save_dir, url.split("/")[-1])
                        if os.path.exists(img_path):
                            print(f"already exists {img_path}")
                            continue
                        save_image(img_path, download_image(url))
                        print(f"save image.... from {url} to {img_path}")
                        sleep(3)

