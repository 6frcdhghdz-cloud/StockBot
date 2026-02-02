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
    message = f"🚨 New Listing!\nPlatform: {platform}\n{item['title']}\nPrice: £{item['price']}\n{item['url']}"
    await bot.send_message(chat_id=CHAT_ID, text=message)

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
        elif platfo
