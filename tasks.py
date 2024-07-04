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
from utils import generate_multiple_images_path, update_price, update_condition, update_location
from helpers.scraper import Scraper

############################################################
logger = logging.getLogger(__name__)

flask_app = create_app() 
celery_app = flask_app.extensions["celery"] 

scraper = Scraper('https://facebook.com')
scraper.add_login_functionality('https://facebook.com', 'svg[aria-label="Your profile"]', 'facebook')
scraper.go_to_page('https://facebook.com/marketplace/you/selling')


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
    scraper.element_send_keys('input[aria-label="Search your listings"]', item['name'])
    time.sleep(1)
    
    scraper.element_click('div[aria-label="More"]')
    scraper.element_click_by_xpath('//span[text()="Edit listing"]')   
    time.sleep(5)
    
    #Update price
    if item.get('price'):
        update_price(item, scraper)
        
    #Update condition
    if item.get('condition'):
        update_condition(item, scraper)
        
    #Update location
    if item.get('location'):
        update_location(item, scraper)
    
    scraper.element_click('div[aria-label="Update"]')
    
    time.sleep(5)
    # logger.info(scraper.get_current_url().split("=")[-1])
    id = 1111111111 #TODO
    try:
        confirm_updating_item(id)
    except:
        logger.error(f"Failed to confirm updating of item {id}")
        

@shared_task(name='tasks.delete_item', bind=True) 
def delete_item(self, item):
	scraper.go_to_page('https://www.facebook.com/marketplace/you/selling')

	scraper.element_delete_text('input[aria-label="Search your listings"]')
	scraper.element_send_keys('input[aria-label="Search your listings"]', item['name'])
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

	images_path = generate_multiple_images_path(item['photo_dir'], item['photo_names'])
	scraper.input_file_add_files('input[accept="image/*,image/heif,image/heic"]', images_path)
 
	scraper.element_send_keys('label[aria-label="Title"] input', item['title'])
	scraper.element_send_keys('label[aria-label="Price"] input', item['price'])

	scraper.scroll_to_element('label[aria-label="Category"]')
	scraper.element_click('label[aria-label="Category"]')
	scraper.element_click_by_xpath(f'//span[text()="{item['category']}"]')

	scraper.element_click('label[aria-label="Condition"]')
	scraper.element_click_by_xpath(f'//span[text()="{item['condition']}"]')

	scraper.element_send_keys('label[aria-label="Description"] textarea', item['description'])
 
	scraper.element_click('div [aria-label="Next"] > div')
	scraper.element_click('div[aria-label="Publish"]:not([aria-disabled])')

	time.sleep(5)
 
	id = 1111111111 #TODO get the id
	try:
		confirm_creating_item(id)
	except:
		logger.error(f"Failed to confirm creating of item {item['Title']}")			
