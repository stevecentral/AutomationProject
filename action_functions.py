import time

import hjson
from pefile import IMAGE_CHARACTERISTICS
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from PIL import Image, ImageChops
import os
import requests

import telnetlib3
import asyncio

import telnetlib3
import asyncio
from threading import Thread
import time


# Used when the element could not be located
class ElementNotFoundException(Exception):
    pass


def login(driver, username, password):
    username_field = driver.find_element(By.XPATH, "//input[@name='username']")
    password_field = driver.find_element(By.XPATH, "//input[@name='password']")

    username_field.send_keys(str(username))
    driver.implicitly_wait(0.5)
    password_field.send_keys(str(password))

    driver.implicitly_wait(0.5)

    login_button = driver.find_element(By.XPATH, "//button[@id='submit-button']")
    login_button.click()

    time.sleep(5)


# Logs out from the web page
def logout(driver):
    power_button = driver.find_element(By.XPATH, "//div[@id='logout']")
    power_button.click()

    time.sleep(3)


# Complete power cycle if user confirms otherwise the process is cancelled
def power_cycle(driver, proceed):
    # Different wait time
    wait_time = 1

    power_button = driver.find_element(By.ID, "power-menu-button")
    power_button.click()

    time.sleep(1)

    reboot_button = driver.find_element(By.XPATH, "//button[contains(text(),'Reboot')]")
    reboot_button.click()

    time.sleep(1)

    will_reboot_button = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/mat-dialog-container/confirm-dialog/div/div[3]/button[2]")

    if proceed == "yes":
        will_reboot_button = driver.find_element(By.XPATH, "//button[.//span[text()='OK']]")
        wait_time = 20

    will_reboot_button.click()
    # Wait longer if rebooting
    time.sleep(wait_time)


# Turn the wall on\off depending on the current state
def power_toggle(driver):
    power_button = driver.find_element(By.ID, "power-menu-button")
    power_button.click()

    time.sleep(1)

    reboot_button = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/div/div/button[1]")
    reboot_button.click()

    time.sleep(1)


# Display a tile pattern
def set_tile_pattern(driver, option):
    # Click the initial button
    tile_pattern_button = driver.find_element(By.XPATH, "//div[@id='identifytiles-button']")
    driver.execute_script("arguments[0].click();", tile_pattern_button)
    time.sleep(1)

    # Dictionary mapping options to their button numbers
    options_map = {
        "off": 1,
        "id": 2,
        "red": 3,
        "green": 4,
        "blue": 5,
        "grey": 6,
        "info": 7,
        "heatmap": 8,
        "neighbor": 9
    }

    # Mapping options to their xpath
    if option in options_map:
        button = driver.find_element(
            By.XPATH,
            f"/html/body/div[2]/div[2]/div/div/div/button[{options_map[option]}]"
        )
        driver.execute_script("arguments[0].click();", button)
    else:
        print("couldn't find")

    time.sleep(1)

    # Use javascript to force a click
    overlay = driver.find_element(By.XPATH, "/html/body/div[2]")
    driver.execute_script("arguments[0].click();", overlay)
    time.sleep(3)


# Take a screenshot of the current page
def screenshot(driver, num):
    time.sleep(1)
    driver.save_screenshot(f'screenshot_{num}.png')
    time.sleep(1)


# Compare the screenshot of the current page to a reference image
def compare_images(driver, reference_filename, num):
    try:
        screenshot_name = f'current_page_{num}.png'



        # Take new screenshot
        driver.save_screenshot(screenshot_name)

        # Open images
        current_image = Image.open(screenshot_name)
        reference_image = Image.open(reference_filename)

        # Ensure images are same size
        if current_image.size != reference_image.size:
            current_image = current_image.resize(reference_image.size)

        # Calculate difference
        diff = ImageChops.difference(current_image, reference_image)

        diff_pixels = sum(diff.convert("L").point(bool).getdata())
        total_pixels = current_image.size[0] * current_image.size[1]
        diff_percentage = (diff_pixels / total_pixels) * 100

        # Save the difference if one exists
        if diff_percentage > 0.1:
            diff_name = f'difference_{num}.png'
            diff.convert("RGB").save(diff_name)
            raise Exception("Images do not match")

    except FileNotFoundError:
        raise Exception(f"Reference image '{reference_filename}' not found")

    except Exception as e:
        raise Exception(f"Image comparison failed: {str(e)}")


# Determine region bounds easier
def get_element_region(element):
    location = element.location
    size = element.size

    return (
        location['x'],
        location['y'],
        location['x'] + size['width'],
        location['y'] + size['height']
    )


