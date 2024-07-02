from config import create_app #-Line 1
from celery import shared_task 

import logging
import requests

import os
import time
import pickle
import random
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidArgumentException
from selenium.common.exceptions import ElementClickInterceptedException

class Scraper:
	# This time is used when we are waiting for element to get loaded in the html
	wait_element_time = 30
	cookies_folder = 'cookies' + os.path.sep


	def __init__(self, url):
		self.url = url

		self.setup_driver_options()
		self.setup_driver()

	# Automatically close driver on destruction of the object
	def __del__(self):
		self.driver.close()

	def get_current_url(self):
		return self.driver.current_url
	# Add these options in order to make chrome driver appear as a human instead of detecting it as a bot
	# Also change the 'cdc_' string in the chromedriver.exe with Notepad++ for example with 'abc_' to prevent detecting it as a bot
	def setup_driver_options(self):
		self.driver_options = Options()

		arguments = [
			'--disable-blink-features=AutomationControlled'
		]

		experimental_options = {
			'excludeSwitches': ['enable-automation', 'enable-logging'],
			'prefs': {'profile.default_content_setting_values.notifications': 2, 
             		  "credentials_enable_service": False,
                      "profile.password_manager_enabled": False}
		}

		for argument in arguments:
			self.driver_options.add_argument(argument)

		for key, value in experimental_options.items():
			self.driver_options.add_experimental_option(key, value)

	# Setup chrome driver with predefined options
	def setup_driver(self):
		chrome_driver_path = ChromeDriverManager().install()
		self.driver = webdriver.Chrome(service=ChromeService(chrome_driver_path), options = self.driver_options)
		self.driver.get(self.url)
		self.driver.maximize_window()
  
    	# Check if cookie file exists
	def is_cookie_file(self):
		return os.path.exists(self.cookies_file_path)

	def load_cookies(self):
		# Load cookies from the file
		cookies_file = open(self.cookies_file_path, 'rb')
		cookies = pickle.load(cookies_file)
		
		for cookie in cookies:
			self.driver.add_cookie(cookie)

		cookies_file.close()

		self.go_to_page(self.url)
  
	def is_logged_in(self, wait_element_time = None):
		if wait_element_time is None:
			wait_element_time = self.wait_element_time

		return self.find_element(self.is_logged_in_selector, False, wait_element_time)

	# Save cookies to file
	def save_cookies(self):
		# Do not save cookies if there is no cookies_file name 
		if not hasattr(self, 'cookies_file_path'):
			return

		# Create folder for cookies if there is no folder in the project
		if not os.path.exists(self.cookies_folder):
			os.mkdir(self.cookies_folder)

		# Open or create cookies file
		cookies_file = open(self.cookies_file_path, 'wb')
		
		# Get current cookies from the driver
		cookies = self.driver.get_cookies()

		# Save cookies in the cookie file as a byte stream
		pickle.dump(cookies, cookies_file)

		cookies_file.close()


	def add_login_functionality(self, login_url, is_logged_in_selector, cookies_file_name):
		self.login_url = login_url
		self.is_logged_in_selector = is_logged_in_selector
		self.cookies_file_name = cookies_file_name + '.pkl'
		self.cookies_file_path = self.cookies_folder + self.cookies_file_name

		# Check if there is a cookie file saved
		if self.is_cookie_file():
			# Load cookies
			self.load_cookies()
			
			# Check if user is logged in after adding the cookies
			is_logged_in = self.is_logged_in(5)
			if is_logged_in:
				return
		
		# Wait for the user to log in with maximum amount of time 5 minutes
		print('Please login manually in the browser and after that you will be automatically loged in with cookies. Note that if you do not log in for five minutes, the program will turn off.')
		is_logged_in = self.is_logged_in(300)

		# User is not logged in so exit from the program
		if not is_logged_in:
			exit()

		# User is logged in so save the cookies
		self.save_cookies()
  
  
	# Wait random amount of seconds before taking some action so the server won't be able to tell if you are a bot
	def wait_random_time(self):
		random_sleep_seconds = round(random.uniform(1, 2), 2)

		time.sleep(random_sleep_seconds)

	# Goes to a given page and waits random time before that to prevent detection as a bot
	def go_to_page(self, page):
		# Wait random time before refreshing the page to prevent the detection as a bot
		self.wait_random_time()

		# Refresh the site url with the loaded cookies so the user will be logged in
		self.driver.get(page)
		time.sleep(5)
		self.scroll_down_and_back()
		time.sleep(2)
  

	def find_element(self, selector, exit_on_missing_element = True, wait_element_time = None):
		if wait_element_time is None:
			wait_element_time = self.wait_element_time

		# Intialize the condition to wait
		wait_until = EC.element_to_be_clickable((By.CSS_SELECTOR, selector))

		try:
			# Wait for element to load
			element = WebDriverWait(self.driver, wait_element_time).until(wait_until)
		except:
			if exit_on_missing_element:
				print('ERROR: Timed out waiting for the element with css selector "' + selector + '" to load')
				# End the program execution because we cannot find the element
				exit()
			else:
				return False

		return element

	def find_multiple_elements_by_xpath(self, xpath, index, exit_on_missing_element = True, wait_element_time = None):
		if wait_element_time is None:
			wait_element_time = self.wait_element_time

		# Intialize the condition to wait
		wait_until = EC.presence_of_all_elements_located((By.XPATH, xpath))

		try:
			# Wait for element to load
			elements = WebDriverWait(self.driver, wait_element_time).until(wait_until)
		except:
			if exit_on_missing_element:
				# End the program execution because we cannot find the element
				print('ERROR: Timed out waiting for the element with xpath "' + xpath + '" to load')
				exit()
			else:
				return False

		return elements[index]

	def find_element_by_xpath(self, xpath, exit_on_missing_element = True, wait_element_time = None):
		if wait_element_time is None:
			wait_element_time = self.wait_element_time

		# Intialize the condition to wait
		wait_until = EC.element_to_be_clickable((By.XPATH, xpath))

		try:
			# Wait for element to load
			element = WebDriverWait(self.driver, wait_element_time).until(wait_until)
		except:
			if exit_on_missing_element:
				# End the program execution because we cannot find the element
				print('ERROR: Timed out waiting for the element with xpath "' + xpath + '" to load')
				exit()
			else:
				return False

		return element

	# Wait random time before clicking on the element
	def element_click(self, selector, delay = True):
		if delay:
			self.wait_random_time()

		try:
			element = self.find_element(selector)
		except:
			print('ERROR: Timed out waiting for the element to load')
		if element: 
			element.click()

	# Wait random time before clicking on the element
	def element_click_by_xpath(self, xpath, delay = True):
		
     
		if delay:
			self.wait_random_time()
		try:
			element = self.find_element_by_xpath(xpath)
		except:
			print('ERROR: Timed out waiting for the element with xpath "' + xpath + '" to load')
		if element: 
			element.click()
	
	# Wait random time before sending the keys to the element
	def element_send_keys(self, selector, text, delay = True):
		if delay:
			self.wait_random_time()

		element = self.find_element(selector)

		try:
			element.click()
		except ElementClickInterceptedException:
			self.driver.execute_script("arguments[0].click();", element)
		self.wait_random_time()
		element.send_keys(text)

	# Wait random time before sending the keys to the element
	def element_send_keys_by_xpath(self, xpath, text, delay = True):
		if delay:
			self.wait_random_time()

		element = self.find_element_by_xpath(xpath)

		try:
			element.click()
		except ElementClickInterceptedException:
			self.driver.execute_script("arguments[0].click();", element)
		
		element.send_keys(text)

	def input_file_add_files(self, selector, files):
		# Intialize the condition to wait
		wait_until = EC.presence_of_element_located((By.CSS_SELECTOR, selector))

		try:
			# Wait for input_file to load
			input_file = WebDriverWait(self.driver, self.wait_element_time).until(wait_until)
		except:
			print('ERROR: Timed out waiting for the input_file with selector "' + selector + '" to load')
			# End the program execution because we cannot find the input_file
			exit()

		self.wait_random_time()

		try:
			input_file.send_keys(files)
		except InvalidArgumentException:
			print('ERROR: Exiting from the program! Please check if these file paths are correct:\n' + files)
			exit()
   
	def scroll_down_and_back(self):
		document_height = self.driver.execute_script("return document.body.scrollHeight")
		# Scroll down 100 pixels every 0.25 seconds
		for i in range(0, document_height, 100):
			self.driver.execute_script(f"window.scrollBy(0, {min(100, document_height - i)});")
			time.sleep(0.1)

		for i in range(document_height, 0, -100):
			self.driver.execute_script(f"window.scrollBy(0, -{min(100, i)});")
			time.sleep(0.1)
  
	def scroll_to_element(self, selector):
		element = self.find_element(selector)

		self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)

	def scroll_to_element_by_xpath(self, xpath):
		element = self.find_element_by_xpath(xpath)

		self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
  
	def element_delete_text(self, selector, delay = True):
			if delay:
				self.wait_random_time()

			element = self.find_element(selector)
			
			# Select all of the text in the input
			element.send_keys(Keys.LEFT_SHIFT + Keys.HOME)
			# Remove the selected text with backspace
			element.send_keys(Keys.BACK_SPACE)

