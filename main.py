from utils import get_card_lists, scrape_website, sort_market_prices, append_console_to_txt
import time
from CardList import CardList

if __name__ == '__main__':

    card_lists = get_card_lists('lists.yaml')
    for split_lists in card_lists:
        this_list = CardList(card_lists[split_lists]['path'], split_lists)
        data = this_list.get_yaml_data()
        name = this_list.get_list_name()
        file_path = scrape_website(data,name)
        sort_market_prices('sorted_pricing/market_prices.yaml')
        sort_market_prices('sorted_pricing/lowest_prices.yaml')
        sort_market_prices('sorted_pricing/last_sold.yaml')
        append_console_to_txt(file_path)
        time.sleep(5)



# TODO
# Requirements
# invidiaul lists
# individual consoles (to allow for multi processing)


# mysql table
# data calculations, graph creations