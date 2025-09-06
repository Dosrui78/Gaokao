from DrissionPage import ChromiumPage, Chromium
from loguru import logger

logger.info("starting")
browser = ChromiumPage()
page = browser.latest_tab
page.get('https://www.baidu.com')

logger.info(page.title)
logger.info(page.url)
logger.info("begin to wait ...")
page.wait(10)