# Compare specific regions of the current image to a reference
def compare_image_regions(driver, reference_filename, region, num):
    try:
        driver.save_screenshot(f'current_region_{num}.png')

        # Open images
        current_image = Image.open(f'current_region_{num}.png')
        reference_image = Image.open(reference_filename)

        # Crop the images to the desired region and ensure they are the same size
        current_region = current_image.crop(region)
        reference_region = reference_image.crop(region)

        if current_region.size != reference_region.size:
            current_region = current_region.resize(reference_region.size)

        # Calculate difference
        diff_bbox = ImageChops.difference(current_region, reference_region).getbbox()

        # Save the difference if one exists
        if diff_bbox:
            diff_image = ImageChops.difference(current_region, reference_region).convert("RGB")
            diff_image.save(f'difference_region_{num}.png')

            raise Exception("Images do not match")

    except FileNotFoundError:
        raise Exception(f"Reference image '{reference_filename}' not found")

    except Exception as e:
        raise Exception(f"Image comparison failed: {str(e)}")


# Compare elements which are regions of the current and reference images
def compare_elements(driver, element, reference_filename, num):
    region = get_element_region(element)
    compare_image_regions(driver,reference_filename, region, num)


# Allow the user to specify how much the program should wait
def wait(duration, unit):
    # Default is seconds
    if unit == 'minutes':
        duration *= 60  # Convert to minutes

    if unit == 'hours':
        duration *= 3600  # Convert to minutes

    print(f"Wait for {duration} {unit}")
    time.sleep(duration)
    print("Wait is over")


# Clicks on the element specified
def click(driver, element_name, current_page, config):
    # Get element info from the config based on current page
    if current_page in config and element_name in config[current_page]:
        element_info = config[current_page][element_name]
        xpath = element_info.split()[0]
    else:
        raise ElementNotFoundException(
            f"Text element '{element_name}' not found in configuration for page '{current_page}'")

    try:
        # Find and click on the element
        element = driver.find_element(By.XPATH, xpath)
        element.click()
        time.sleep(0.5)

    except NoSuchElementException:
        raise ElementNotFoundException(f"Element '{element_name}' not found on the page")

    print(f"Clicked on element : {element_name}")


def check_text(driver, element_name, current_page, config):
    # Get element info from the config based on current page
    if current_page in config and element_name in config[current_page]:
        element_info = config[current_page][element_name]
        xpath = element_info.split()[0]
        expected_properties = ' '.join(element_info.split()[1:])
    else:
        raise ElementNotFoundException(
            f"Text element '{element_name}' not found in configuration for page '{current_page}'")

    try:
        element = driver.find_element(By.XPATH, xpath)

        # Get CSS properties
        font_family = element.value_of_css_property('font-family')
        font_size = element.value_of_css_property('font-size')
        text_content = element.text

        # Get element location and basic properties
        location = element.location
        actual_properties = f"{location} {element.tag_name} {element.get_attribute('id')}{element.get_attribute('name')}"

        # Print out the characteristics
        print(f"\nChecking text element '{element_name}':")
        print(f"XPath: {xpath}")
        print(f"Text Content: {text_content}")
        print(f"Font Family: {font_family}")
        print(f"Font Size: {font_size}")
        print(f"ID: {element.get_attribute('id')}")

        # Check basic properties consistency
        if actual_properties == expected_properties:
            print(f"Element '{element_name}' properties are consistent.")
        else:
            print(f"Element '{element_name}' properties have changed.")
            print(f"Expected: {expected_properties}")
            print(f"Actual: {actual_properties}")

        # Parse expected font properties from config if available
        expected_font_info = expected_properties.split()
        expected_font = None
        expected_size = None
        expected_text = None

        # Assuming the config contains font info in a specific format
        for prop in expected_font_info:
            if prop.startswith('font='):
                expected_font = prop.split('=')[1]
            elif prop.startswith('size='):
                expected_size = prop.split('=')[1]
            elif prop.startswith('text='):
                expected_text = prop.split('=')[1]

        # Check font properties if they are specified
        font_checks = []
        if expected_font:
            font_match = expected_font.lower() in font_family.lower()
            font_checks.append(font_match)
            print(f"Font Check: {'Pass' if font_match else 'Fail'} (Expected: {expected_font}, Actual: {font_family})")

        if expected_size:
            size_match = expected_size == font_size
            font_checks.append(size_match)
            print(f"Size Check: {'Pass' if size_match else 'Fail'} (Expected: {expected_size}, Actual: {font_size})")

        if expected_text:
            text_match = expected_text == text_content
            font_checks.append(text_match)
            print(f"Text Check: {'Pass' if text_match else 'Fail'} (Expected: {expected_text}, Actual: {text_content})")

        # Return True only if all specified checks pass
        return len(font_checks) > 0 and all(font_checks)

    except NoSuchElementException:
        raise ElementNotFoundException(f"Text element '{element_name}' not found on the page.")


