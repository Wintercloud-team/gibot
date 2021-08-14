from __future__ import print_function, unicode_literals
from pprint import pprint
from PyInquirer import prompt, Separator
from examples import custom_style_2
import os
import requests
import sqlite3


#Prechecking, setting up, creating DB
con = sqlite3.connect("datas.db")
cur = con.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
if str(cur.fetchall()) != "[('saves',)]":
    cur.execute("""CREATE TABLE saves
                    (username text, email text, api_token text, auto text)""")
    cur.execute("""INSERT INTO saves VALUES ('your username', 'your email', 'your api', 'useless, just ignore')""")
    con.commit()
#--------------------------------------------------

#Data base
user_upd = ("""Update saves set username = ?""")
email_upd = ("""Update saves set email = ?""")
api_upd = ("""Update saves set api_token = ?""")
auto_upd = ("""Update saves set auto = ?""")
user_from_db = str(cur.execute("""SELECT username FROM saves""").fetchall()[0][0])
email_from_db = str(cur.execute("""SELECT email FROM saves""").fetchall()[0][0])
api_from_db = str(cur.execute("""SELECT api_token FROM saves""").fetchall()[0][0])
auto_from_db = str(cur.execute("""SELECT auto FROM saves""").fetchall()[0][0])

#Starting
repos = []
#--------------------------------------------------

#Main vars
GH_API_TOKEN = api_from_db
GH_USER = user_from_db
GH_EMAIL = email_from_db
NEW_REPO_NAME = ""
name_of_folder = ""
api_for_print = api_from_db[0:4]+("*"*32)+api_from_db[36:40]
answer = ""
answers = ""
confirming = False
def menu(view, name, message, choises):
    global answer
    global answers
    questions = [{
        "type": f"{view}",
        "name": f"{name}",
        "message": f"{message}",
        "choices": choises
    }]
    answers = prompt(questions, style=custom_style_2)
    answer = str(answers[f"{name}"])
def confirming():
    global answer
    global answers
    questions = [
    {
        'type': 'confirm',
        'message': 'Repo | %s |, continue?' %answer,
        'name': 'continue',
        'default': True,
    }
]
    answers = prompt(questions, style=custom_style_2)
    pprint(answers)
#--------------------------------------------------

#Path and folders
path = os.path.dirname(__file__)
content = os.listdir(str(path+"/"))
contlist = []
#--------------------------------------------------


os.system(f"git config --global user.name {GH_USER}")
os.system(f"git config --global user.email {GH_EMAIL}")
os.system("clear")

answer = ""

#Starting
def start():
    os.system("clear")
    menu("list", "start", "", ["Local", "Github", "Settings"])
    if answer == "Settings":
        sett()
    elif answer == "Github":
        github_parse()
    else: par_ch()

#Parsing from Github and uploading
def github_parse():
    os.system("clear")
    global repos
    repos = []
    headers = {
                    "Authorization": f"token {GH_API_TOKEN}"
            }
    response = requests.get('https://api.github.com/user/repos', headers=headers)
    json_answer = response.json()
    for list in json_answer:
        repos.append(list["name"])
    repos.append(Separator())
    repos.append("Back")
    menu("list", "start", "Choose your repo", repos)
    repos = answer
    if answer == "Back":
        start()
    else:
        os.system("clear")
        confirming()
        if answers["continue"] == True:
            print("CLONING...")
            os.system(f"cd "+path+"/"+f" && git clone https://{GH_USER}:{GH_API_TOKEN}@github.com/{GH_USER}/{answer}")
#AAAAAAAAAAAAAAAAAAA

#MAIN MODULE folders parsing and choosing
def par_ch():
    contlist = []
    for i, name in enumerate(content):
        if os.path.isdir(path+"/"+name):
            contlist.append(name)
    contlist.append(Separator())
    contlist.append("Back")
    menu("list", "ch", "Choose folder", contlist)
    global name_of_folder
    name_of_folder = str(answers["ch"])
    global NEW_REPO_NAME
    NEW_REPO_NAME = name_of_folder
    if answer == "Back":
        start()
    else: dwnld_yn()
#--------------------------------------------------

#Accepting Upload
def dwnld_yn():
    os.system("clear")
    confirming()
    if answers["continue"] == True:
        checkin()
#--------------------------------------------------

