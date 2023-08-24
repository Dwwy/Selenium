import datetime
import os
import time
import pandas as pd
import pymongo
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import certifi
import code
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
import calendar

urlNotScrapped = []
twitterUserEmail= ""
twitterUserName =  ""
twitterPassword = ""
def initialiseMongo():
    client = pymongo.MongoClient("")
    db = client["Test"]
    global collection
    collection = db["Tweets"]
def initialiseDriver():
    options = Options()
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--verbose")
    options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    # options.add_argument('--disable-dev-shm-usage')
    # options.add_argument('--no-sandbox')
    # options.add_argument(r"--user-data-dir=/Users/danielwong/Library/Application Support/Google/Chrome")
    # options.add_argument(r"--profile-directory=Profile 1")
    global driver
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

def TwitterSignInSequence(twitter_user_email = twitterUserEmail, twitter_username = twitterUserName, twitter_password = twitterPassword):
    # driver.get("https://twitter.com/login")
    driver.get("https://tweetdeck.twitter.com/")

    time.sleep(4)
    try:
        driver.find_element(By.XPATH,'//div[@class="css-18t94o4 css-1dbjc4n r-1niwhzg r-sdzlij r-1phboty r-rs99b7 r-1kb76zh r-2yi16 r-1qi8awa r-1ny4l3l r-ymttw5 r-o7ynqc r-6416eg r-lrvibr"]').click()
        time.sleep(4)
    except Exception as e:
        print(e)
    try:
        email = driver.find_element(By.XPATH, "//input[@name='text']")
        email.send_keys(twitter_user_email)
        email.send_keys(Keys.RETURN)
        time.sleep(2)
    except Exception as e:
        print(e)
    try:
        username = driver.find_element(By.XPATH, "//input[@name='text']")
        username.send_keys(twitter_username)
        username.send_keys(Keys.RETURN)
        time.sleep(2)
    except Exception as e:
        print(e)
    try:
        password = driver.find_element(By.XPATH, "//input[@name='password']")
        password.send_keys(twitter_password)
        password.send_keys(Keys.RETURN)
        time.sleep(7)
    except Exception as e:
        print(e)

def concatenate_keywords(keywords):
    formatted_keywords = ' '.join(keywords)
    return f'{formatted_keywords}'

def clickSearchTweet ():
    try:
        search_button = driver.find_element(By.XPATH, '//div[@aria-label="Search Tweets"]')
        ActionChains(driver).move_to_element(search_button).click().perform()
        time.sleep(2)
        return True
    except:
        return False

def findSelect(labelText):
    wait = WebDriverWait(driver, 10)
    container_element = wait.until(EC.visibility_of_element_located((By.XPATH, f"//div[contains(label, '{labelText}')]")))
    label_element = container_element.find_element(By.XPATH, f".//label[contains(., '{labelText}')]")
    select_element = container_element.find_element(By.XPATH, ".//select")
    select = Select(select_element)
    wait.until(EC.presence_of_all_elements_located((By.XPATH, "//option")))
    return select_element, select

