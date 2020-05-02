from locust import HttpLocust, TaskSet, between
from bs4 import BeautifulSoup
from faker import Faker
import random, time

USER_CREDENTIALS = [
    ("thomaswolf", "thomaswolf"),
    ("susanwilliams", "susanwilliams"),
    ("student_01", "student_01"),
    ("shaunberkley", "shaunberkley"),
    ("robertandrews", "robertandrews"),
    ("petershaw", "petershaw"),
    ("paulharris", "paulharris"),
    ("michelleclark", "michelleclark"),
    ("ironman", "ironman"),
    ("EAA_official", "EAA_official"),
    ("chrishall", "chrishall"),
    ("alisonhendrix", "alisonhendrix"),
]

def is_static_file(f):
    if "/sites/default/files" in f:
        return True
    else:
        return False

def fetch_static_assets(session, response):
    resource_urls = set()
    soup = BeautifulSoup(response.text, "html.parser")

    # Look through the code to find static assets that can be called.
    for res in soup.find_all(src=True):
        url = res['src']
        if is_static_file(url):
            resource_urls.add(url)

    for url in set(resource_urls):
        # Retrieve static files.
        session.client.get(url, name="(Static File)")

def index(self):
    # Go to the homepage and fetch static assets.
    response = self.client.get("/")
    fetch_static_assets(self, response)

def about(self):
    # Go to the about page and fetch static assets.
    response = self.client.get("/about")
    fetch_static_assets(self, response)

def createTopic(self):
    # Go to the add topic page and fetch static assets.
    response = self.client.get("/node/add/topic")
    fetch_static_assets(self, response)

    # Find the Drupal form build id and token.
    content = BeautifulSoup(response.content, "html.parser")
    build_id = content.body.find('input', {'name': 'form_build_id'})['value']
    form_token = content.body.find('input', {'data-drupal-selector': 'edit-node-topic-form-form-token'})['value']

    # Submit the form.
    fake = Faker()
    response = self.client.post("/node/add/topic", {
        "title[0][value]": fake.sentence(),
        "body[0][value]": fake.text(),
        "field_topic_type": 1,
        "groups": "_none",
        "field_content_visibility": "community",
        "field_topic_comments[0][status]": 2,
        "status[value]": 1,
        "form_build_id": build_id,
        "form_token": form_token,
        "form_id": "node_topic_form",
        "op": "Save"
    })
    fetch_static_assets(self, response)

def drupalLogin(self):
    # Get a random user to login with.
    username, password = random.choice(USER_CREDENTIALS)

    # Go to the user login page and fetch static assets.
    response = self.client.get("/user/login")
    fetch_static_assets(self, response)

    # Find the Drupal form build id.
    content = BeautifulSoup(response.content, "html.parser")
    build_id = content.body.find('input', {'name': 'form_build_id'})['value']

    # Submit the login form.
    response = self.client.post("/user/login", {
        "name_or_mail": username,
        "pass": password,
        "form_id": "social_user_login_form",
        "form_build_id": build_id,
        "op": "Log in"
    })
    fetch_static_assets(self, response)

def drupalLogout(self):
    # Go to the logout page and fetch static assets.
    response = self.client.get("/user/logout")
    fetch_static_assets(self, response)

class UserBehavior(TaskSet):
    # Switch randomly between different tasks.
    tasks = {index: 1, about: 1, createTopic: 1}

    def on_start(self):
        drupalLogin(self)

    def on_stop(self):
        drupalLogout(self)

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    wait_time = between(5.0, 9.0)
