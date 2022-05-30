from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import re
import logging
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning) # Removes "depreceated" selenium warnings
logging.getLogger('WDM').setLevel(logging.NOTSET) # Removes Webdriver Manager logging
logging.getLogger("urllib3").propagate = False

def getRegNumberOfVehicle(vinNumber):
    DRIVER = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    # Creating the request
    response = DRIVER.get(f'https://www.vegvesen.no/en/vehicles/buy-and-sell/vehicle-information/sjekk-kjoretoyopplysninger/?registreringsnummer={vinNumber}')
    time.sleep(1)
    # Check if response went through
    if response:
        print('(getRegNumberOfVehicle) Request is successful.')
    #else:
        #print('(getRegNumberOfVehicle) Request returned an error.')

    """
    Find element with the registration number
    Remove the whitespace in between the letters and numbers.
    Convert to text
    """

    regNumber = DRIVER.find_element(by=By.TAG_NAME, value="h2").text[0:8].replace(" ", "")

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
        print('(getVehiclePrivateAndDealerPrice) Request is successful.')
    #else:
        #print('(EgetVehiclePrivateAndDealerPrice) Request returned an error.')

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
        print(f"\nRegNumber:{regNumber}\nDealerprice: {dealerPrice}\nPrivateprice: {privatePrice}\nLiens: {liens}")
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
        print('(getVehicleAuctionPrice) Request is successful.')
    #else:
        #print('(getVehicleAuctionPrice) Request returned an error.')

    # Get elements with the "text-price" class.
    vehicleAuctionHighestBid = DRIVER.find_element_by_css_selector(('.term')).text

    vehicleAuctionLocation = DRIVER.find_element_by_css_selector(('.auction-location')).text

    vehicleTotalKilometresDriven = DRIVER.find_element_by_css_selector(('.key-number')).text

    vehicleTitle = DRIVER.find_element_by_css_selector(('.crumb-title')).text

    print(f"""{vehicleTitle}\nTotal kilometres: {vehicleTotalKilometresDriven} KM\nHighest bid on Auksjonen.no: {vehicleAuctionHighestBid} NOK\nCar location: {vehicleAuctionLocation}\n""")
    DRIVER.close()

    return vehicleAuctionHighestBid

def getAllAuctionCarsGivenBrand(auctionCarLinks, brand):

    DRIVER = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    DRIVER.set_window_position(-1000,-1000)
    # Creating the request
    response = DRIVER.get(f"https://auksjonen.no/auksjoner/bruktbil?filter=~(valueFilters~(~(field~%27details.brand~values~(~%27{brand}))))")
    
    if response:
        print('(getAllAuctionCarsGivenBrand) Request is successful.')
    #else:
        #print('(getAllAuctionCarsGivenBrand) Request returned an error.')

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
        print('(getRegNumberOfAuctionCar) Request is successful.')
    #else:
    #   print('(getRegNumberOfAuctionCar) Request returned an error.')

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
        print(f'Highest bid on auction: {carHighestBidOnAuction} kr\n Dealer Price: {carPrivateDealerPrice} kr')

        if int(carHighestBidOnAuction) - int(carPrivateDealerPrice) < 0:
            print(f"Auction car is cheaper by: {int(carPrivateDealerPrice) - int(carHighestBidOnAuction)} kr.")

def getCarDetailsFromFinn(url):

    DRIVER = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    # Creating the request
    response = DRIVER.get(url)
    if response:
        print('(getCarDetailsFromFinn) Request is successful.')
    #else:
        #print('(getCarDetailsFromFinn) Request returned an error.')

    finnCarsDetailsStrong = DRIVER.find_elements_by_css_selector('.u-strong') # Details with bold font on FINN advertisement
    carModelYear = finnCarsDetailsStrong[0].text
    carKilometres = finnCarsDetailsStrong[1].text.replace("km","").replace(" ", "")
    carTransmission = finnCarsDetailsStrong[2].text
    carFuelType = finnCarsDetailsStrong[3].text
    
    finnCarsDetailsInColumns = DRIVER.find_elements_by_css_selector('.list-descriptive') # Listed details under "specifications" subfield.

    carHorsePower = finnCarsDetailsInColumns
    # Convert from Array to String required:
    carBrand = DRIVER.find_elements_by_css_selector('.u-t2') # Array with the brand
    carTitle = DRIVER.find_elements_by_css_selector('.panel>p') # Array with the title
    carBrandString = ','.join(str(x.text) for x in carBrand) # Convert array to string. 
    carTitleString = carTitle[0].text # Convert array to string. 
    print(f'''Brand: {carBrandString}\nTitle: {carTitleString}\nModel Year: {carModelYear}\nTotal Kilometres: {carKilometres} KM\nTransmission: {carTransmission}\nFuel Type: {carFuelType}''')
    carDetailsOverview = {}
    carDetailsOverview["brand"] = carBrandString
    carDetailsOverview["title"] = carTitleString
    carDetailsOverview["modelyear"] = carModelYear
    carDetailsOverview["kilometres"] = carKilometres
    carDetailsOverview["transmission"] = carTransmission
    carDetailsOverview["fueltype"] = carFuelType
    return carDetailsOverview

