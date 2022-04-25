from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def main():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox') # An error will occur without this line
    driver = webdriver.Chrome(options=options)
    try:
        driver.get('https://stackoverflow.com/questions/49323099/webdriverexception-message-service-chromedriver-unexpectedly-exited-status-co')
        search = driver.find_element(By.NAME, 'q')
        search.send_keys('Python')
        search.send_keys(Keys.RETURN)

        time.sleep(30)
        #driver.save_screenshot('search.png')
    finally:
        driver.close()
        driver.quit()

if __name__ == '__main__':
    main()