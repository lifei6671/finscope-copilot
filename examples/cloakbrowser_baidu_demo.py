import json
from pathlib import Path

from cloakbrowser import launch
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


TARGET_URL = "https://finance.baidu.com/stock/ab-601138"
CANDLESTICK_API_URL = "https://finance.pae.baidu.com/sapi/v1/get_candlestick_event"
CANDLESTICK_PARAMS = {
    "financeType": "stock",
    "code": "601138",
    "market": "ab",
    "period": "dayK",
    "activeType": "active",
    "finClientType": "pc",
}


def main() -> None:
    screenshot_path = Path("artifacts") / "baidu-stock-601138.png"
    data_path = Path("artifacts") / "baidu-stock-601138-candlestick-event.json"
    screenshot_path.parent.mkdir(parents=True, exist_ok=True)

    # `headless=False` 方便学习时直接观察浏览器行为。
    browser = launch(headless=False, humanize=True, locale="zh-CN", timezone="Asia/Shanghai")

    try:
        page = browser.new_page()
        page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60_000)
        page.wait_for_selector("body", timeout=15_000)

        candlestick_response = page.context.request.get(
            CANDLESTICK_API_URL,
            params=CANDLESTICK_PARAMS,
            headers={"Referer": TARGET_URL},
            timeout=60_000,
            fail_on_status_code=True,
        )
        candlestick_data = candlestick_response.json()
        data_path.write_text(
            json.dumps(candlestick_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"K线接口状态码: {candlestick_response.status}")
        print(f"K线接口地址: {candlestick_response.url}")
        print(f"K线数据已保存到: {data_path}")

        try:
            page.locator("text=工业富联").first.wait_for(timeout=15_000)
            print("已检测到目标股票名称：工业富联")
        except PlaywrightTimeoutError:
            print("未等到“工业富联”文本，继续输出当前页面信息。")

        print(f"页面标题: {page.title()}")
        print(f"当前地址: {page.url}")

        try:
            page.screenshot(path=str(screenshot_path), full_page=False, timeout=10_000)
            print(f"截图已保存到: {screenshot_path}")
        except PlaywrightTimeoutError:
            print("截图超时，已跳过；K线数据已经成功保存。")

        # 给你留一点观察时间，学习时更方便。
        page.wait_for_timeout(5_000)
    finally:
        browser.close()


if __name__ == "__main__":
    main()
