#!/usr/bin/python
import sys, getopt
import time

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from row_parser import RowParser
from slugify import slugify

short_args = "hu:p:b:m:"
long_args = ["help", "user=", "password=", "base-url=", "mode="]
modes = ["a", "v", "p"]

base_url_filter = "https://adam.unibas.ch/goto_adam_"

template = """
<html>
<head>
<title>Crawled videos for {}</title>
</head>
<body>
{}
</body>
</html>
"""


def main(argv):
    try:
        opts, args = getopt.getopt(argv, short_args, long_args)
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
    req_opts = {"u": False, "p": False}
    user = None
    pwd = None
    base_url = "https://adam.unibas.ch/goto_adam_crs_910690.html"
    mode = 'a'
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
        elif opt in ("-u", "--user="):
            req_opts['u'] = True
            user = arg
        elif opt in ("-p", "--password="):
            req_opts['p'] = True
            pwd = arg
        elif opt in ("-b", "--base-url="):
            base_url = arg
        elif opt in ("-m", "--mode="):
            if not arg in modes:
                print("Invalid argument '{}' for option --mode".format(arg))
                usage()
                sys.exit(2)
            mode = arg
    if False in req_opts.values():
        for arg, found in req_opts.items():
            if not found:
                lng_arg = get_long_arg(arg)
                example = get_example(arg)
                print("error: missing argument --{}={}".format(lng_arg, example))
        usage()
        return


    target_id = base_url.replace(base_url_filter, "").replace(".html", "")
    driver = webdriver.Firefox()
    success = login_switch(driver, user, pwd)
    if not success:
        driver.close()
        return
    driver.get(base_url)
    success = login(driver, user, pwd, target_id)
    if not success:
        driver.close()
        return
    base_name = slugify(driver.find_element_by_id("il_mhead_t_focus").text)
    data = []
    elems = driver.find_elements_by_xpath("//a[@href]")
    for elem in elems:
        url = elem.get_attribute("href")
        name_tag = elem.find_element_by_xpath("..")
        name = ""
        if name_tag.tag_name == "li":
            name = name_tag.text
        if "dropbox" in url or "tube" in url:
            data.append([base_name + "/" + name, elem.text, url, "link"])
    for k in reversed(range(len(data))):
        (path_a, name, _, _) = data[k]
        for i in range(len(data)):

            (path, _, _, _) = data[i]
            if path_a.replace(base_name, "")[:4] in path:
                if i != k:
                    data[i][0] = path.replace(name, "")
    data.extend(parse_rows(driver, base_name, mode))

    body_tags = """<ul>{}</ul>"""
    body_data = ""
    for (path, name, dl_url, file_type) in data:
        if file_type == "link" and mode in ["a", "v"]:
            body_data += get_li_tag(file_type, path, dl_url, name)
        elif file_type == "file" and mode in ["a", "p"]:
            body_data += get_li_tag(file_type, path, dl_url, name)
    body = body_tags.format(body_data)
    local_template = template.format(base_name, "{}")

    f = open(base_name + ".html", "a")
    f.write(local_template.format(body))
    f.close()
    driver.close()


def get_li_tag(tzpe, path, href, title):
    return """<li>({}){}: <a href="{}" target="_blank">{}</a></li>\n""".format(tzpe, path, href, title)


def parse_rows(driver, parent_name, mode):
    row_parser = RowParser(driver)
    elements = row_parser.parse()
    ret_elements = []
    for (name, ref, r_type) in elements:

        if r_type == "folder":
            driver.get(ref)
            wait_for_text(driver, "il_mhead_t_focus", name)
            child_elements = parse_rows(driver, parent_name + "/" + name, mode)
            ret_elements.extend(child_elements)
        elif r_type == "link" and mode in ["a", "v"]:
            driver.get(ref)
            if "switch" in driver.current_url:
                link = driver.find_element_by_xpath(
                    "/html/body/div[2]/section/div[1]/div[1]/video/source[1]").get_attribute("src")
            elif "dropbox" in driver.current_url:
                link = ref
            ret_elements.append((parent_name + "/", name, link, r_type))
        else:
            if mode in ['a', 'p']:
                ret_elements.append((parent_name + "/", name, ref, r_type))
    return ret_elements


