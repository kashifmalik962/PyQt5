import ast
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

# setup chrome
chrome_options = Options()
chrome_options.add_argument('--headless')
driver = webdriver.Chrome()

# Open txt file
file = open('path.txt','r')
step = ast.literal_eval('['+ file.read() +']')
file.close()
driver.get('http://127.0.0.1:5000')
actions = ActionChains(driver)

wait = WebDriverWait(driver,5)


# Selenium logic
for i in step:
    print(i[0])
    wait.until(EC.element_to_be_clickable((By.XPATH, i[0]))).click()
    if len(i[1]) >= 1:
        for input_data in i[1]:
            xpath = input_data[0]
            text = input_data[1]
            print(xpath, '==', text)
            wait.until(EC.element_to_be_clickable((By.XPATH, xpath))).click()
            actions.send_keys(text)
            actions.perform()
    
    if i[2] != []:
        print(i[2],"++++++++++++++++++++++++++++++++++++++++++++++++")
        driver.get(i[2])

print("script Execute Successfully")