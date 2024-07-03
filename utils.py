from helpers.scraper import Scraper
import time

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

def update_price(item, scraper: Scraper):
    scraper.scroll_to_element('label[aria-label="Price"] input"]')
    time.sleep(1)
    scraper.element_delete_text('label[aria-label="Price"] input')
    scraper.element_send_keys('label[aria-label="Price"] input', item['Price'])
    time.sleep(1)
 
def update_condition(item, scraper: Scraper):
    scraper.scroll_to_element('label[aria-label="Condition"]')
    time.sleep(1)
    scraper.element_click('label[aria-label="Condition"]')
    scraper.element_click_by_xpath(f'//div[@aria-selected]/div/div/div/span[text()="{item["Condition"]}"]')
    time.sleep(1)
    
def update_location(item, scraper: Scraper):
    scraper.scroll_to_element('input[aria-label="Location"]')
    time.sleep(1)
    scraper.element_delete_text('input[aria-label="Location"]')
    scraper.element_send_keys('input[aria-label="Location"]', item['Location'])
    time.sleep(1)
    scraper.find_multiple_elements_by_xpath('//ul[@aria-label="5 suggested searches"]/li', 0).click()