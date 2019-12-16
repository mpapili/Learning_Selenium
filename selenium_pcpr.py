import argparse
from part_hierarchy import gamer_hierarchy, part_hierarchy
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import StaleElementReferenceException
import sys
import this
import time


BUDGET = 1000.0
WIGGLE = 30
CHROMIUM_LOCATION = '/usr/bin/chromium'
NAP_TIME = 0.25 # base time to sleep 
# set up our web-driver to control chromium
this.driver = None
this.args = None
#this.hierarchy = None


class NoPartFound(Exception):
    print("no part found!")


def what_can_i_do(obj) -> None:
    ''' prints dir(object) line-by-line '''
    for attribute in dir(obj):
        print(attribute)


def find_element_for_link(elements: list, link: str) -> WebElement:
    '''
    given a link as a string, returns the WebElement
    that contains that link from a list of WebElements
    '''
    for element in elements:

        elem_link = element.get_attribute('href')

        if elem_link and link in elem_link:
            return element


def input_search_text(driver, s_text: str) -> None:
    '''
    given search text as a string, 
    search on the PCPR part gridview screen
    '''
    search = driver.find_element_by_id('part_category_search')
    search.send_keys(f'{s_text}\n')


def click_link_naturally(link: str):
    '''
    given a link on current page, locate and 
    click on it
    '''
    links = extract_links()
    button = find_element_for_link(links, link)
    this.driver.execute_script("arguments[0].click();", button)


def extract_links() -> list:
    '''
    returns list of WebElements that are links
    '''
    return [link for link in this.driver.find_elements_by_xpath('.//a')]


def get_webtable_cols() -> dict:
    '''
    return list of column elements for webtable
    '''
    wt_cols = {}

    part_table = this.driver.find_element_by_xpath(
        "//table[@id='paginated_table']")
    title_row = part_table.find_elements_by_tag_name("tr")[0]
    cols = title_row.find_elements_by_tag_name("th")

    for col in cols:

        try:
            divs = col.find_elements_by_class_name("tablesorter-header-inner")
            for div in divs:

                try:
                    col_text = div.find_elements_by_tag_name("p")[0]
                    if col_text.text not in wt_cols.keys():
                        wt_cols[col_text.text] = col

                except IndexError:
                    pass

        except IndexError:
            pass  # not all cols have divs with that header
    return wt_cols


def add_cheapest() -> dict:
    '''
    returns dict of {'name': 'prod_name', 'price': float}
    and adds product
    '''
    part_table = this.driver.find_element_by_xpath(
        "//table[@id='paginated_table']")
    product_rows = part_table.find_elements_by_tag_name("tr")

    for product in product_rows:

        name = None
        price = None

        cols = part_table.find_elements_by_tag_name("td")
        for col in cols:
            try:
                className = (col.get_attribute('class'))
                if className == 'td__name':
                    name = col.text
                elif className == 'td__price':
                    price = float(col.text.rstrip('Add').lstrip("$"))

                if name and price:

                    print(f'{name}: {price}')
                    # time to add!
                    button = col.find_element_by_tag_name("button")
                    button.click()
                    return {'name': name, 'price': price}

            except StaleElementReferenceException:
                pass  # noticing lots of stale elements?


def apply_filter(filter_id: str, valid_elements: list) -> None:
    '''
    given a filter_id (ex: 'filterdiv_s') and valid list of 
    elements, check off those elements in the filter list
    '''
    filter_block = this.driver.find_element_by_id(filter_id)  # "Speed"
    labels = filter_block.find_elements_by_tag_name('label')
    for label in labels:

        if label.text and label.text in valid_elements:
            label.click()
            time.sleep(NAP_TIME/2)


def buy_cpu(cpu_model: str) -> dict:
    '''
    given cpu_model (ex: "Ryzen 5 2600") search for 
    cheapest option on pcpartpicker
    '''
    click_link_naturally('/products/cpu/')
    input_search_text(this.driver, cpu_model)  # let's get a ryzen 2600
    # get webtable cols
    wt_cols = get_webtable_cols()
    # sort by price
    time.sleep(NAP_TIME)
    wt_cols['Price'].click()
    time.sleep(NAP_TIME)
    # let's get the full big table now to find the price and add-button
    part = add_cheapest()
    if part != None:
        return part
    else:
        raise NoPartFound()


def buy_motherboard(mobo_model: str) -> dict:
    '''
    given mobo_model (ex: "b450") search for 
    cheapest option on pcpartpicker
    '''
    time.sleep(NAP_TIME*2)
    click_link_naturally('/products/motherboard/')
    input_search_text(this.driver, mobo_model)  # let's get a ryzen 2600
    # sort by price
    time.sleep(NAP_TIME)
    wt_cols = get_webtable_cols()
    wt_cols['Price'].click()
    time.sleep(NAP_TIME)
    return add_cheapest()


