from datetime import datetime
from bs4 import BeautifulSoup
import time
import prettytable
import yaml
# from prettytable import PLAIN_COLUMNS
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

base_url = 'https://store.tcgplayer.com/admin/product/manage/'
current_date = str(datetime.date(datetime.now()))
current_year_full = datetime.now().strftime('%Y')  # 2018
current_month = datetime.now().strftime('%m')  # 02 //This is 0 padded
current_month_text = datetime.now().strftime('%h')  # Feb
current_day = datetime.now().strftime('%d')  # // 23 //This is also padded


def scrape_website(card_data_yaml, list_name, browser):
    delete_console_txt()
    start = time.time()
    file_path = ''

    # first = True
    timer = 10
    lowest_listed_price_total = 0
    last_sold_price_total = 0
    market_price_total = 0
    for card in card_data_yaml:
        url = '{}{}'.format(base_url, card_data_yaml[card]['url'])
        condition_edition = card_data_yaml[card]['edition']
        card_quantity = card_data_yaml[card]['qty']
        browser.get(url)

        try:
            WebDriverWait(browser, timer).until(EC.presence_of_element_located((By.ID, 'ProductsTable')))
            no_table = False
        except:
            output_to_txt_console('Timeout No Results for: {}'.format(card))
            no_table = True

        if no_table:
            continue  # increments to the next element in for loop.

        # time.sleep(2)
        html = browser.page_source
        soup = BeautifulSoup(html, 'html.parser')
        for script in soup(['script', 'style']):
            script.extract()

        text_only = extract_text_only(soup, condition_edition)  # data table with the prices we want to extract
        data_prices = extract_data_prices(text_only, card)  # List[] 0 = Lowest listing, 1 = Last Sold, 2 = Market Price

        lowest_listed_price_total += (data_prices[0] * card_quantity)
        last_sold_price_total += (data_prices[1] * card_quantity)
        market_price_total += (data_prices[2] * card_quantity)

        price_yaml_generator(card, data_prices[0], 'sorted_pricing/lowest_prices.yaml')
        price_yaml_generator(card, data_prices[1], 'sorted_pricing/last_sold.yaml')
        price_yaml_generator(card, data_prices[2], 'sorted_pricing/market_prices.yaml')

        my_table = create_pretty_table(data_prices)
        # my_table.set_style(PLAIN_COLUMNS)
        file_path = output_to_txt(card, my_table, card_quantity, condition_edition, list_name)

    output_to_txt_console('Sum of Lowest Listed: ${:,.2f}'.format(lowest_listed_price_total))
    output_to_txt_console('Sum of Last Sold Prices: ${:,.2f}'.format(last_sold_price_total))
    output_to_txt_console('Sum of Market Prices: ${:,.2f}'.format(market_price_total))
    done = time.time()
    print(done - start)
    return file_path, [lowest_listed_price_total, last_sold_price_total, market_price_total]


def price_yaml_generator(card_name, price, yaml_name):
    with open(yaml_name, 'r') as stream:
        current_yaml = yaml.load(stream)
        current_yaml.update({card_name: price})

    with open(yaml_name, 'w') as stream:
        yaml.safe_dump(current_yaml, stream)

    return 0


def delete_console_txt():
    console = 'sorted_pricing/console.txt'
    with open(console, 'w') as f:
        f.write('')


def output_to_txt_console(string):
    print(string)
    txt_console = 'sorted_pricing/console.txt'
    with open(txt_console, 'a') as my_file:
        my_file.write(string + '\n')


def output_to_txt(card_name, my_table, card_quantity, condition_edition, list_name):
    yaml_name = list_name + '-' + current_date + '.txt'
    directory = 'full_listings/{0}/{1}-{2}/{3}'.format(current_year_full,
                                                       current_month,
                                                       current_month_text,
                                                       current_day)
    try:
        os.makedirs(directory)
    except FileExistsError:
        pass  # directory already exists

    full_listing_file_path = 'full_listings/{0}/{1}-{2}/{3}/{4}'.format(current_year_full,
                                                                        current_month,
                                                                        current_month_text,
                                                                        current_day, yaml_name)
    with open(full_listing_file_path, 'a') as my_file:
        my_file.write('{0} [{1}] - {2}\n'.format(card_name, card_quantity, condition_edition))
        my_file.write(str(my_table) + '\n\n')
        return full_listing_file_path


