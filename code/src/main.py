import selenium.webdriver as webdriver
from  selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import time

from typing import Literal, Union, List, Tuple


def scrape_heathrow_pages(driver:WebDriver)-> pd.DataFrame:
     
    times = []
    codes = []
    citys = []
    urls = []
    status = []

    while True:
        time, code, city, url, stat = scrape_heathrow_table(driver)
        times.extend(time)
        codes.extend(code) 
        citys.extend(city)
        urls.extend(url)
        status.extend(stat)
        try:
            click_LHR_later(driver)
        except:
            print('Reached end of the page')
            break

    df = pd.DataFrame({"time_sch":times,'code':codes,'dest':citys, "status":status,'url':urls})
    df = df.set_index('code')        
    
    return df

def scrape_heathrow_table(driver: WebDriver)->Tuple[List]:
    """
    parse the departure time, flight code and the city to three list
    """
    times = []
    codes = []
    citys = []
    urls = []
    status = []

    # loop over all list flight schedule item
    for result in driver.find_elements(By.XPATH,'//*[@class="airline-listing-table"]/a[contains(@class,"airline-listing-line-item")]'):
        ftime = result.find_element(By.XPATH,"./div").text
        code = result.find_element(By.XPATH,"./div[2]/div[1]/div[1]").text
        city = result.find_element(By.XPATH,"./div[2]/div[1]/div[2]").text
        url  = result.get_attribute("href")
        status_i = result.find_element(By.XPATH,"./div[3]/p").text
        times.append(ftime)
        codes.append(code)
        citys.append(city)
        urls.append(url)
        status.append(status_i)

        # print(f"Flight {code} departing for {city} at {ftime}: {url}")
    return times, codes, citys, urls, status


def click_LHR_later(driver:WebDriver):
    # loop through all schedule of the date
    later_flight_button =   '//*[@id="flight-list-app"]/div/div[2]/div[2]/div/div[3]/button'
    try: 
		# load later flights
	    driver.find_element(By.XPATH,later_flight_button).send_keys(Keys.RETURN)

    except:
        raise NoSuchElementException


def scrape_flight_page(dep:bool, driver: WebDriver):
    """scape the individual HEATHROW flight page (one flight page not the table)"""
    # identify which block to scrape
    div_id = 0 if dep else 1
    # point to the flight detail card
    res  = driver.find_elements(By.XPATH, "//div[contains(@class,'show-flight-details')]")
    card = res[div_id] # identified the card by departure or arrival
    iata_card = res[1 if dep else 0]
    try:
        time_act = card.find_element(By.XPATH, ".//div[contains(@aria-label,'actual time')]").text
    except:
        print("An error occured when parsing the actual time.")
        time_act = None
    try:
        iata = iata_card.find_element(By.XPATH, "./p").text
    except:
        print("An error occured when parsing the iata.")
        iata = None

    return time_act, iata

def go_to_top(driver: WebDriver): 
    """
    to be called when web driver is at the daily schedule page, to scroll to the top of the page
    """           
    earlier_flight_button = '//*[@id="flight-list-app"]/div/div[2]/div[2]//button[1]'
    
    while True:
        try:
            driver.find_element(By.XPATH,earlier_flight_button).send_keys(Keys.RETURN)
            time.sleep(0.5) 
        except:
            print("Loaded to the top of the list")
            break
    

if __name__ == '__main__':
    # initiate the web driver
    driver = webdriver.Firefox()

    print('Finishing job')
        