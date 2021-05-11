from utils import get_card_lists, scrape_website, sort_market_prices, append_console_to_txt
from CardList import CardList
from selenium import webdriver
import time


url = 'https://store.tcgplayer.com/admin/product/manage/33224'

if __name__ == '__main__':
    browser = webdriver.Chrome(
        executable_path=r'C:\Users\Richard Le\IdeaProjects\SellerPortalDatabase\chromedriver.exe')
    browser.get(url)
    filler_char = input("Enter any key after login captcha: ")

    card_lists = get_card_lists('lists.yaml')
    for split_lists in card_lists:
        this_list = CardList(card_lists[split_lists]['path'], split_lists)
        data = this_list.get_yaml_data()
        name = this_list.get_list_name()
        file_path = scrape_website(data, name, browser)
        sort_market_prices('sorted_pricing/market_prices.yaml', name)
        sort_market_prices('sorted_pricing/lowest_prices.yaml', name)
        sort_market_prices('sorted_pricing/last_sold.yaml', name)
        append_console_to_txt(file_path)
        time.sleep(1)
    browser.quit()

# TODO
# individual consoles (to allow for multi processing)

# mysql table
# data calculations, graph creations
