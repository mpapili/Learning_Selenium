from part_hierarchy import part_hierarchy
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import StaleElementReferenceException
import this
import time


BUDGET = 875.0
CHROMIUM_LOCATION = '/usr/bin/chromium'
NAP_TIME = 0.25
# set up our web-driver to control chromium
this.driver = None
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
            print(f'found {elem_link} of type {type(element)}')
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
    print(f'found {filter_block} for filter!')
    labels = filter_block.find_elements_by_tag_name('label')
    for label in labels:
        # debug
        if label.text:
            print(label.text)
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


def buy_hard_drive(types: list, cap_search: str) -> dict:
    '''
    given types (ex: ['SSD', 'HDD'])
    and cap_search (ex: '1TB') find cheapest 
    option on pcpartpicker
    '''
    time.sleep(NAP_TIME*2)
    click_link_naturally('/products/internal-hard-drive/')
    time.sleep(NAP_TIME)
    apply_filter('t_set', types)
    time.sleep(NAP_TIME)
    input_search_text(this.driver, cap_search)
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
    # sort by price
    wt_cols = get_webtable_cols()
    wt_cols['Price'].click()
    time.sleep(NAP_TIME)
    return add_cheapest()


def buy_psu(make: list, efficiencies: list) -> dict:
    '''
    given makes (ex: ['Corsair, EVGA']) and
    given efficiencies (ex: ['80+ Gold', '80+']) 
    buy cheapest PSU
    '''

    time.sleep(NAP_TIME*2)
    click_link_naturally('/products/power-supply/')
    time.sleep(NAP_TIME)
    apply_filter('m_set', ['Corsair', 'EVGA', 'SeaSonic'])
    time.sleep(NAP_TIME)
    apply_filter('e_set', ['80+ Gold', '80+ Bronze'])
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
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--test-type')
    options.add_argument("--start-maximized")
    options.add_argument("--incognito")
    options.binary_location = CHROMIUM_LOCATION
    this.driver = webdriver.Chrome(chrome_options=options)

    parts_list = []

    # let's get PCPARTPICKER.COM
    this.driver.get('https://pcpartpicker.com/list/')
    time.sleep(NAP_TIME*2)
    # let's go to the cpu page, and search
    parts_list.append(buy_cpu(parts_dict['CPU']))
    # let's do a motherboard now
    parts_list.append(buy_motherboard('b450'))
    # memory!
    parts_list.append(buy_memory(
        ['DDR4-3000', 'DDR4-3200', 'DDR4-3600'], ['2 x 8GB']))
    # hard drive!
    parts_list.append(buy_hard_drive(['SSD'], '1TB'))
    # video card!
    #parts_list.append(buy_video_card(['Radeon RX 570', 'Radeon RX 580', 'GeForce GTX 1060', 'GeForce GTX 1660']))
    parts_list.append(buy_video_card(parts_dict['GPU']))
    # case (lol)
    parts_list.append(buy_case())
    # PSU
    parts_list.append(
        buy_psu(['Corsair', 'EVGA', 'SeaSonic'], parts_dict['PSU_EFFs']))
    return parts_list


if __name__ == '__main__':

    #this.hierarchy = dict(part_hierarchy)

    def recursive_buy():
        '''
        keep buying and stepping down in part_hierarchy
        until a build fits budget
        '''
        try:
            parts_dict = part_hierarchy.pop(0)
            #parts_dict = {'CPU': part_hierarchy['CPU'].pop(0)}
            parts_list = build_a_pc(parts_dict)
            # and what's the final cost?
            cost = calculate_cost(parts_list)
            print(parts_list)
            print(cost)
            if cost > BUDGET:
                recursive_buy()
        except NoPartFound:
            print("a part was not found, skipping...")
            recursive_buy()

    recursive_buy()
