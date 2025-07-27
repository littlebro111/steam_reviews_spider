import os
import requests
import json
import time
import urllib.parse
import pandas as pd

BASE_URL = "https://store.steampowered.com/appreviews/"
dir_path = r"E:\Codes\Python\steam_reviews_spider\reviews"

def fetch_reviews(appid, language="all", filter="all", day_range=30, review_type="all", purchase_type="steam",
                  num_per_page=20, max_reviews=100, longtext=0):
    reviews = []
    cursor = "*"  # 初始游标
    cnt = 1
    while cursor and len(reviews) < max_reviews:
        # 示例：https://store.steampowered.com/appreviews/2358720?json=1&language=schinese&filter=all&day_range=246&review_type=all&purchase_type=steam&num_per_page=20
        url = f"{BASE_URL}{appid}?json=1&language={language}&filter={filter}&day_range={day_range}&review_type={review_type}&purchase_type={purchase_type}&num_per_page={num_per_page}&cursor={urllib.parse.quote(cursor)}"

        try:
            response = requests.get(url)
        except Exception as e:
            print(f"请求出错: {e}")
            time.sleep(1)
            continue

        if response.status_code != 200:
            break

        data = response.json()

        if data.get('success') == 1:
            # 解析评测数据
            all_reviews = data.get('reviews', [])
            long_reviews = []
            cur_len = len(all_reviews)
            if longtext > 0:
                for i in range(len(all_reviews)):
                    if len(all_reviews[i]['review']) >= longtext:
                        long_reviews.append(all_reviews[i])
                cur_len = len(long_reviews)
                reviews.extend(long_reviews)
            else:
                reviews.extend(all_reviews)
            # 重置游标
            cursor = data.get('cursor', None)
            print(f"GET {cur_len} 条， 当前共 {len(reviews)} 条。")
        else:
            break

        if len(reviews) >= max_reviews:
            break

        if len(reviews) // 50 == cnt:
            json_file_path = os.path.join(dir_path, f"reviews_{language}_{max_reviews}_longtext_{len(reviews)}.json")
            save_reviews_to_file(reviews, json_file_path)
            cnt += 1

        time.sleep(1)

    return reviews[:max_reviews]


def clean_review_data(reviews):
    return reviews.copy()


def save_reviews_to_file(reviews, filename="reviews.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(reviews, f, ensure_ascii=False, indent=4)
    print(f"成功保存 {len(reviews)}")


def json2excel(json_file_path, excel_file_path):
    # 读取JSON文件
    data = pd.read_json(json_file_path)

    # 将"author"字段展开为单独的列
    author_data = pd.json_normalize(data['author'])
    data = pd.concat([data.drop('author', axis=1), author_data], axis=1)

    # 将DataFrame保存为Excel文件
    data.to_excel(excel_file_path, index=False)

    print(f"JSON文件已成功转换为Excel文件: {excel_file_path}")

if __name__ == "__main__":
    # 修改appid定位到不同游戏
    # 参数详见：https://partner.steamgames.com/doc/store/getreviews

    appid = "2358720"
    max_reviews = 1000
    language = "schinese"
    json_file_path = os.path.join(dir_path, f"reviews_{language}_{max_reviews}_longtext.json")
    excel_file_path = os.path.join(dir_path, f"reviews_{language}_{max_reviews}_longtext.xlsx")
    print(f"json路径：{json_file_path}")
    print(f"excel路径：{excel_file_path}")
    print("开始爬取")
    reviews = fetch_reviews(appid, language=language, filter="all", day_range=342, review_type="all",
                            purchase_type="steam", num_per_page=20, max_reviews=max_reviews, longtext=800)
    reviews = clean_review_data(reviews)
    save_reviews_to_file(reviews, json_file_path)
    json2excel(json_file_path, excel_file_path)