# Check if a button can be clicked
def check_button(driver, button_name, current_page, config):
    # Get element info from the config based on current page
    if current_page in config and button_name in config[current_page]:
        element_info = config[current_page][button_name]
        xpath = element_info.split()[0]
        expected_properties = ' '.join(element_info.split()[1:])
    else:
        raise ElementNotFoundException(f"Button '{button_name}' not found in configuration for page '{current_page}'")

    try:
        element = driver.find_element(By.XPATH, xpath)

        # Check multiple conditions for clickability
        is_present = element is not None  # Check if the button isn't null
        is_displayed = element.is_displayed()
        is_enabled = element.is_enabled()

        # Print out the characteristics
        print(f"\nChecking button '{button_name}':")
        print(f"XPath: {xpath}")
        print(f"Is Present: {is_present}")
        print(f"Is Displayed: {is_displayed}")
        print(f"Is Enabled: {is_enabled}")
        print(f"ID: {element.get_attribute('id')}")
        print(f"Name: {element.get_attribute('name')}")

        # Check the position and properties of the element
        location = element.location
        actual_properties = f"{location} {element.tag_name} {element.get_attribute('id')}{element.get_attribute('name')}"

        if actual_properties == expected_properties:
            print(f"Button '{button_name}' properties are consistent.")
        else:
            print(f"Button '{button_name}' properties have changed.")
            print(f"Expected: {expected_properties}")
            print(f"Actual: {actual_properties}")

        # If all clickability checks pass
        if all([is_present, is_displayed, is_enabled]):
            print(f"Button '{button_name}' is clickable.")
            return True
        else:
            print(f"Button '{button_name}' is not clickable.")
            return False

    except NoSuchElementException:
        raise ElementNotFoundException(f"Button '{button_name}' not found on the page.")


def check_element(driver, element_name, current_page, config):
    # Get element info from the config based on current page
    if current_page in config and element_name in config[current_page]:
        element_info = config[current_page][element_name]
        xpath = element_info.split()[0]
        expected_properties = ' '.join(element_info.split()[1:])
    else:
        raise ElementNotFoundException(
            f"Element '{element_name}' not found in configuration for page '{current_page}'")

    try:
        element = driver.find_element(By.XPATH, xpath)
        print(f"Element '{element_name}' found at XPath: {xpath}")
        print(f"ID: {element.get_attribute('id')}")
        print(f"Name: {element.get_attribute('name')}")
        print(f"XPath: {xpath}")

        # Check the position of the element
        location = element.location
        actual_properties = f"{location} {element.tag_name} {element.get_attribute('id')}{element.get_attribute('name')}"

        if actual_properties == expected_properties:
            print(f"Element '{element_name}' properties are consistent.")
        else:
            print(f"Element '{element_name}' properties have changed.")
            print(f"Expected: {expected_properties}")
            print(f"Actual: {actual_properties}")

    except NoSuchElementException:
        raise ElementNotFoundException(f"Element '{element_name}' not found on the page.")


def highlight(driver, element_name, current_page, config):
    # Get element info from the config based on current page
    if current_page in config and element_name in config[current_page]:
        element_info = config[current_page][element_name]
        xpath = element_info.split()[0]
    else:
        raise ElementNotFoundException(f"Element '{element_name}' not found in configuration for page '{current_page}'")

    try:
        # Find the element using the provided XPath
        element = driver.find_element(By.XPATH, xpath)

        # Highlight the element
        def apply_style(s):
            driver.execute_script("""
                    var element = arguments[0];
                    element.setAttribute('style', arguments[1]);
                """, element, s)

        original_style = element.get_attribute('style')
        apply_style("background: yellow; border: 2px solid red;")
        time.sleep(0.5)  # Duration for which the highlight is visible
        apply_style(original_style)  # Restore original style

        return element

    except NoSuchElementException:
        raise ElementNotFoundException(f"Element '{element_name}' not found on the page.")


# Send a command to the API
def send_serial_command(command, address):
    try:
        import telnetlib3
        import asyncio

        async def send():
            reader, writer = await telnetlib3.open_connection(
                address,
                23,  # Using port 23 like in log_handler
                connect_minwait=0.1,
                connect_maxwait=1.0
            )

            # Send the exact echo command
            echo_command = f'echo "{command}" |nc {address}:3002\r\n'
            writer.write(echo_command)
            await writer.drain()

            response = await reader.read(1024)
            writer.close()

            return response.strip()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(send())
        loop.close()

        print(f"Sent command: {command}")
        print(f"Response: {response}")

        return response, None

    except Exception as e:
        error_msg = f"Error sending command: {e}"
        print(error_msg)
        return None, error_msg

