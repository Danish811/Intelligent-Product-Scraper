import asyncio
from playwright.async_api import async_playwright
from urllib.parse import quote_plus

async def snapdeal_scraper(search_term: str):
    print("scraper called")
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)  # headless since no manual viewing needed
        page = await browser.new_page(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ))

        encoded_term = quote_plus(search_term)
        url = f"https://www.snapdeal.com/search?keyword={encoded_term}&sort=rlvncy"
        print(f"▶ Loading {url}")
        await page.goto(url, wait_until="domcontentloaded")

        await page.wait_for_selector("div.product-tuple-listing", timeout=30000)
        products = await page.query_selector_all("div.product-tuple-listing")
        results = []

        for product in products:
            if len(results) >= 3:
                print(f"3 results for {search_term}")
                break
            title_el = await product.query_selector("p.product-title")
            price_el = await product.query_selector("span.lfloat.product-price")
            discount_el = await product.query_selector("div.product-discount")
            link_el = await product.query_selector("a.dp-widget-link")
            img_el = await product.query_selector("img.product-image")

            title = (await title_el.inner_text()).strip() if title_el else None
            price = (await price_el.inner_text()).strip() if price_el else None
            discount = (await discount_el.inner_text()).strip() if discount_el else None
            link = (await link_el.get_attribute("href")).strip() if link_el else None
            img = (await img_el.get_attribute("src")) if img_el else None

            if link and not link.startswith("http"):
                link = "https://www.snapdeal.com" + link

            # Validate that all fields exist
            if all([title, price, discount, link, img]):
                results.append({
                    "title": title,
                    "price": price,
                    "discount": discount,
                    "link": link,
                    "image": img
                })

        await browser.close()
        return results

# Multi-keyword concurrent scraper with browser reuse
async def snapdeal_scraper_multi(keywords):
    results = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        pages = [await browser.new_page(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )) for _ in keywords]

        async def scrape(page, search_term):
            encoded_term = quote_plus(search_term)
            url = f"https://www.snapdeal.com/search?keyword={encoded_term}&sort=rlvncy"
            print(f"▶ Loading {url}")
            await page.goto(url, wait_until="domcontentloaded")
            await page.wait_for_selector("div.product-tuple-listing", timeout=30000)
            products = await page.query_selector_all("div.product-tuple-listing")
            res = []
            for product in products:
                if len(res) >= 3:
                    break
                title_el = await product.query_selector("p.product-title")
                price_el = await product.query_selector("span.lfloat.product-price")
                discount_el = await product.query_selector("div.product-discount")
                link_el = await product.query_selector("a.dp-widget-link")
                img_el = await product.query_selector("img.product-image")
                title = (await title_el.inner_text()).strip() if title_el else None
                price = (await price_el.inner_text()).strip() if price_el else None
                discount = (await discount_el.inner_text()).strip() if discount_el else None
                link = (await link_el.get_attribute("href")).strip() if link_el else None
                img = (await img_el.get_attribute("src")) if img_el else None
                if link and not link.startswith("http"):
                    link = "https://www.snapdeal.com" + link
                if all([title, price, discount, link, img]):
                    res.append({
                        "title": title,
                        "price": price,
                        "discount": discount,
                        "link": link,
                        "image": img
                    })
            return res

        tasks = [scrape(page, kw) for page, kw in zip(pages, keywords)]
        results_lists = await asyncio.gather(*tasks)
        await browser.close()
        # Flatten the results
        all_results = []
        for r in results_lists:
            all_results.extend(r)
        return all_results

# Example of how to call it
# if __name__ == "__main__":
#     async def test():
#         products = await snapdeal_scraper("laptop")
#         print(products)

#     asyncio.run(test())