def buy_memory(freqs: list, capacities: list) -> dict:
    '''
    given freqs (ex: ['DDR4-3000', 'DDR4-3200'])
    and capacity (ex: ['2 x 8GB']) find cheapest 
    option on pcpartpicker
    '''
    time.sleep(NAP_TIME*2)
    click_link_naturally('/products/memory/')
    time.sleep(NAP_TIME)
    apply_filter('filterdiv_s', freqs)
    time.sleep(NAP_TIME)
    apply_filter('filterdiv_Z', capacities)
    time.sleep(NAP_TIME)
    wt_cols = get_webtable_cols()
    wt_cols['Price'].click()
    time.sleep(NAP_TIME)
    return add_cheapest()


def buy_hard_drive(types: list, min_capacity: str) -> dict:
    '''
    given types (ex: ['SSD', 'HDD'])
    and min_capacity in GB (ex: '1000') find cheapest 
    option on pcpartpicker
    '''
    time.sleep(NAP_TIME*2)
    click_link_naturally('/products/internal-hard-drive/')
    time.sleep(NAP_TIME)
    apply_filter('m_set', ['Intel', 'Samsung', 'Seagate', 'Western Digital'])
    time.sleep(NAP_TIME)
    apply_filter('t_set', types)
    time.sleep(NAP_TIME)

    # minimum capacity
    capacity_div = this.driver.find_element_by_id("filter_slide_left_A")
    capacity_div.click()
    capacity_min_box = capacity_div.find_element_by_tag_name("input")
    capacity_min_box.send_keys(f"{min_capacity}\n")
    time.sleep(NAP_TIME)

    time.sleep(NAP_TIME)
    # sort by price
    wt_cols = get_webtable_cols()
    wt_cols['Price'].click()
    time.sleep(NAP_TIME)
    return add_cheapest()


def buy_video_card(chipsets: list) -> dict:
    '''
    given chipsets (ex: ['Radeon RX 570', 'Radeon RX 580'])
    buy the cheapest option on pcpartpicker
    '''
    time.sleep(NAP_TIME*2)
    click_link_naturally('/products/video-card/')
    time.sleep(NAP_TIME)
    apply_filter('c_set', chipsets)
    time.sleep(NAP_TIME)
    # sort by price
    wt_cols = get_webtable_cols()
    wt_cols['Price'].click()
    time.sleep(NAP_TIME)
    return add_cheapest()


def buy_case() -> dict:
    '''
    buy a case.
    '''
    time.sleep(NAP_TIME*2)
    click_link_naturally('/products/case/')
    time.sleep(NAP_TIME)
    apply_filter('t_set', ['MicroATX Mid Tower', 'ATX Mid Tower'])
    time.sleep(NAP_TIME)
    # sort by price
    wt_cols = get_webtable_cols()
    wt_cols['Price'].click()
    time.sleep(NAP_TIME)
    return add_cheapest()


def buy_psu(makes: list, efficiencies: list, watt_min: str) -> dict:
    '''
    given makes (ex: ['Corsair, EVGA']) and
    given efficiencies (ex: ['80+ Gold', '80+']) and
    given watt_min (ex: "650")
    buy cheapest PSU
    '''

    time.sleep(NAP_TIME*2)
    click_link_naturally('/products/power-supply/')
    time.sleep(NAP_TIME)
    apply_filter('m_set', makes)
    time.sleep(NAP_TIME)
    apply_filter('e_set', efficiencies)
    wattage_div = this.driver.find_element_by_id("filter_slide_left_A")
    wattage_div.click()
    wattage_min_box = wattage_div.find_element_by_tag_name("input")
    wattage_min_box.send_keys(f"{watt_min}\n")
    time.sleep(NAP_TIME)
    # sort by price
    wt_cols = get_webtable_cols()
    wt_cols['Price'].click()
    time.sleep(NAP_TIME)
    return add_cheapest()


def calculate_cost(parts_list: list) -> float:
    '''
    given a parts_list (ex: [{'name': 'part', 'price': 23.45}])
    return the sum of all prices
    '''
    total = 0
    for part in parts_list:
        total += part['price']
    return total