def connect_url():
    time.sleep(3)
    Data_List = []
    content_header = 'tweetText'
    alliance_name_header = 'css-901oao css-1hf3ou5 r-1bwzh9t r-18u37iz r-37j5jr r-1wvb978 r-a023e6 r-16dba41 r-rjixqe r-bcqeeo r-qvutc0'
    username_header = 'User-Name' #data-testid
    total_scraped_tweets = 0
    page = 0
    max_height = 80000
    body = driver.find_element(By.XPATH, "//div[@data-viewportview='true']")
    trialCount = 5
    i = 0
    while True:
        try:
            retryButton = driver.find_element(By.XPATH, "//div[@role='button']//span[text()='Retry']")
            retryButton.click()
            time.sleep(2)
        except:
            pass

        last_height = driver.execute_script("return arguments[0].scrollTop", body)
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", body)
        new_height = driver.execute_script("return arguments[0].scrollTop", body)
        if i == (trialCount - 1) and new_height == last_height:
            driver.execute_script("arguments[0].scrollTop = 0", body)
            max_height = new_height
            break
        elif new_height == last_height:
            driver.execute_script("arguments[0].scrollTop -= 1000;", body)
            time.sleep(2)
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", body)
            i += 1
        time.sleep(2)
        if new_height >= max_height:
            max_height = new_height
            driver.execute_script("arguments[0].scrollTop = 0", body)
            break


    while True:
        try:
            js = 'arguments[0].scrollTop += 1000'
            driver.execute_script(js, body)
            html = driver.page_source.encode('utf-8')
            soup = BeautifulSoup(html, 'html.parser')
            main_div = soup.find(
                'div', {'class': 'css-1dbjc4n r-13qz1uu'})
            divs = main_div.find_all('article', {'data-testid': 'tweet'})
            page += 1
            print('Fetching data on page {}！！！'.format(page))
            previous_scraped_tweets = total_scraped_tweets
            last_height = driver.execute_script("return arguments[0].scrollTop", body)
            for div in divs:
                data_list = []

                try:
                    content = div.find('div', {
                        'data-testid': content_header}).get_text()
                    data_list.append(str(content).strip().replace('\n', ' '))
                except:
                    continue
                user_name = div.find(
                    'div', {
                        'data-testid': username_header})
                alliance_name_div = user_name.find(
                    'div', {
                        'class': 'css-1dbjc4n r-18u37iz r-1wbh5a2 r-13hce6t'})
                alliance_name = alliance_name_div.find('span').get_text()
                data_list.append(alliance_name)
                name_div = user_name.find(
                    'div', {
                        'class': 'css-1dbjc4n r-1awozwy r-18u37iz r-1wbh5a2 r-dnmrzs'})
                name = name_div.find('span').get_text()
                data_list.append(name)
                date = div.find('time')["datetime"]
                datetime_obj = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
                formatted_datetime = datetime_obj.strftime("%b %d, %Y %H:%M:%S")

                data_list.append(formatted_datetime)

                Data_List.append(data_list)
                total_scraped_tweets += 1
            time.sleep(3)
        except Exception as e:
            print(e)
        if last_height == max_height or last_height > max_height or abs(last_height - max_height) <= 1000:
            # Break the loop when no new tweets are loaded
            break

    print('第 {} 个URL信息已获取完毕。'.format(i))
    i = i + 1


    Data_List_New = []
    for data in Data_List:
        if data not in Data_List_New:
            Data_List_New.append(data)
    return Data_List_New
# def fillInKeywords(keywords):
#     try:
#         includeAll = driver.find_element(By.XPATH, '//textarea[@name="includeAllOfTheseWords"]')
#         includeExact = driver.find_element(By.XPATH, '//textarea[@name="includeExactPhrase"]')
#         includeAll.clear()
#         includeExact.clear()
#         includeAny = driver.find_element(By.XPATH, '//textarea[@name="includeAnyOfTheseWords"]')
#         includeAny.clear()
#         includeAny.send_keys(concatenate_keywords(keywords))
#         time.sleep(3)
#     except:
#         driver.refresh()
#         time.sleep(3)
#         fillInKeywords(keywords)


