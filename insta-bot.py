"""
An Instagram bot written in Python using Selenium on Google Chrome. 
It will go through posts in hashtag(s) and like and comment on them.
"""

# Built-in/Generic Imports
from time import sleep
import logging
import sys, json
from random import randint

# Library Imports
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager as CM
from tkinter import *
from tkinter.scrolledtext import ScrolledText



logging.basicConfig(format='%(levelname)s [%(asctime)s] %(message)s', datefmt='%m/%d/%Y %r', level=logging.INFO)
logger = logging.getLogger()

#GUI
def insert_entry(container, string_to_i, row, column):
    entry_widget = Entry(container)
    entry_widget.insert("end", string_to_i)
    entry_widget.grid(row=row, column=column)
    return entry_widget

def initialize_browser():

    # Do this so we don't get DevTools and Default Adapter failure
    options = webdriver.ChromeOptions()
    # options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # options.add_argument("--log-level=3")

    # Initialize chrome driver and set chrome as our browser
    browser = webdriver.Chrome(executable_path=CM().install(), options=options)

    return browser


def login_to_instagram(browser):
    browser.get('https://www.instagram.com/')
        
    sleep(2)

    # Get the login elements and type in your credentials
    with open("data/database.json", "r") as file:
        database = json.load(file)

    browser.implicitly_wait(30)
    username = browser.find_element_by_name('username')
    username.send_keys(database['credentials']['username'])
    browser.implicitly_wait(30)
    password = browser.find_element_by_name('password')
    password.send_keys(database['credentials']['password'])

    sleep(2)

    # Click the login button
    browser.implicitly_wait(30)
    browser.find_element_by_xpath("//*[@id='loginForm']/div/div[3]/button").click()

    # If login information is incorrect, program will stop running
    browser.implicitly_wait(30)
    try:
        if browser.find_element_by_xpath("//*[@id='slfErrorAlert']"):
            browser.close()
            sys.exit('Error: Login information is incorrect')
        else:
            pass
    except:
        pass

    browser.implicitly_wait(30)
    
    logger.info('Logged in to '+ database['credentials']['username'])

    # Save your login info? Not now
    browser.implicitly_wait(30)
    browser.find_element_by_xpath("//*[@id='react-root']/section/main/div/div/div/div/button").click()

    # Turn on notifications? Not now
    browser.implicitly_wait(30)
    browser.find_element_by_xpath("/html/body/div[4]/div/div/div/div[3]/button[2]").click()

def automate_instagram(browser):
    # Keep track of how many you like and comment
    likes = 0
    comments = 0

    with open("data/database.json", "r") as file:
        database = json.load(file)

    for hashtag in database['hashtags']:
        browser.implicitly_wait(30)
        browser.get(f'https://www.instagram.com/explore/tags/{hashtag}/')
        logger.info(f'Exploring #{hashtag}')
        sleep(randint(1,2))

        # Click first thumbnail to open
        browser.implicitly_wait(30)
        first_thumbnail = browser.find_element_by_xpath("//*[@id='react-root']/section/main/article/div[1]/div/div/div[1]/div[1]/a/div/div[2]")
        first_thumbnail.click()

        sleep(randint(1,2))

        # Go through x number of photos per hashtag
        for post in range(1,database['number_of_posts']):

            
            try:
                if database['like'] == True:
                    # Like
                    browser.implicitly_wait(30)
                    browser.find_element_by_xpath("/html/body/div/div[2]/div/article/div[3]/section[1]/span[1]/button").click()
                    logger.info("Liked")
                    likes += 1

                sleep(randint(2,4))

                # Comment
                try:
                    browser.implicitly_wait(30)
                    browser.find_element_by_xpath("//form").click()
                    # Random chance of commenting
                    do_i_comment = randint(1,database['chance_to_comment'])
                    if do_i_comment == 1:

                            browser.implicitly_wait(30)
                            comment = browser.find_element_by_xpath("//textarea")

                            sleep(randint(database['wait_to_comment']['min'], database['wait_to_comment']['max']))

                            rand_comment_index = randint(0,len(database['comment_list']))
                            comment.send_keys(database['comment_list'][rand_comment_index])
                            comment.send_keys(Keys.ENTER)
                            logger.info('Commented ' + database['comment_list'][rand_comment_index])
                            comments += 1
                            sleep(randint(database['wait_between_posts']['min'], database['wait_between_posts']['max']))

                except Exception:
                    # Continue to next post if comments section is limited or turned off
                    pass

            except Exception:
                # Already liked it, continue to next post
                logger.info('Already liked this photo previously')
                pass
            
            # Go to next post
            browser.implicitly_wait(30)
            browser.find_element_by_link_text('Next').click()
            logger.info('Getting next post')
            sleep(randint(database['wait_between_posts']['min'], database['wait_between_posts']['max']))    

    logger.info(f'Liked {likes} posts')
    logger.info(f'Commented on {comments} posts')

    # Close browser when done
    logger.info('Closing chrome browser...')
    browser.close()