def getCarBrandAndModelCode(url):

    carBrandAndModelCode = {}

    DRIVER = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    # Creating the request
    response = DRIVER.get(url)
    if response:
        print('(getCarBrandAndModelCode) Request is successful.')
    #else:
     #   print('(getCarBrandAndModelCode) Request returned an error.')

    carBrandAndModelCode = DRIVER.find_elements_by_css_selector('.truncate') # Details with bold font on FINN advertisement
    carBrandCodeFromLink = "" # Get car brand  e.g Audi
    carModelCodeFromLink = "" # Get car model e.g A6

    for brandcode in carBrandAndModelCode: 
        actualCode = brandcode.get_attribute('href')  
        if(actualCode != None):
            make = re.search("\d\.\d\d\d", actualCode) # Uses RegEx to find a pattern which matches the brandcode (Finn.no) e.g 0.744 = Audi
            if(make):
                carBrandCodeFromLink = make.group(0)

    for modelcode in carBrandAndModelCode:
        actualCode = modelcode.get_attribute('href')
        if(actualCode != None):
            make = re.search("\d\.\d\d\d\.\d\d\d", actualCode) # Uses RegEx to find a pattern which matches the modelcode (Finn.no) e.g 1.744.840 = Audi -> A6
            if(make):
                carModelCodeFromLink = make.group(0)
        else:
            continue
    #print(f"Car brand code : {carBrandCodeFromLink}")
    #print(f"Car model code: {carModelCodeFromLink}")

    carBrandAndModelCode["brandCode"] = carBrandCodeFromLink
    carBrandAndModelCode["modelCode"] = carModelCodeFromLink

    return carBrandAndModelCode

def createFinnLinkWithCarsSimilarToGivenCar(carDetailsDictionary):
    findCarsBrandAndModelCode = carDetailsDictionary["model"]
    findCarsWithHorsePowerFrom = carDetailsDictionary["horsepower"]
    findCarsWithHorsePowerTo = carDetailsDictionary["horsepower"]
    findCarsWithFuelType = carDetailsDictionary["fueltype"]
    findCarsWithMileageFrom = carDetailsDictionary["mileage"] - 30000
    findCarsWithMileageTo = carDetailsDictionary["mileage"] + 30000
    findCarsWithTransmission = carDetailsDictionary["transmission"]
    findCarsWithWheelDrive = carDetailsDictionary["wheeldrive"]
    # Year from & to depends on which generation the car is.
    findCarsWithYearFrom = carDetailsDictionary["modelyear"]
    findCarsWithYearTo = carDetailsDictionary["modelyear"]

    urlToCarWithSimilarSpecs = f'https://www.finn.no/car/used/search.html?engine_effect_from={findCarsWithHorsePowerFrom}&engine_effect_to={findCarsWithHorsePowerTo}&engine_fuel={findCarsWithFuelType}&mileage_from={findCarsWithMileageFrom}&mileage_to={findCarsWithMileageTo}&model={findCarsBrandAndModelCode}&page=1&sales_form=1&sort=PRICE_ASC&transmission={findCarsWithTransmission}&wheel_drive={findCarsWithWheelDrive}&year_from={findCarsWithYearFrom}&year_to={findCarsWithYearTo}'

    return urlToCarWithSimilarSpecs

def getAllCarsWithSameSpecsFromFinn(url, initialCarModelCode):
    DRIVER = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    # Creating the request
    response = DRIVER.get(url)
    if response:
        print('(getAllCarsWithSameSpecsFromFinn) Request is successful.')
    #else:
     #   print('(getAllCarsWithSameSpecsFromFinn) Request returned an error.')

    carBrandAndModelCode = DRIVER.find_elements_by_css_selector("")

def userMenu():
    auctionCarLinks = []
    userChoice = True
    while(userChoice):
        print("\n1. Get vehicle registration number from Statens Vegvesen using VIN-number (INSERT VIN-number)\n2. Get vehicle prices from regnr.no (INSERT Registration Number)\n3. Get auction prices from auksjonen.no (INSERT URL)\n4. Get auction cars from auksjonen.no (INSERT URL)\n5. Compare auction car with dealer price (INSERT URL)\n6. Get car details from FINN.no (INSERT URL)\n7. Exit Program\n")

        userChoice = input("I want to: ")

        if(userChoice == "1"):
            vinNumberInput = input("Please write the VIN Number: ")
            getRegNumberOfVehicle(vinNumberInput)

        elif(userChoice == "2"):
            regNumberInput = input("Please write the registration number: ")
            getVehiclePrivateAndDealerPrice(regNumberInput)
    
        elif(userChoice == "3"):
            url = regNumberInput = input("Please write the auction URL (https://www.auksjonen.no/auksjon/...): ")
            getVehicleAuctionPrice(url)

        elif (userChoice == "4"):
            brand = input("Please write the car brand: ")
            getAllAuctionCarsGivenBrand(auctionCarLinks,brand)
            for auctionCarLink in auctionCarLinks:
                getVehicleAuctionPrice(auctionCarLink)
        
        elif (userChoice == "5"):
            compareAuctionPriceWithDealerPrice(auctionCarLinks)

        elif (userChoice == "6"):
            url = input("FINN.no URL: ")
            getCarDetailsFromFinn(url)   

        elif(userChoice == "7"):
            userChoice = False
        
        else:
            print("\n Not Valid Choice Try again")  

userMenu()