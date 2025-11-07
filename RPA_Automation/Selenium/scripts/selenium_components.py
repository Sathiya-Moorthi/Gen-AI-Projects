from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import selenium.webdriver.support.ui as webdriverwaits

driver = webdriver.Chrome()
driver.get("https://www.saucedemo.com")


# Navigation commands
# driver.back()
# driver.forward()
# driver.refresh()

# Finding elements
element = driver.find_element(By.ID, "login-button")
# element =  driver.find_elements(By.XPATH, "//*[@id='root']")

print(element)

#wait
wait = webdriverwaits.WebDriverWait(driver, 10)
element = wait.until(EC.element_to_be_clickable((By.ID, "login-button")))

#Intersections with elements
element.click()
driver.find_element(By.ID, "user-name").send_keys("standard_user")
driver.find_element(By.ID, "password").send_keys("secret_sauce")
