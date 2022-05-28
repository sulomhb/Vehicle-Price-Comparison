from lib2to3.pgen2.driver import Driver
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
import time



def getRegNumberOfVehicle(vinNumber):
    
    DRIVER = webdriver.Chrome('/home/sesu/Documents/Home/dev/python/chromedriver')

    # Creating the request
    response = DRIVER.get(f'https://www.vegvesen.no/en/vehicles/buy-and-sell/vehicle-information/sjekk-kjoretoyopplysninger/?registreringsnummer={vinNumber}')
    time.sleep(1)
    # Check if response went through
    if response:
        print('(Get RegNumber) Request is successful.')
    else:
        print('(Get RegNumber) Request returned an error.')

    """
    Find element with the registration number
    Remove the whitespace in between the letters and numbers.
    Convert to text
    """

    regNumber = DRIVER.find_element_by_tag_name("h2").text[0:8].replace(" ", "")

    print(f'\nVIN Number: {vinNumber} belongs to registration number: {regNumber}')

    # Close browser window
    DRIVER.close()

    return regNumber



def getVehiclePrices(regNumber):
    DRIVER = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    # Creating the request
    response = DRIVER.get(f"https://www.regnr.no/{regNumber}")

    # Check if response went through
    if response:
        print('(Estimated vehicle price) Request is successful.')
    else:
        print('(Estimated vehicle price) Request returned an error.')

    time.sleep(10)

    
 
    python_button = DRIVER.find_elements_by_xpath("/html/body/div/div/div/div[1]/div[3]/div[1]")[0]
    python_button.click()

    # Get elements with the "text-price" class.
    allVehiclePrices = WebDriverWait(DRIVER,500).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".text-price")))

    # Print the parent element with children elements as an array (for debugging purposes)
    print([price.text for price in allVehiclePrices])
    
    #Convert each element to text
    if(len(allVehiclePrices) == 6):
        dealerPrice = allVehiclePrices[3].text
        privatePrice = allVehiclePrices[4].text
        liens = allVehiclePrices[5].text
         # Print out the different prices
        print(f'''
        RegNumber: {regNumber}\n
        Dealerprice: {dealerPrice}\n'
        Privateprice: {privatePrice}\n'
        Liens: {liens}\n''')
    else:
        print(f"Could not get price, please check this URL: https://www.regnr.no/{regNumber}")
    DRIVER.close()


def getVehicleAuctionPrice(url):
    DRIVER = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    # Creating the request
    response = DRIVER.get(url)

    # Check if response went through
    if response:
        print('(Estimated vehicle price) Request is successful.')
    else:
        print('(Estimated vehicle price) Request returned an error.')

    # Get elements with the "text-price" class.
    vehicleAuctionHighestBid = DRIVER.find_element_by_css_selector(('.term')).text

    vehicleAuctionLocation = DRIVER.find_element_by_css_selector(('.auction-location')).text

    vehicleTotalKilometresDriven = DRIVER.find_element_by_css_selector(('.key-number')).text

    vehicleTitle = DRIVER.find_element_by_css_selector(('.crumb-title')).text

    print(f'''
    {vehicleTitle}
    Total kilometres: {vehicleTotalKilometresDriven} KM
    Highest bid on Auksjonen.no: {vehicleAuctionHighestBid} NOK
    Car location: {vehicleAuctionLocation}\n\n''')
    DRIVER.close()

def userMenu():
    userChoice = True
    while(userChoice):
        print("""
        1. Get vehicle registration number from Statens Vegvesen using VIN-number (INSERT VIN-number)
        2. Get vehicle prices from regnr.no (INSERT Registration Number)
        3. Get auction prices from auksjonen.no (INSERT URL)
        4. Get auction cars from auksjonen.no
        5. Exit Program
        """)

        userChoice = input("        I want to: ")

        if(userChoice == "1"):
            vinNumberInput = input("        Please write the VIN Number: ")
            getRegNumberOfVehicle(vinNumberInput)

        elif(userChoice == "2"):
            regNumberInput = input("        Please write the registration number: ")
            getVehiclePrices(regNumberInput)
    
        elif(userChoice == "3"):
            url = regNumberInput = input("      Please write the auction URL: ")
            getVehicleAuctionPrice(url)

        elif (userChoice == "4"):
            auctionCarLinks = []
            brand = input("      Please write the car brand: ")
            getAllAuctionCarsGivenBrand(auctionCarLinks,brand)
            for auctionCarLink in auctionCarLinks:
                getVehicleAuctionPrice(auctionCarLink)

        elif(userChoice == "5"):
            userChoice = False
        
        else:
            print("\n Not Valid Choice Try again")
        


def getAllAuctionCarsGivenBrand(auctionCarLinks, brand):

    DRIVER = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    # Creating the request
    response = DRIVER.get(f"https://auksjonen.no/auksjoner/bruktbil?filter=~(valueFilters~(~(field~%27details.brand~values~(~%27{brand}))))")
    
    if response:
        print('(Get RegNumber) Request is successful.')
    else:
        print('(Get RegNumber) Request returned an error.')

    auctionListings = DRIVER.find_elements_by_css_selector('.clearfix')

    for auctionCar in auctionListings:
        auctionCarLink = auctionCar.get_attribute('href')
        if(auctionCarLink != None):
            auctionCarLinks.append(auctionCarLink)
        else:
            continue

    #print(auctionCarLinks)
