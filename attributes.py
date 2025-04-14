import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

driver = webdriver.Chrome()

driver.get("http://192.168.233.179/#/login")


def get_element_info(driver, element):
    info = {}
    info['position'] = element.location
    info['id'] = element.get_attribute('id')
    info['name'] = element.get_attribute('name')
    info['class_name'] = element.get_attribute('class')
    return info


def get_info(driver, xpath):
    element = driver.find_element(By.XPATH, xpath)

    # Extract the required information
    element_info = (
        f"{xpath} "
        f"{element.location} "
        f"{element.tag_name} "
        f"{element.get_attribute('id')} "
        f"{element.get_attribute('name')}"
    )

    return element_info

# Should expect a string in return
def get_xpath(driver, element: WebElement):
    # Construct the XPath manually
    tag = element.tag_name
    attributes = []
    if element.get_attribute("id"):
        attributes.append(f"@id='{element.get_attribute('id')}'")
    if element.get_attribute("name"):
        attributes.append(f"@name='{element.get_attribute('name')}'")
    if attributes:
        xpath = f"//{tag}[{' and '.join(attributes)}]"
    else:
        xpath = driver.execute_script(
            "function absoluteXPath(element) {"
            "var comp, comps = [];"
            "var parent = null;"
            "var xpath = '';"
            "var getPos = function(element) {"
            "var position = 1, curNode;"
            "if (element.nodeType == Node.ATTRIBUTE_NODE) {"
            "return null;"
            "}"
            "for (curNode = element.previousSibling; curNode; curNode = curNode.previousSibling) {"
            "if (curNode.nodeName == element.nodeName) {"
            "++position;"
            "}"
            "}"
            "return position;"
            "};"
            "if (element instanceof Document) {"
            "return '/';"
            "}"
            "for (; element && !(element instanceof Document); element = element.nodeType == Node.ATTRIBUTE_NODE ? element.ownerElement : element.parentNode) {"
            "comp = comps[comps.length] = {};"
            "switch (element.nodeType) {"
            "case Node.TEXT_NODE:"
            "comp.name = 'text()';"
            "break;"
            "case Node.ATTRIBUTE_NODE:"
            "comp.name = '@' + element.nodeName;"
            "break;"
            "case Node.PROCESSING_INSTRUCTION_NODE:"
            "comp.name = 'processing-instruction()';"
            "break;"
            "case Node.COMMENT_NODE:"
            "comp.name = 'comment()';"
            "break;"
            "case Node.ELEMENT_NODE:"
            "comp.name = element.nodeName;"
            "break;"
            "}"
            "comp.position = getPos(element);"
            "}"
            "for (var i = comps.length - 1; i >= 0; i--) {"
            "comp = comps[i];"
            "xpath += '/' + comp.name.toLowerCase();"
            "if (comp.position !== null) {"
            "xpath += '[' + comp.position + ']';"
            "}"
            "}"
            "return xpath;"
            "}"
            "return absoluteXPath(arguments[0]);", element)
    return xpath


username_field = driver.find_element(By.NAME, "username")
password_field = driver.find_element(By.NAME, "password")
login_button = driver.find_element(By.ID, "submit-button")
network_img = driver.find_element(By.XPATH, "//img[@id='network-img']")
mat_icon = driver.find_element(By.XPATH, "/html[1]/body[1]/app-root[1]/app-login[1]/div[1]/div[2]/div[1]/div[1]/form[1]/div[2]/span[1]/mat-icon[1]")


print(username_field.tag_name)
print(username_field.rect)
print(username_field.value_of_css_property("font-size"))
print(username_field.text)
print(username_field.get_attribute('href'))
print(login_button.text)

print(str(get_element_info(driver, login_button)) + "\n")
print(str(get_element_info(driver, username_field)) + "\n")
print(str(get_element_info(driver, password_field)) + "\n")

print(get_element_info(driver, login_button))
print(get_element_info(driver, network_img))
print(get_element_info(driver, mat_icon))


element = driver.find_element(By.XPATH, "//button[@id='submit-button']")


def apply_style(s):
    driver.execute_script("""
        var element = arguments[0];
        element.setAttribute('style', arguments[1]);
    """, element, s)


original_style = element.get_attribute('style')
apply_style("background: yellow; border: 2px solid red;")
time.sleep(.3)
apply_style(original_style)


username_field = driver.find_element(By.XPATH, "//input[@name='username']")
password_field = driver.find_element(By.XPATH, "//input[@name='password']")

username_field.send_keys("user")
driver.implicitly_wait(0.5)
password_field.send_keys("user")

driver.implicitly_wait(0.5)

login_button = driver.find_element(By.XPATH, "//button[@id='submit-button']")
#login_button.click()

time.sleep(3)


#input_selection = driver.find_element(By.XPATH, "/html[1]/body[1]/app-root[1]/app-page-layout[1]/div[1]/aside[1]/app-primary-nav[1]/perfect-scrollbar[1]/div[1]/div[1]/nav[1]/a[2]")
#input_selection.click()

#settings = driver.find_element(By.XPATH, "/html[1]/body[1]/app-root[1]/app-page-layout[1]/div[1]/aside[1]/app-primary-nav[1]/perfect-scrollbar[1]/div[1]/div[1]/nav[1]/a[6]")
#settings.click()

elements_id = driver.find_elements(By.XPATH, '//*[@id]')
elements_css = driver.find_elements(By.CSS_SELECTOR, "*")
nodes = driver.find_elements(By.XPATH, "//*")






file = open("login_page.txt", "w")

for x in nodes:
    file.write(str(get_xpath(driver, x)) + " " + str(x.location) + " " + str(x.tag_name) + " " + str(x.get_attribute('id')) + " " +
               str(x.get_attribute('name')) + '\n')

file.close()

driver.quit()