#Checking if choosed repository exist with options
def checkin():
        os.system("clear")
        headers = {
                "Authorization": f"token {GH_API_TOKEN}"
        }
        response = requests.get('https://api.github.com/user/repos', headers=headers)
        json_str = str(response.json())
        json_count = json_str.count(f"'{name_of_folder}'")
        if json_count >= 1:
            menu("list", "ch", "The repository exist", ["Refresh", "Replace with local", "Delete"])
            #OPTION refresh
            if answers["ch"] == "Refresh":
                message = str(input("Commit message: "))
                print("\nREFRESHING...\n")
                headers = {
                            "Authorization": f"token {GH_API_TOKEN}",
    }
                data = '{"name":"%s"}' % NEW_REPO_NAME

                response = requests.patch('https://api.github.com/repos/FGamer112/%s'%name_of_folder, headers=headers, data=data, auth=(f"{GH_USER}", f"{GH_API_TOKEN}"))
                print(f"Status-code: {response.status_code}\n")
                os.system("cd "+path+"/"+name_of_folder+f" && git init && git add . && git branch -M main && git commit -m '{message}' && git config remote.origin.url https://{GH_USER}:{GH_API_TOKEN}@github.com/{GH_USER}/{name_of_folder} && git remote add origin https://github.com/FGamer112/MyTelega.git && git push https://{GH_USER}:{GH_API_TOKEN}@github.com/{GH_USER}/{name_of_folder}.git -u origin/main --all")
            #--------------------------------------------------

            #OPTION Replace with local repo
            elif answers["ch"] == "Replace with local":
                #Deleting
                print("\nDELETING...\n")
                headers = {
                            "Authorization": f"token {GH_API_TOKEN}",
    }
                response = requests.delete('https://api.github.com/repos/FGamer112/%s'%name_of_folder, headers=headers)
                print(f"Status-code: {response.status_code}\n")
                #Uploading
                print("\nUPLOADING...")
                headers1 = {
                            "Authorization": f"token {GH_API_TOKEN}"
    }
                data1 = '{"name": "%s", "private": "True"}' % NEW_REPO_NAME
                response1 = requests.post('https://api.github.com/user/repos', headers=headers1, data=data1)
                print(f"Status-code: {response1.status_code}\n")
                os.system("cd "+path+"/"+name_of_folder+f" && git init && git add . && git config remote.origin.url https://{GH_USER}:{GH_API_TOKEN}@github.com/{GH_USER}/{name_of_folder} && git commit -m 'update' && git branch -M main && git push -u origin main && git remote add origin https://{GH_USER}:{GH_API_TOKEN}@github.com/{GH_USER}/{name_of_folder}.git && git push https://{GH_USER}:{GH_API_TOKEN}@github.com/{GH_USER}/{name_of_folder}.git -u origin main")
            #--------------------------------------------------

            #OPTION Delete
            elif answers["ch"] == "Delete":
                print("\nDELETING...\n")
                headers = {
                            "Authorization": f"token {GH_API_TOKEN}",
    }
                response = requests.delete('https://api.github.com/repos/FGamer112/%s'%name_of_folder, headers=headers)
                print(f"Status-code: {response.status_code}\n")
            #--------------------------------------------------
        else:
            just_dwnld()
#--------------------------------------------------

#Settings
def sett():
        os.system("clear")
        global user_from_db
        global email_from_db
        global api_from_db
        global auto_from_db
        print(f"Username: {user_from_db}\nEmail: {email_from_db}\nApi: {api_from_db}\nUpdates: {auto_from_db}\n")
        alt = [
            {
                'type': 'list',
                'name': 'settings',
                'message': 'Settings',
                'choices':
                [
                    {'name':'Username'},
                    {'name':'Email'},
                    {'name':'API-token'},
                    {'name':'Self-updates (useless for now, just ignore)'},
                    {'name':'Back'}
                ]
            }
        ]
        alt_answers = prompt(alt, style=custom_style_2)
        alt_answer = str(alt_answers["settings"])
        pprint(alt_answers)
        if alt_answer == "Username":
            user = str(input("Enter username: "))
            cur.execute(user_upd, (user,))
            con.commit()
            pprint(alt_answers)
            user_from_db = user
            sett()
        elif alt_answer == "Email":
            email = str(input("Enter Email: "))
            cur.execute(email_upd, (email,))
            con.commit()
            pprint(alt_answers)
            email_from_db = email
            sett()
        elif alt_answer == "API-token":
            api = str(input("Enter API-token: "))
            cur.execute(api_upd, (api,))
            con.commit()
            pprint(alt_answers)
            api_from_db = api
            sett()
        elif alt_answer == "Self-updates":
            auto = str(input("Enter value: "))
            cur.execute(auto_upd, (auto,))
            con.commit()
            pprint(alt_answers)
            auto_from_db = auto
            sett()
        elif alt_answer == "Back":
            start()
#--------------------------------------------------

#Uploading only
def just_dwnld():
        os.system("clear")
        print("\nUploading\n")
        print(NEW_REPO_NAME)
        headers = {
                    "Authorization": f"token {GH_API_TOKEN}"
        }
        data = '{"name": "%s", "private": "True"}' % NEW_REPO_NAME
        response = requests.post('https://api.github.com/user/repos', headers=headers, data=data)
        print(f"Status-code: {response.status_code}\n")
        os.system("cd "+path+"/"+name_of_folder+f" && git init && git add . && git config remote.origin.url https://{GH_USER}:{GH_API_TOKEN}@github.com/{GH_USER}/{name_of_folder} && git commit -m 'update' && git branch -M main && git push -u origin main && git remote add origin https://{GH_USER}:{GH_API_TOKEN}@github.com/{GH_USER}/{name_of_folder}.git && git push https://{GH_USER}:{GH_API_TOKEN}@github.com/{GH_USER}/{name_of_folder}.git -u origin main")
#--------------------------------------------------
start()