def generate_multiple_images_path(path, images):
	# Last character must be '/' because after that we are adding the name of the image
	if path[-1] != '/':
		path += '/'

	images_path = ''

	# Split image names into array by this symbol ";"
	image_names = images.split(';')

	# Create string that contains all of the image paths separeted by \n
	if image_names:
		for image_name in image_names:
			# Remove whitespace before and after the string
			image_name = image_name.strip()

			# Add "\n" for indicating new file
			if images_path != '':
				images_path += '\n'

			images_path += path + image_name

	return images_path
############################################################
flask_app = create_app() 
celery_app = flask_app.extensions["celery"] 

scraper = Scraper('https://facebook.com')
scraper.add_login_functionality('https://facebook.com', 'svg[aria-label="Your profile"]', 'facebook')
scraper.go_to_page('https://facebook.com/marketplace/you/selling')



logger = logging.getLogger(__name__)

def confirm_updating_item(id):
	response = requests.get(f'http://localhost:5000/main_app/facebook_bot/confirm_update/{id}')
	logger.info(f"Confirming updating item {id} is successfully with response: {response}")
 
def confirm_deleting_item(id):
	response = requests.get(f'http://localhost:5000/main_app/facebook_bot/confirm_delete/{id}')
	logger.info(f"Confirming deleting item {id} is successfully with response: {response}")
 
