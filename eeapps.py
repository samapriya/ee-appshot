import requests
import os
import json
import pendulum
import sys
from bs4 import BeautifulSoup

date = str(pendulum.now()).split("T")[0]
pathway = os.path.dirname(os.path.realpath(__file__))
path = os.path.join(pathway, "EE-Apps_" + date)
infile = os.path.join(pathway, "eeuser.json")


BASE_URL = ".users.earthengine.app"


def jsext(urllist, folder):
    for i, url in enumerate(urllist):
        username = url.split(".user")[0].split("https://")[1]
        app_name = url.split("/")[-1]
        # print(username,app_name)
        if not os.path.exists(os.path.join(folder, username)):
            os.makedirs(os.path.join(folder, username))
        try:
            local_path = os.path.join(folder, username, f"{app_name}.js")
        except TypeError:
            local_path = os.path.join(
                folder, username, f"{app_name.encode('utf-8')}.js"
            )
        print(f"Writing {i+1} of {len(urllist)} apps")
        try:
            source = requests.get(url)
            html_content = source.text
            soup = BeautifulSoup(html_content, "html.parser")
            for articles in soup.find_all("script"):
                if not articles.string == None and articles.string.strip().startswith(
                    "init"
                ):
                    url = articles.string.strip().split('"')[1]
                    if url.startswith("https"):
                        iscript = requests.get(url).json()
                        pt = iscript["path"]
                        scr = iscript["dependencies"][pt]
                        if not os.path.exists(local_path):
                            try:
                                file = open(local_path, "w", encoding="utf-8")
                                file.write(str(iscript["dependencies"][pt]).strip())
                                file.close()
                                clean_lines = []
                                with open(local_path, "r", encoding="utf-8") as f:
                                    lines = f.readlines()
                                    clean_lines = [
                                        l.strip("\n") for l in lines if l.strip()
                                    ]
                                with open(local_path, "w", encoding="utf-8") as f:
                                    f.writelines("\n".join(clean_lines))
                            except Exception as e:
                                print(e)
        except Exception as e:
            print(e)


def merge_dictionary_list(dict_list):
    return {
        k: [d.get(k) for d in dict_list if k in d]  # explanation A
        for k in set().union(*dict_list)  # explanation B
    }


app_urls = []
json_app_urls = []


def jurl(folder, user_list):
    for user in user_list:
        url = f"https://{user}{BASE_URL}"
        try:
            source = requests.get(url).text
            soup = BeautifulSoup(source, "lxml")

            for article in soup.find_all("div", class_="mdl-grid"):
                for li in article.find_all("a"):
                    url = li["href"]
                    name = li.get_text().strip()
                    app_urls.append(str(url))
                    json_app_urls.append({user: str(url)})
                    print(f"Total unique url : {len(set(app_urls))}", end="\r")
        except Exception as e:
            pass
    unique_url = list(set(app_urls))

    return unique_url, json_app_urls


ulist = []


def eeapps(folder):
    try:
        folder = os.path.join(
            folder.encode("utf-8"), "EE-Apps_" + str(date).encode("utf-8")
        )
    except TypeError:
        folder = os.path.join(folder, "EE-Apps_" + date)
    try:
        with open("eeuser.json") as f:
            data = json.load(f)
            repo_user_list = [users.split("users/")[-1].split("/")[0] for users in data]
            user_list = list(set(repo_user_list))
            print(f"Processing a total of {len(user_list)} users")
            applist, user_app_list = jurl(folder, user_list)
            json_sorted = merge_dictionary_list(user_app_list)
            with open("app_urls.json", "w") as out:
                json.dump(json_sorted, out, indent=4)
            print("")
            jsext(applist, folder)
    except Exception as e:
        print(e)
    except (KeyboardInterrupt, SystemExit) as e:
        print("\n" + "Program escaped by User")
        sys.exit()
    result = [
        os.path.join(dp, f)
        for dp, dn, filenames in os.walk(folder)
        for f in filenames
        if os.path.splitext(f)[1] == ".js"
    ]
    print(f"Written a total source code for {len(result)} apps")


# eeapps(,
#  folder=path)
