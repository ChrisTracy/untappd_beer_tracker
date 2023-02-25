# import the necessary modules and classes from the Selenium library
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os
import datetime
import time
from flask import Flask
import threading

class BeerTracker:
    def __init__(self, json_file):  # initialize the BeerTracker object
        self.json_file = json_file  # set the JSON file name
        self.load_data()  # load the data from the JSON file

    def load_data(self):
        if not os.path.isfile(self.json_file):  # if the JSON file does not exist
            with open(self.json_file, 'w') as f:  # create a new file and write an empty dictionary to it
                json.dump({}, f)

        with open(self.json_file, 'r') as f:  # open the JSON file for reading
            try:
                self.data = json.load(f)  # try to load the data from the file into the BeerTracker object
            
            except json.JSONDecodeError:  # if the file cannot be parsed
                self.data = {}  # set the data to an empty dictionary
                with open(self.json_file, 'w') as f:  # create a new file and write an empty dictionary to it
                    json.dump(self.data, f)

        if 'total' not in self.data:  # if the 'total' key is not in the data dictionary
            self.update_total()  # update the total using the check_untap_total method

    def update_total(self):
        untap_total = self.check_untap_total()  # get the number of beers on Untappd using the check_untap_total method
        self.data['total'] = untap_total  # set the 'total' key in the data dictionary to the new value
        self.save_data()  # save the updated data to the JSON file
        return untap_total  # return the new total

    def add_beer(self, num_beers, date=None):  # add a specified number of beers to the total count for a given date
        if date is None:  # if the date is not specified
            date = datetime.date.today()  # use today's date

        if str(date) not in self.data:  # if the date is not in the data dictionary
            self.data[str(date)] = 0  # add the date with a count of zero

        self.data[str(date)] += num_beers  # add the specified number of beers to the count for the given date
        self.save_data()  # save the updated data to the JSON file

    def check_untap_total(self):  # use the Selenium web driver to get the number of beers from the user's Untappd profile page
        try:
            options = webdriver.FirefoxOptions()  # create a FirefoxOptions object
            options.add_argument('--headless')  # set the FirefoxOptions object to run in headless mode
            driver = webdriver.Firefox(executable_path=gecko_driver_path, options=options)  # create a Firefox web driver object using the FirefoxOptions object
            wait = WebDriverWait(driver, 2)  # create a WebDriverWait object with a timeout of 2 seconds
            untappd_username = os.getenv('UNTAPPD_USERNAME') # pull the username from the host enviroment variable
            driver.get(f'https://untappd.com/user/{untappd_username}')  # navigate to the user's Untappd
            stat_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'stat')))  # wait until the 'stat' element is present on the page
            total = int(stat_element.text.replace(',', ''))  # get the number of beers from the 'stat' element and remove any commas
            driver.quit()  # quit the web driver
            return total  # return the number of beers
        
        except Exception as e:  # if there is an error
            print(f'Error checking Untappd total: {str(e)}')  # print an error message
            return None  # return None

    def save_data(self):  # write the data to the JSON file
        with open(self.json_file, 'w') as f:  # open the JSON file for writing
            json.dump(self.data, f, indent=4)  # write the data to the file with indentation for readability

if __name__ == '__main__':  # if this script is being run as the main program
    app = Flask(__name__) # init Flask
    tracker = BeerTracker('beer_tracker.json')  # create a BeerTracker object with the specified JSON file name
    interval = int(os.environ.get('INTERVAL', 120)) # Pull the interval from the env variable. If it does not exist 120 is default
    gecko_driver_path = GeckoDriverManager().install() # Install the firefox Gecko Driver

    @app.route('/data/beer') # Set the flask route
    def get_data(): # pull json data
        with open(tracker.json_file) as f: # open the json file
            data = json.load(f) # lod json data
        return data # return the file to the flask route
    
    thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8089)) # set params for the threading server
    thread.start() # start the threading server

    while True: # While loop on set interval

        untap_total = tracker.check_untap_total()  # get the current number of beers on Untappd using the check_untap_total method
        tracker = BeerTracker('/app/data/beer_tracker.json')  # create a BeerTracker object with the specified JSON file name. This will load the file at every loop for testing (change the json file)
        json_total = tracker.data['total']  # get the total number of beers from the data dictionary

        if json_total != untap_total:  # if the number of beers has changed since the last time the script was run
            print("running loop")
            beer_change = untap_total - json_total  # calculate the difference in the number of beers
            tracker.add_beer(beer_change)  # add the difference to the count for today's date using the add_beer method
            tracker.update_total()  # update the total count in the data dictionary and save the data to the JSON file

        time.sleep(interval) # Sleep for the set interval seconds before running again