# settings window
def setting_ui():
    def save_setting():

        if str(like_f.get()) == "yes":
            like_var = True
        else:
            like_var = False

        

        setting_dict = {
            "credentials": {
                "username": username_f.get(),
                "password": password_f.get()
            },

            "hashtags": [
                hashtag
                for hashtag in hashtag_list_f.get("1.0", "end-1c").split("\n")
                if hashtag or not hashtag.isspace()
            ],

            "comment_list": [
                comment
                for comment in comment_box_f.get("1.0", "end-1c").split("\n")
                if comment or not comment.isspace()
            ],

            "number_of_posts": int(max_post_f.get()),

            "chance_to_comment": int(chance_f.get()),

            "wait_between_posts": {
                "min" : int(wait_p1_f.get()),
                "max": int(wait_p2_f.get())
            },
            
            "wait_to_comment": {
                "min" : int(wait_c1_f.get()),
                "max": int(wait_c2_f.get())
            },

            "like": like_var
            
        }

        with open("data/database.json", "w") as file:
            json.dump(setting_dict, file)
        setting_root.destroy()
    

    with open("data/database.json", "r") as file:
        setting = json.load(file)
    
    if setting['like'] == True:
            l_placeholder = 'yes'
    else:
        l_placeholder = 'no'

    setting_root = Tk()
    setting_root.resizable(False, False)
    setting_root.title('Bot Settings')

    Label(setting_root, text="USERNAME", width=25).grid(row=0, column=0)
    Label(setting_root, text="PASSWORD", width=25).grid(row=1, column=0)

    Label(setting_root, text="HASHTAGS", width=25).grid(row=2, column=0)
    Label(setting_root, text="COMMENTS", width=25).grid(row=3, column=0)
    Label(setting_root, text="NUMBER OF POST TO COMMENT",width=25).grid(row=4, column=0)
    Label(setting_root, text="CHANCE TO COMMENT", width=25).grid(row=5, column=0)
    Label(setting_root, text="WAIT BETWEEN POSTS (MIN)",width=25).grid(row=6, column=0)
    Label(setting_root, text="WAIT BETWEEN POSTS (MAX)",width=25).grid(row=7, column=0)
    Label(setting_root, text="WAIT TO COMMENT (MIN)",width=25).grid(row=8, column=0)
    Label(setting_root, text="WAIT TO COMMENT (MAX)",width=25).grid(row=9, column=0)
    Label(setting_root, text="DO YOU WANT TO LIKE",width=25).grid(row=10, column=0)

    username_f = insert_entry(setting_root, setting["credentials"]['username'], 0, 1)
    password_f = insert_entry(setting_root, setting["credentials"]['password'], 1, 1)
    
    hashtag_list_f = ScrolledText(setting_root, width=25, height=6)
    hashtag_list_f.insert("1.0", "\n".join(setting["hashtags"]))
    hashtag_list_f.grid(row=2, column=1)

    comment_box_f = ScrolledText(setting_root, width=25, height=6)
    comment_box_f.insert("1.0", "\n".join(setting["comment_list"]))
    comment_box_f.grid(row=3, column=1)

    max_post_f = insert_entry(setting_root, setting["number_of_posts"], 4, 1)
    chance_f = insert_entry(setting_root, setting["chance_to_comment"], 5, 1)
    wait_p1_f = insert_entry(setting_root, setting["wait_between_posts"]["min"], 6, 1)
    wait_p2_f = insert_entry(setting_root, setting["wait_between_posts"]["max"], 7, 1)
    wait_c1_f = insert_entry(setting_root, setting["wait_to_comment"]["min"], 8, 1)
    wait_c2_f = insert_entry(setting_root, setting["wait_to_comment"]["max"], 9, 1)
    like_f = insert_entry(setting_root, l_placeholder, 10, 1)

    Button(setting_root,
                   text="SAVE",
                   bg="#33571c",
                   fg='#ffffff',
                   command=save_setting,
                   width=25).grid(row=11, column=1)

    setting_root.mainloop()

def run_engine():
    browser = initialize_browser()
    login_to_instagram(browser)
    automate_instagram(browser)

if __name__ == "__main__":
    root = Tk()
    root.title('Instagram Comment/Like Bot')
    root.resizable(False, False)
    root.geometry("520x460")
    main_button = Button(root,
                                text="START BOT",
                                bg='#292929',
                                fg='#ffffff',
                                font=25,
                                command=run_engine,
                                width=25).place(relx=0.3, rely=0.5)
    Button(root, text="COMMENT BOT SETTING", command=setting_ui,
                width=25).place(relx=0.35, rely=0.6)

    root.mainloop()
    