def create_pretty_table(data_prices):
    my_table = prettytable.PrettyTable(['TCG Lowest', 'TCG Last Sold', 'TCG Market Price'])
    my_table.add_row([data_prices[0], data_prices[1], data_prices[2]])
    return my_table


def extract_data_prices(price_table, card):
    data_list = []
    num_dollar_sign = 1
    for character_index in range(0, len(price_table)):
        if price_table[character_index] == '-':
            if num_dollar_sign == 1:
                output_to_txt_console('Missing [0] TCG Lowest for:    {}'.format(card))
            if num_dollar_sign == 3:
                output_to_txt_console('Missing [1] TCG Last Sold for: {}'.format(card))
            if num_dollar_sign == 5:
                output_to_txt_console('Missing [2] Market Price for:  {}'.format(card))
            data_list.append(0)
            num_dollar_sign += 2
        if price_table[character_index] == '$':
            if num_dollar_sign == 1 or num_dollar_sign == 3 or num_dollar_sign == 5:
                data_list.append(dollar_string_to_int(price_table[character_index:character_index + 5].split('.')[0]))
            num_dollar_sign += 1
        if num_dollar_sign > 5:
            return data_list
    return data_list


def get_card_lists(yaml_name):
    with open(yaml_name, 'r') as stream:
        try:
            card_lists = yaml.safe_load(stream)
        except yaml.YAMLError:
            pass
        return card_lists


def extract_text_only(input_html, edition):
    # Extracts data table starting from edition
    # lowest listing (1st dollar), last sold listing (3rd dollar), market price( 5th dollar)
    start = edition  # First word before price table
    end = 'Browsing as Yuginag'  # Last word of page
    text_only = input_html.get_text()
    text_only = text_only.strip('\n')
    text_only = text_only.strip('')
    text_only = text_only.replace('\n', ' ')
    text_only = text_only.replace('  ', ' ')
    try:
        text_only = text_only.split(start)[1]
    except IndexError:
        print(text_only)
    try:
        text_only = text_only.split(end)[0]
    except IndexError:
        print(text_only)
    return text_only


def dollar_string_to_int(dollar_string):
    dollar_string = dollar_string.replace('$', '')
    return int(dollar_string)


def sort_market_prices(yaml_name, name):
    with open(yaml_name, 'r') as stream:
        try:
            yaml_data = yaml.safe_load(stream)
            card_list = list()
            for cards in yaml_data:
                card_list.append(cards)
        except yaml.YAMLError:
            pass
    yaml_data = yaml_data

    prices_sorted = {k: v for k, v in sorted(yaml_data.items(), key=lambda x: x[1], reverse=True)}

    my_table = prettytable.PrettyTable(['Card', 'Price'])

    for card in prices_sorted:
        my_table.add_row([card, prices_sorted[card]])

    sorted_yaml = yaml_name.replace('.yaml', '') + '_sorted.txt'
    with open(sorted_yaml, 'a') as my_file:
        my_file.write(str(name) + ' - ' + str(current_date) + '\n')
        my_file.write(str(my_table) + '\n')
    delete_yaml_contents(yaml_name)
    return 0


def delete_yaml_contents(yaml_name):
    test_dict = {'test': 0}
    with open(yaml_name, 'w') as stream:
        yaml.safe_dump(test_dict, stream)


def append_console_to_txt(path):
    console = 'sorted_pricing/console.txt'
    with open(console, 'r') as console:
        console_data = console.read()
    with open(path, 'r') as original:
        data = original.read()
    with open(path, 'w') as modified:
        modified.write(console_data + "\n" + data)
    delete_console_txt()


def sum_total_prices(current_sums, list_of_sums):
    current_sums[0] = current_sums[0] + list_of_sums[0]  # Lowest
    current_sums[1] = current_sums[1] + list_of_sums[1]  # Last
    current_sums[2] = current_sums[2] + list_of_sums[2]  # Market
    return current_sums


def print_sums(sums):
    print('Sum of Lowest: {}'.format(sums[0]))
    print('Sum of Last: {}'.format(sums[1]))
    print('Sum of Market: {}'.format(sums[2]))
    print('[{}, {}, {}]'.format(human_format(sums[0]), human_format(sums[1]), human_format(sums[2])))


def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:.1f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])
