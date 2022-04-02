import requests
from selenium import webdriver
from selenium.webdriver import ChromeOptions
import time
import yaml
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from urllib.parse import urljoin
import chromedriver_autoinstaller


def set_requests_session(driver, session):
    selenium_user_agent = driver.execute_script("return navigator.userAgent;")
    session.headers.update({"user-agent": selenium_user_agent})
    for cookie in driver.get_cookies():
        session.cookies.set(
            cookie['name'],
            cookie['value'],
            domain=cookie['domain']
        )


class LeetCodeParser():
    def __init__(self, username, password):
        self.info = {
            "id_login": username,
            "id_password": password
        }
        self.requests_session = requests.Session()
        options = ChromeOptions()
        options.add_argument('--headless')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_page_load_timeout(30)
        self.driver.implicitly_wait(3)
        self.user_agent = self.driver.execute_script(
            "return navigator.userAgent;"
        )

    def fill_element(self, element_id):
        elem = self.driver.find_element(by='id', value=element_id)
        elem.clear()
        elem.send_keys(self.info[element_id])

    def login(self):
        login_url = "https://leetcode.com/accounts/login/"
        self.driver.get(login_url)
        WebDriverWait(self.driver, 20).until(
            expected_conditions.presence_of_element_located(
                (By.ID, 'id_login')
            )
        )
        self.fill_element("id_login")
        self.fill_element("id_password")

        # self.driver.find_element(by='id', value='signin_btn').click()
        login_btn = self.driver.find_element(by='id', value='signin_btn')
        self.driver.execute_script("arguments[0].click();", login_btn)
        print("Login success!")
        time.sleep(5)

    def get_today_status(self):
        set_requests_session(self.driver, self.requests_session)
        resp = self.requests_session.post(
            "https://leetcode.com/graphql",
            params={
                'query': '\n    query questionOfToday {\n  activeDailyCodingChallengeQuestion {\n    date\n    userStatus\n    link\n    question {\n      acRate\n      difficulty\n      freqBar\n      frontendQuestionId: questionFrontendId\n      isFavor\n      paidOnly: isPaidOnly\n      status\n      title\n      titleSlug\n      hasVideoSolution\n      hasSolution\n      topicTags {\n        name\n        id\n        slug\n      }\n    }\n  }\n}\n    ',
                'variables': {}
            },
            headers={
                "content-type": "Content-Type: application/json",
                "origin": "https://leetcode.com",
                "referer": "https://leetcode.com/problemset/all/",
                "user-agent": self.user_agent,
                "x-csrftoken": dict(self.requests_session.cookies)["csrftoken"]
            }
        )
        daily_question = resp.json()["data"][
            "activeDailyCodingChallengeQuestion"
        ]
        status = daily_question["userStatus"]
        difficulty = daily_question["question"]["difficulty"]
        question_title = daily_question["question"]["title"]
        question_link = urljoin(
            "https://leetcode.com/", daily_question["link"]
        )
        return {
            "status": status,
            "difficulty": difficulty,
            "question_title": question_title,
            "question_link": question_link
        }


if __name__ == "__main__":
    chromedriver_autoinstaller.install()
    with open("user_info.yaml", "r") as f:
        user_info = yaml.safe_load(f)
    lc_parser = LeetCodeParser(user_info["username"], user_info["password"])
    lc_parser.login()
    today_status = lc_parser.get_today_status()
    print(today_status)
