import requests
from selenium import webdriver
from selenium.webdriver.common.by import By


def login_via_api(username, password):
    response = requests.post("https://example.com/api/login", json={
        "username": username,
        "password": password
    })
    return response.json()


def get_page_title(driver):
    return driver.find_element(By.TAG_NAME, "h1").text
