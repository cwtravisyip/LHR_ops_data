# selenium
import pandas as pd
import datetime 
import logging

from selenium import webdriver 
from selenium.webdriver.firefox.options import Options

if __name__ == '__main__':
    import os
    os.chdir('./code')
    print(os.getcwd())

    from src.scrape_data import *


    logger = logging.getLogger(__name__)
    current_date = datetime.datetime.now(tz= datetime.timezone.utc)
    sleep_time = 1

    options = Options()
    #options.add_argument("-headless") 

    with webdriver.Firefox(options = options) as driver:
        # initate_driver("https://www.heathrow.com/departures")
        driver.get("https://www.heathrow.com/departures")
        time.sleep(5) 
        # confirm the page is loadded to the date wanted properly
        input("Enter when the desired page is loaded (accepted cookies)")

        # get to top of the day
        go_to_top(driver)

        departures = scrape_heathrow_pages(driver=driver,departure=True)

        # get the actual departure time
        # initialise a 'time_act' column to fill
        departures['time_act'] = pd.NA

        # iterate through rows
        counter = 1
        error_list = []
        # set up headless driver
        for key, val in departures[(departures['time_act'].isna()) & (departures["status"] == "DEPARTED")].iterrows():
            driver.get(val['url'])
            time.sleep(sleep_time)
            try:
                time_act, iata = scrape_flight_page(dep=True)
                departures.loc[key,['time_act','iata']] = time_act, iata
                # print(f'{counter}: flight {key} scheduled at {val["time_sch"]} departed at {time_act}')
            except:
                logger.info(f"Error occured when calling scrape_flight_page for {val['status']} flight {key}")
                error_list.append(val['url'])
            counter +=1 

        logger.info(f"{departures.isnull().sum()} null values returned")

        ######################## return arrival data ##################################

        driver.get("https://www.heathrow.com/arrivals")
        time.sleep(5) 
        # confirm the page is loadded to the date wanted properly
        input("Enter when the desired page is loaded (accepted cookies)")
        # get to top of the day
        go_to_top(driver)

        arrivals = scrape_heathrow_pages(driver=driver,departure=False)

        # iterate through rows
        counter = 1
        arrivals["time_act"] = pd.NA
        # set up headless driver
        for key, val in arrivals[arrivals['time_act'].isnull() &
                            ((arrivals["status"] != "CANCELLED")& (arrivals['status'] != "FLIGHT DIVERTED"))
                            ].iterrows():
            driver.get(val['url'])
            time.sleep(sleep_time)
            try:
                time_act,iata = scrape_flight_page(dep = False)
                arrivals.loc[key,['time_act','iata']] = time_act, iata
                # print(f'{counter}: flight {key} scheduled at {val["time_sch"]} landed at {time_act}')
            except:
                logger.log(f"Error occured when calling scrape_flight_page for {val['status']} flight {key}")
                error_list.append(val['url'])
            counter +=1 

        logger.info(f"{arrivals.isnull().sum()} null values returned")


    # add orig/dest column
    departures['orig'] = ["London" for _ in range(len(departures))]
    arrivals['dest'] = ['London' for _ in range(len(arrivals))]
    df_lhr = pd.concat([departures, arrivals])
    # inspect
    df_lhr.head()


    file_name = f"{current_date.strftime('%d%b%Y')}_LHR.csv" 
    # define file name
    # Get the parent directory (preceding folder) of the current directory
    parent_directory = os.path.dirname(os.getcwd())
    filepath = os.path.join(parent_directory ,"data",file_name )

    # save to csv
    logger.log(f"Saving df to {filepath}")
    df_lhr.to_csv(filepath)


    # export the error list
    file_name = f"error_{current_date.strftime('%d%b%Y')}_LHR.txt"
    with open(os.path.join(parent_directory,'data',file_name), 'w') as file:
        file.write("\n".join(error_list))