def searchCriteria (keywords , fromDate):
    attempt = 2
    i = 0
    while i < attempt:
        try:
            include = driver.find_element(By.XPATH,
                                          '//div[@class="css-18t94o4 css-1dbjc4n r-1awozwy r-18u37iz r-1wtj0ep r-1ny4l3l r-1e081e0 r-1yzf0co r-o7ynqc r-6416eg"]')
            include.click()
            time.sleep(2)
            includeAll = driver.find_element(By.XPATH, '//textarea[@name="includeAllOfTheseWords"]')
            includeExact = driver.find_element(By.XPATH, '//textarea[@name="includeExactPhrase"]')
            includeAll.clear()
            includeExact.clear()
            includeAny = driver.find_element(By.XPATH, '//textarea[@name="includeAnyOfTheseWords"]')
            includeAny.clear()
            includeAny.send_keys(concatenate_keywords(keywords))
            time.sleep(3)
            include.click()
            time.sleep(2)
            break
        except:
            searchTweet = clickSearchTweet()
            if not searchTweet and i == attempt - 1:
                driver.refresh()
                i = 0
            i += 1
            continue



    for i in range(2):
        try:
            timeFilter = driver.find_element(By.XPATH,
                                             '//div[@class="css-18t94o4 css-1dbjc4n r-1awozwy r-18u37iz r-1wtj0ep r-1ny4l3l r-1e081e0 r-1yzf0co r-o7ynqc r-6416eg"]//span[text()="Time and location"]')
            timeFilter.click()
            time.sleep(2)
            break
        except:
            continue
    wait = WebDriverWait(driver, 10)
    # try:
    #     select_element, select = wait.until(EC.element_to_be_clickable((By.ID, "SELECTOR_2")))
    # except:
    #     time.sleep(3)
    #     timeFilter = driver.find_element(By.XPATH,
    #                                      '//div[@class="css-18t94o4 css-1dbjc4n r-1awozwy r-18u37iz r-1wtj0ep r-1ny4l3l r-1e081e0 r-1yzf0co r-o7ynqc r-6416eg"]//span[text()="Time and location"]')
    #     timeFilter.click()
    #     time.sleep(2)
    #     select_element = wait.until(EC.element_to_be_clickable((By.ID, "SELECTOR_2")))
    #
    # select = Select(select_element)
    # wait.until(EC.presence_of_all_elements_located((By.XPATH, "//option")))
    select_element, select = findSelect('Time')
    select.select_by_visible_text("Within a time frame")
    time.sleep(1)
    select_element, select = findSelect('Start time')
    select_element.click()
    interval = datetime.timedelta(days=1)
    endDate = fromDate + interval
    # fromDate = fromDate - interval

    year = str(fromDate.year)
    month = calendar.month_name[fromDate.month]
    day = str(fromDate.day)

    select_element, select = findSelect('Month')
    select.select_by_visible_text(month)
    select_element, select = findSelect('Day')
    select.select_by_visible_text(day)
    select_element, select = findSelect('Year')
    select.select_by_visible_text(year)
    doneButton = wait.until(
        EC.visibility_of_element_located((By.XPATH, "//div/div/span/span[contains(text(), 'Done')]")))
    doneButton.click()

    select_element, select = findSelect('End time')
    select_element.click()

    year = str(endDate.year)
    month = calendar.month_name[endDate.month]
    day = str(endDate.day)

    select_element, select = findSelect('Month')
    select.select_by_visible_text(month)
    select_element, select = findSelect('Day')
    select.select_by_visible_text(day)
    select_element, select = findSelect('Year')
    select.select_by_visible_text(year)
    doneButton = wait.until(
        EC.visibility_of_element_located((By.XPATH, "//div/div/span/span[contains(text(), 'Done')]")))
    doneButton.click()
    time.sleep(2)
    closeButton = wait.until(
        EC.visibility_of_element_located((By.XPATH, "//div/div/span/span[contains(text(), 'Close')]")))
    closeButton.click()

def scrape(keywords, fromDate):
    searchCriteria(keywords, fromDate)
    df = connect_url()
    df_Sheet = pd.DataFrame(df, columns=[
        'content', 'name', 'userName', 'date'])
    collection.insert_many(df_Sheet.to_dict(orient='records'))
    driver.refresh()
    time.sleep(5)



def run():
    initialiseDriver()
    initialiseMongo()
    TwitterSignInSequence()
    keywords = ["bitcoin", "btc"]
    year = 2021
    month = 12
    last_day = calendar.monthrange(year, month)[1]
    fromDate = datetime.datetime(year, month, 31, 0, 0, 0)
    # endDate = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    endDate = datetime.datetime(year, month, last_day, 0, 0, 0)
    interval = datetime.timedelta(days=1)
    while fromDate <= endDate:
        print("Scraping tweets from " + str(fromDate.date()))
        scrape(keywords,fromDate)
        fromDate = fromDate + interval


run()
code.interact(local=globals())
