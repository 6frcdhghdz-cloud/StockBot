import requests
from bs4 import BeautifulSoup
import json
from telegram import Bot
import asyncio
import time

# ----------------------
# Telegram setup
# ----------------------
BOT_TOKEN = "7951022787:AAHnCfx_XyPAr91Bs2HVzX9XVZMN99pFbhw"
CHAT_ID = "6239137470"
bot = Bot(BOT_TOKEN)

# ----------------------
# Items / keywords to monitor
# ----------------------
items_to_watch = [
    {"platform": "eBay", "search": "rare sneakers", "max_price": 200},
    {"platform": "Depop", "search": "vintage streetwear", "max_price": 100},
    {"platform": "Vinted", "search": "limited edition sneakers", "max_price": 150}
]

# ----------------------
# State tracking
# ----------------------
def load_state():
    try:
        with open("state.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_state(state):
    with open("state.json", "w") as f:
        json.dump(state, f)

# ----------------------
# Scrapers
# ----------------------
def fetch_ebay(search, max_price):
    url = f"https://www.ebay.co.uk/sch/i.html?_nkw={search.replace(' ', '+')}&_sop=10"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    for item in soup.select(".s-item"):
        title = item.select_one(".s-item__title")
        price = item.select_one(".s-item__price")
        link = item.select_one(".s-item__link")
        if title and price and link:
            try:
                price_value = float(price.text.replace("£","").replace(",","").split()[0])
            except:
                continue
            if price_value <= max_price:
                results.append({"title": title.text, "price": price_value, "url": link["href"]})
    return results

def fetch_depop(search, max_price):
    url = f"https://www.depop.com/search/{search.replace(' ', '%20')}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    for item in soup.select("a._itemCard"):
        title = item.get("title")
        price_elem = item.select_one("._itemCardPrice")
        link = item.get("href")
        if title and price_elem and link:
            try:
                price_value = float(price_elem.text.replace("£","").strip())
            except:
                continue
            if price_value <= max_price:
                results.append({"title": title, "price": price_value, "url": link})
    return results

def fetch_vinted(search, max_price):
    url = f"https://www.vinted.co.uk/catalog?search_text={search.replace(' ','%20')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    for item in soup.select(".feed-grid__item"):
        title_elem = item.select_one(".feed-grid__item-title")
        price_elem = item.select_one(".feed-grid__item-price")
        link_elem = item.select_one("a")
        if title_elem and price_elem and link_elem:
            try:
                price_value = float(price_elem.text.replace("£","").strip())
            except:
                continue
            if price_value <= max_price:
                results.append({"title": title_elem.text.strip(), "price": price_value, "url": "https://www.vinted.co.uk" + link_elem["href"]})
    return results

# ----------------------
# Telegram alert
# ----------------------
async def send_alert(item, platform):
    message = (
        f"🚨 New Listing!\n"
        f"Platform: {platform}\n"
        f"{item['title']}\n"
        f"Price: £{item['price']}\n"
        f"{item['url']}"
    )
    await bot.send_message(chat_id=CHAT_ID, text=message)  # ✅ await fixes the warning

# ----------------------
# Main bot logic
# ----------------------
async def main():
    state = load_state()
    for item in items_to_watch:
        platform = item["platform"]
        search = item["search"]
        max_price = item["max_price"]

        if platform == "eBay":
            new_items = fetch_ebay(search, max_price)
        elif platform == "Depop":
            new_items = fetch_depop(search, max_price)
        elif platform == "Vinted":
            new_items = fetch_vinted(search, max_price)
        else:
            continue

        for listing in new_items:
            if listing["url"] not in state:
                await send_alert(listing, platform)
                state[listing["url"]] = True

    save_state(state)
    print(f"Checked all platforms. {len(state)} items tracked.")  # Optional debug print

# ----------------------
# Run in a loop every 5 minutes
# ----------------------
if __name__ == "__main__":
    while True:
        asyncio.run(main())
        time.sleep(300)  # wait 5 minutes