def login(driver: webdriver, user, pwd, target_id):
    login_target = "https://adam.unibas.ch/shib_login.php?target="
    driver.get(login_target + target_id)
    success = wait_for(driver, "userIdPSelection_iddicon")
    if not success:
        return False
    unibas_selector = driver.find_element_by_xpath("//*[@id='userIdPSelection_iddicon']")
    unibas_selector.click()
    unibas = driver.find_element_by_xpath("//div[@title='Universities: Universität Basel']")
    unibas.click()
    actualTitle = driver.title
    if not actualTitle.startswith('SWITCH edu-ID Login'):
        return False

    return wait_for(driver, "userlog")


def login_switch(driver: webdriver, user, pwd, ):
    driver.get('https://tube.switch.ch/organizations/28')
    success = wait_for_class(driver, "profile")
    if not success:
        return False
    sign_in = driver.find_element_by_xpath('/html/body/div[1]/nav/ul/li[5]/a/span')
    sign_in.click()
    unibas_selector = driver.find_element_by_xpath("//*[@id='userIdPSelection_iddicon']")
    unibas_selector.click()
    unibas = driver.find_element_by_xpath("//div[@title='Universities: Universität Basel']")
    unibas.click()
    actualTitle = driver.title
    if not actualTitle.startswith('SWITCH edu-ID Login'):
        return False

    success = wait_for(driver, "username")
    if not success:
        return False

    driver.find_element_by_name("j_username").send_keys(user)
    driver.find_element_by_name("j_password").send_keys(pwd)
    driver.find_element_by_name("_eventId_proceed").click()
    return wait_for_class(driver, "avatar")


def wait_for(driver, elem_id):
    try:
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, elem_id)))
        return True
    except TimeoutException:
        return False


def wait_for_class(driver, class_id):
    try:
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, class_id)))
        return True
    except TimeoutException:
        return False


def wait_for_text(driver, elem_id, text):
    try:
        WebDriverWait(driver, 30).until(EC.text_to_be_present_in_element((By.ID, elem_id), text))
        return True
    except TimeoutException:
        return False


def wait_for_text_class(driver, class_id, text):
    try:
        WebDriverWait(driver, 30).until(EC.text_to_be_present_in_element((By.CLASS_NAME, class_id), text))
        return True
    except TimeoutException:
        return False


def get_example(arg):
    if arg == "u":
        return "mail@example.com"
    if arg == "p":
        return "sup3r5ecur3p4wd"


def usage():
    print("Usage:")
    print("\tadam-crawl.py -u -p [-b] [-m a,v,p]")
    print("Required: ")
    print("\t-u --user=<e-mail>\t\t\t\t\t The UniBas e-mail address.")
    print("\t-p --password=<passwd>\t\t\t\t The eduID password.")
    print("Optional: ")
    print("\t-b --base-url<adam.unibas.ch/...>\t The base-url of the crawled lecture.")
    print("\t-m a,v,p --mode=a,v,p\t\t\t\t Decides wether to crawl [a]ll, [v]ideos or [p]dfs only.")
    print("\t-h --help\t\t\t\t Prints this information.")


def get_short_arg(long_arg):
    short_args_cache = short_args.replace(":", "")
    for i, arg in long_args:
        if arg == long_arg:
            return short_args_cache[i]
    return None


def get_long_arg(short_arg):
    short_args_cache = short_args.replace(":", "")
    i = short_args_cache.find(short_arg)
    if i > 0:
        return long_args[i]
    return None


if __name__ == '__main__':
    main(sys.argv[1:])
