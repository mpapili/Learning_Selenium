# Following: https://pythonspot.com/selenium-click-button/

from selenium import webdriver
import time

CHROMIUM_LOCATION = '/usr/bin/chromium'

def what_can_i_do(obj) -> None:
	''' prints dir(object) line-by-line '''
	for attribute in dir(obj):
		print(attribute)


# set up our web-driver to control chromium
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--test-type')
options.binary_location = CHROMIUM_LOCATION
driver = webdriver.Chrome(chrome_options=options)
driver.get('https://python.org')

# get html source
html = driver.page_source
print(html)

# let's try and access the info from a text-box
text_area = driver.find_element_by_class_name('introduction')
print(type(text_area)) # so this gets us a WebElement object!
print(dir(text_area))
print(text_area.text) # it works!!!

# let's try and enter some text!
search_bar_input = driver.find_element_by_class_name('search-field')
search_bar_input.send_keys("Searching for something") # it types it!

# clicking is trickier, we need to find element by xpath!
search_bar_go_button = driver.find_element_by_class_name('search-button')
search_bar_go_button.click()

