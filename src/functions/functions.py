from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import re

def userMenu():
    auctionCarLinks = []
    userChoice = True
    while(userChoice):
        print("""
        1. Get vehicle registration number from Statens Vegvesen using VIN-number (INSERT VIN-number)
        2. Get vehicle prices from regnr.no (INSERT Registration Number)
        3. Get auction prices from auksjonen.no (INSERT URL)
        4. Get auction cars from auksjonen.no (INSERT URL)
        5. Compare auction car with dealer price (INSERT URL)
        6. Get car details from FINN.no (INSERT URL)
        7. Exit Program
        """)

        userChoice = input("        I want to: ")

        if(userChoice == "1"):
            vinNumberInput = input("        Please write the VIN Number: ")
            getRegNumberOfVehicle(vinNumberInput)

        elif(userChoice == "2"):
            regNumberInput = input("        Please write the registration number: ")
            getVehiclePrivateAndDealerPrice(regNumberInput)
    
        elif(userChoice == "3"):
            url = regNumberInput = input("      Please write the auction URL: ")
            getVehicleAuctionPrice(url)

        elif (userChoice == "4"):
            brand = input("      Please write the car brand: ")
            getAllAuctionCarsGivenBrand(auctionCarLinks,brand)
            for auctionCarLink in auctionCarLinks:
                getVehicleAuctionPrice(auctionCarLink)
        
        elif (userChoice == "5"):
            compareAuctionPriceWithDealerPrice(auctionCarLinks)

        elif (userChoice == "6"):
            url = "https://www.finn.no/car/used/ad.html?finnkode=257881559"
            getCarDetailsFromFinn(url)   

        elif(userChoice == "7"):
            userChoice = False
        
        else:
            print("\n Not Valid Choice Try again")  

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

def getVehiclePrivateAndDealerPrice(regNumber):
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
    dealerPrice = 0
    privatePrice = 0
    #Convert each element to text
    if(len(allVehiclePrices) == 6):
        dealerPrice = allVehiclePrices[3].text
        privatePrice = allVehiclePrices[4].text
        liens = allVehiclePrices[5].text
         # Print out the different prices
        print(" RegNumber:" + regNumber + "\n Dealerprice:" + dealerPrice + "\n Privateprice: " + privatePrice + "\n Liens:" + liens)
    else:
        print(f"Could not get price, please check this URL: https://www.regnr.no/{regNumber}")
    DRIVER.close()
    return [dealerPrice, privatePrice]

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

    print(f"""
    {vehicleTitle}
    Total kilometres: {vehicleTotalKilometresDriven} KM
    Highest bid on Auksjonen.no: {vehicleAuctionHighestBid} NOK
    Car location: {vehicleAuctionLocation}\n""")
    DRIVER.close()

    return vehicleAuctionHighestBid

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

def getRegNumberOfAuctionCar(url):
    DRIVER = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    # Creating the request
    response = DRIVER.get(url)
    
    if response:
        print('(Get RegNumber) Request is successful.')
    else:
        print('(Get RegNumber) Request returned an error.')

    auctionCarRegistrationNumber = DRIVER.find_elements_by_css_selector('.ng-binding')
    for info in auctionCarRegistrationNumber:
        if re.findall("^[A-Z]{1,2}[0-9]{2,5}$", info.text): # Check if the information is in the Norwegian license plate pattern. [XX00000]
            regNumber = info.text
    return regNumber

def compareAuctionPriceWithDealerPrice(auctionCarLinks):
    brand = input('Insert brand you would like to compare the prices to: ')
    getAllAuctionCarsGivenBrand(auctionCarLinks, brand)
    for auctionCarLink in auctionCarLinks:
        carHighestBidOnAuction = int(getVehicleAuctionPrice(auctionCarLink).replace(",-","").replace(" ", ""))
        regNumberOfAuctionCar = getRegNumberOfAuctionCar(auctionCarLink)
        carPrivateDealerPrice = getVehiclePrivateAndDealerPrice(regNumberOfAuctionCar)
        carPrivateDealerPrice = str(carPrivateDealerPrice[0]).replace(",-","").replace("kr", "").replace(" ", "")
        print(f' Highest bid on auction: {carHighestBidOnAuction} kr\n Dealer Price: {carPrivateDealerPrice} kr')

        if int(carHighestBidOnAuction) - int(carPrivateDealerPrice) < 0:
            print(f" Auction car is cheaper by: {int(carPrivateDealerPrice) - int(carHighestBidOnAuction)} kr.")

def getCarDetailsFromFinn(url):
    
    DRIVER = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    # Creating the request
    response = DRIVER.get(url)
    if response:
        print('(Get RegNumber) Request is successful.')
    else:
        print('(Get RegNumber) Request returned an error.')

    finnCarsDetailsStrong = DRIVER.find_elements_by_css_selector('.u-strong') # Details with bold font on FINN advertisement
    carModelYear = finnCarsDetailsStrong[0].text
    carKilometres = finnCarsDetailsStrong[1].text.replace("km","").replace(" ", "")
    carTransmission = finnCarsDetailsStrong[2].text
    carFuelType = finnCarsDetailsStrong[3].text
    carBrand = DRIVER.find_elements_by_css_selector('.u-t2') # Array with the brand
    carTitle = DRIVER.find_elements_by_css_selector('.panel>p') # Array with the title
    carBrandString = ','.join(str(x.text) for x in carBrand) # Convert array to string. 
    carTitleString = carTitle[0].text # Convert array to string. 
    print(f''' 
    Brand: {carBrandString}
    Title: {carTitleString}
    Model Year: {carModelYear}
    Total Kilometres: {carKilometres} KM
    Transmission: {carTransmission}
    Fuel Type: {carFuelType}
    ''')
    carDetailsOverview = {}
    carDetailsOverview["brand"] = carBrandString
    carDetailsOverview["title"] = carTitleString
    carDetailsOverview["modelyear"] = carModelYear
    carDetailsOverview["kilometres"] = carKilometres
    carDetailsOverview["transmission"] = carTransmission
    carDetailsOverview["fueltype"] = carFuelType
    return carDetailsOverview
def getAllCarsWithSameSpecsFromFinn():
    return

userMenu()