def confirm_creating_item(id):
	response = requests.get(f'http://localhost:5000/main_app/facebook_bot/confirm_create/{id}')
	logger.info(f"Confirming creating item {id} is successfully with response: {response}")


@shared_task(name='tasks.update_item', bind=True) 
def update_item(self, item):
    scraper.go_to_page('https://www.facebook.com/marketplace/you/selling')

    scraper.element_delete_text('input[aria-label="Search your listings"]')
    scraper.element_send_keys('input[aria-label="Search your listings"]', item['Name'])
    time.sleep(1)
    
    scraper.element_click('div[aria-label="More"]')
    scraper.element_click_by_xpath('//span[text()="Edit listing"]')   
    time.sleep(5)
    
    scraper.element_delete_text('label[aria-label="Price"] input')
    scraper.element_send_keys('label[aria-label="Price"] input', item['Price'])
    time.sleep(1)
    
    scraper.scroll_to_element('label[aria-label="Category"]')
    time.sleep(1)
    
    scraper.element_click('label[aria-label="Condition"]')
    scraper.element_click_by_xpath(f'//div[@aria-selected]/div/div/div/span[text()="{item["Condition"]}"]')
    time.sleep(1)
    
    scraper.scroll_to_element('input[aria-label="Location"]')
    time.sleep(1)
    
    scraper.element_delete_text('input[aria-label="Location"]')
    scraper.element_send_keys('input[aria-label="Location"]', item['Location'])
    time.sleep(1)
    
    scraper.find_multiple_elements_by_xpath('//ul[@aria-label="5 suggested searches"]/li', 0).click()
    scraper.element_click('div[aria-label="Update"]')
    
    time.sleep(5)
    logger.info(scraper.get_current_url().split("=")[-1])
    id = 1111111111 #TODO
    try:
        confirm_updating_item(id)
    except:
        logger.error(f"Failed to confirm updating of item {id}")
        

@shared_task(name='tasks.delete_item', bind=True) 
def delete_item(self, item):
	scraper.go_to_page('https://www.facebook.com/marketplace/you/selling')

	scraper.element_delete_text('input[aria-label="Search your listings"]')
	scraper.element_send_keys('input[aria-label="Search your listings"]', item['Name'])
	time.sleep(2)

	scraper.element_click('div[aria-label="More"]')
	scraper.element_click_by_xpath('//span[text()="Delete listing"]')   
	time.sleep(1)
	
	scraper.find_element_by_xpath('//div[@aria-label="Cancel"]/parent::div/parent::div').find_elements(By.XPATH, '*')[0].click()
	
	if scraper.find_element('div[aria-label="Next"]', False):
		scraper.element_click('div[aria-label="Next"]')
		
	time.sleep(5)
	id = 11111 #TODO
	try:
		confirm_deleting_item(id)
	except:
		logger.error(f"Failed to confirm deleting of item {item['Id']}")			

@shared_task(name='tasks.create_item', bind=True) 
def create_item(self, item):
	scraper.go_to_page('https://www.facebook.com/marketplace/you/selling')

	scraper.element_click('div[aria-label="Marketplace sidebar"] a[aria-label="Create new listing"]')
	scraper.element_click('a[href="/marketplace/create/item/"]')

	images_path = generate_multiple_images_path(item['Photos Folder'], item['Photos Names'])
	scraper.input_file_add_files('input[accept="image/*,image/heif,image/heic"]', images_path)
 
	scraper.element_send_keys('label[aria-label="Title"] input', item['Title'])
	scraper.element_send_keys('label[aria-label="Price"] input', item['Price'])

	scraper.scroll_to_element('label[aria-label="Category"]')
	scraper.element_click('label[aria-label="Category"]')
	scraper.element_click_by_xpath('//span[text()="' + item['Category1'] + '"]')

	scraper.element_click('label[aria-label="Condition"]')
	scraper.element_click_by_xpath('//span[text()="' + item['Condition'] + '"]')

	scraper.element_send_keys('label[aria-label="Description"] textarea', item['Description'])
 
	next_button_selector = 'div [aria-label="Next"] > div'
	next_button = scraper.find_element(next_button_selector, False, 3)
	if not next_button.get_attribute('aria-disabled'):
		scraper.element_click(next_button_selector)
		scraper.element_click('div[aria-label="Publish"]:not([aria-disabled])')
	else: 
		save_draft_button = 'div [aria-label="Save draft"] > div'
		scraper.element_click(save_draft_button)
		scraper.go_to_page("https://facebook.com/marketplace/you/selling")
	time.sleep(5)
	id = 1111111111 #TODO get the id
	try:
		confirm_creating_item(id)
	except:
		logger.error(f"Failed to confirm creating of item {item['Title']}")			
