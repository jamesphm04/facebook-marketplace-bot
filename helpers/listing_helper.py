from ..utils import generate_multiple_images_path
from scraper import Scraper
import time

def create_items(data, scraper: Scraper):
    
    for item in data:
        create_item(item, scraper)
        
def create_item(item, scraper: Scraper):
	scraper.go_to_page('https://www.facebook.com/marketplace/you/selling')

	scraper.element_click('div[aria-label="Marketplace sidebar"] a[aria-label="Create new listing"]')
	scraper.element_click('a[href="/marketplace/create/item/"]')

	images_path = generate_multiple_images_path(item['photo_dir'], item['photo_names'])
	scraper.input_file_add_files('input[accept="image/*,image/heif,image/heic"]', images_path)
 
	scraper.element_send_keys('label[aria-label="Title"] input', item['title'])
	scraper.element_send_keys('label[aria-label="Price"] input', item['price'])

	scraper.scroll_to_element('label[aria-label="Category"]')
	scraper.element_click('label[aria-label="Category"]')
	scraper.element_click_by_xpath('//span[text()="' + item['category'] + '"]')

	scraper.element_click('label[aria-label="Condition"]')
	scraper.element_click_by_xpath('//span[text()="' + item['condition'] + '"]')

	scraper.element_send_keys('label[aria-label="Description"] textarea', item['description'])
 
	scraper.element_click('div [aria-label="Next"] > div')
	scraper.element_click('div[aria-label="Publish"]:not([aria-disabled])')

	time.sleep(5)