def build_a_pc(parts_dict: dict) -> list:
    '''
    build a PC! (to be used recursively!)
    '''
    set_webdriver()
    parts_list = []

    # let's get PCPARTPICKER.COM
    this.driver.get('https://pcpartpicker.com/list/')
    time.sleep(NAP_TIME*2)

    if this.args.country:
        switch_country(args.country)
 
    # let's go to the cpu page, and search
    parts_list.append(buy_cpu(parts_dict['CPU']))
    if calculate_cost(parts_list) > BUDGET + WIGGLE:
        return False

    # let's do a motherboard now
    parts_list.append(buy_motherboard(parts_dict['MOBO']))
    if calculate_cost(parts_list) > BUDGET + WIGGLE:
        return False

    # memory!
    parts_list.append(buy_memory(['DDR4-3000', 'DDR4-3200', 'DDR4-3600'], parts_dict['MEMORY_CONFIG']))
    if calculate_cost(parts_list) > BUDGET + WIGGLE:
        return False

    # hard drive!
    parts_list.append(buy_hard_drive(['SSD'], '1000'))
    if calculate_cost(parts_list) > BUDGET:
        return False

    # video card!
    parts_list.append(buy_video_card(parts_dict['GPU']))
    if calculate_cost(parts_list) > BUDGET + WIGGLE:
        return parts_list

    # case
    parts_list.append(buy_case())
    if calculate_cost(parts_list) > BUDGET + WIGGLE:
        return False

    # PSU
    parts_list.append(
        buy_psu(['Corsair', 'EVGA', 'SeaSonic'], parts_dict['PSU_EFFs'], parts_dict['PSU_WATT_MIN']))
    if calculate_cost(parts_list) > BUDGET + WIGGLE:
        return False

    # any wiggle room?
    cost = calculate_cost(parts_list)
    if BUDGET - cost > 50:
        # add an HDD!
        parts_list.append(buy_hard_drive(['7200RPM'], '2800'))
        cost = calculate_cost(parts_list)

    permalink = get_permalink()

    if BUDGET - cost > 100 and len(parts_dict['GPU']) > 1:
        # more GPU!

        old_list = parts_list
        old_permalink = permalink
        new_parts_dict = parts_dict['GPU'].pop()
        new_list = build_a_pc(parts_dict) # rebuild with better gpu

        if new_list:
            new_cost = calculate_cost(new_list)
            if new_cost < BUDGET + WIGGLE:
                return new_list
            else:
                print(f'\ngoing to be doing get() on {old_permalink}')
                this.driver.get(old_permalink)

    return parts_list


def get_permalink() -> str:
    '''
    returns permalink from site
    '''
    time.sleep(NAP_TIME*4)
    action_box = this.driver.find_element_by_class_name("actionBox__wrapper")
    permalink_elems = action_box.find_elements_by_tag_name("input")

    for element in permalink_elems:
        permalink = element.get_attribute('value')
        if permalink:
            return permalink


def set_webdriver() -> None:
    '''
    resets this.webdriver
    '''
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--test-type')
    options.add_argument("--start-maximized")
    options.add_argument("--incognito")
    options.binary_location = CHROMIUM_LOCATION
    this.driver = webdriver.Chrome(chrome_options=options)


def switch_country(country: str) -> None:
    '''
    given a country (example: "Canada")
    switches pcpartpicker site to that country's locale
    '''
    country_selector = this.driver.find_element_by_class_name("country-selector")
    country_selector.click()
    country_list = country_selector.find_element_by_id("country_select")
    countries = country_list.find_elements_by_tag_name("option")
    for country_name in countries:
        if country_name.text.lower() == country.lower():
            country_name.click()
            break
    time.sleep(NAP_TIME*2) # let page load


if __name__ == '__main__':


    def recursive_buy():
        '''
        keep buying and stepping down in part_hierarchy
        until a build fits budget
        '''
        try:
            parts_dict = part_hierarchy.pop(0)
            #parts_dict = {'CPU': part_hierarchy['CPU'].pop(0)}
            parts_list = build_a_pc(parts_dict)
            if parts_list:
                # and what's the final cost?
                cost = calculate_cost(parts_list)
                print(parts_list)
                print(cost)
                if cost > (BUDGET+WIGGLE):
                    recursive_buy()
            else:
                recursive_buy()
        except NoPartFound:
            print("a part was not found, skipping...")
            recursive_buy()
        return parts_list, cost


    # MAIN
    parser = argparse.ArgumentParser()
    parser.add_argument("--budget", help="max budget for build")
    parser.add_argument("--build_type", help="type of build ('ex: gaming')")
    parser.add_argument("--country", help="country ('ex: 'Canada')")
    args = parser.parse_args()
    this.args = args

    if args.budget:
        BUDGET = float(args.budget)
        print(f'budget was set to {BUDGET}')

    if args.build_type and args.build_type == 'gaming':
        # switch to an alternate hierarchy for gaming rigs
        part_hierarchy = gamer_hierarchy 

    parts_list, cost = recursive_buy()

    if BUDGET - cost > 50:
        # add an HDD!
        parts_list.append(buy_hard_drive(['7200RPM'], '2800'))
