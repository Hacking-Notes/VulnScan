import re
import os
import sys
import json
import time
import datetime
import textwrap
import requests
import itertools
import threading
import concurrent.futures
import concurrent.futures
from bs4 import BeautifulSoup
from urllib.parse import urlparse

print("""
██╗   ██╗██╗   ██╗██╗     ███╗   ██╗███████╗ ██████╗ █████╗ ███╗   ██╗
██║   ██║██║   ██║██║     ████╗  ██║██╔════╝██╔════╝██╔══██╗████╗  ██║
██║   ██║██║   ██║██║     ██╔██╗ ██║███████╗██║     ███████║██╔██╗ ██║
╚██╗ ██╔╝██║   ██║██║     ██║╚██╗██║╚════██║██║     ██╔══██║██║╚██╗██║
 ╚████╔╝ ╚██████╔╝███████╗██║ ╚████║███████║╚██████╗██║  ██║██║ ╚████║
  ╚═══╝   ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝                                                                                             
""")

# Set Variables URL & Recursion Level ---> (URL_Finder)
url = input('Enter the website URL: ').strip()
print("")
if not (url.startswith("http://") or url.startswith("https://")):
    url = "https://" + url

try:
    response = requests.get(url)
    if response.status_code == 200:
        print("The script will follow internal links on the website up to the maximum recursion level specified.")
        while True:
            try:
                max_recursion_level = int(input('Recursion Level (Between 1-3 | Default = 1): ').strip() or 1)
                if 1 <= max_recursion_level <= 3:
                    break
                else:
                    print('Input must be between 1 and 3')
            except ValueError:
                print('Input must be a number')
        print("")
except requests.exceptions.RequestException:
    print('Could not connect to the website')
except:
    print('Invalid URL')

# Set file_name
file_name = url[8:] + ".txt"

# Set Variable JS_scanner_file_name        ---> (JS_Scanner)
JS_scanner_file_name = file_name

# Set Variable ChatGPT_file_name           ---> (ChatGPT)
JS_Unique_file_name = "JS_Unique_staratlas.help.txt"
JS_URL_file_name = "JS_URL_" + file_name

# Set Variable ChatGPT_file_name           ---> (ChatGPT)
ChatGPT_file_name = "chatGPT_" + file_name

# Set Variable Clean_up_file_name          ---> (clean_up_files)
Clean_up_file_name = "final_" + file_name

# Search URL's on the targeted website
def URL_Finder(url, max_recursion_level):

    visited_urls = []

    def crawl_website(url, max_recursion_level, visited_urls):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0;Win64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
        session = requests.Session()
        response = requests.get(url, headers=headers, allow_redirects=True)
        final_url = response.url
        if response.status_code != 200:
            return []
        soup = BeautifulSoup(response.text, 'html.parser')
        parsed_url = urlparse(final_url)
        same_domain_urls = []
        visited_urls.append(url)
        for link in soup.find_all('a'):
            link_url = link.get('href')
            parsed_link_url = urlparse(link_url)
            if parsed_link_url.netloc == parsed_url.netloc:
                # remove trailing slash from URL if it exists
                link_url = link_url.rstrip('/')
                if max_recursion_level > 0 and link_url not in visited_urls:
                    same_domain_urls.append(link_url)
                    same_domain_urls.extend(crawl_website(link_url, max_recursion_level - 1, visited_urls))

        # Check for sitemap or robots.txt
        sitemap_url = final_url + '/sitemap.xml'
        robots_url = final_url + '/robots.txt'
        for file_url in [sitemap_url, robots_url]:
            try:
                file_response = requests.get(file_url)
                if file_response.status_code != 200:
                    continue
                file_soup = BeautifulSoup(file_response.text, 'xml')
                for link in file_soup.find_all('loc'):
                    link_url = link.get_text().rstrip('/')
                    parsed_link_url = urlparse(link_url)
                    if parsed_link_url.netloc == parsed_url.netloc and max_recursion_level > 0 and link_url not in visited_urls:
                        same_domain_urls.append(link_url)
                        visited_urls.append(link_url)
            except:
                pass
        return same_domain_urls

    def run_animation():
        spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        while not crawl_future.done():
            sys.stdout.write("\rCrawling in progress " + next(spinner))
            sys.stdout.flush()
            time.sleep(0.5)
        print("")

    if __name__ == '__main__':
        while True:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                crawl_future = executor.submit(crawl_website, url, max_recursion_level, visited_urls)
                run_animation()
            urls = crawl_future.result()
            urls.append(url)
            urls.sort()  # Sort the URLs alphabetically

            number_of_urls_found = len(urls)
            print("")
            print("=" * 45)
            print("")
            print("VulnScan has found " + str(number_of_urls_found) + " pages ↓")
            print("")
            for url in urls:
                print(url)
            parsed_url = urlparse(url)
            file_name = parsed_url.netloc + '.txt'
            try:
                with open(file_name, 'w') as f:
                    for url in urls:
                        f.write(url + '\n')
            except IOError:
                print(f"Unable to write to {file_name}")
            break

        print("")
        print("=" * 45)
# Scan the Website for all the Javascript elements
def JS_Scanner(JS_scanner_file_name):

    print("")
    print("Analysing Javascript elements, this could take a few minutes...")

    def search_scripts(urls):
        # Set up a counter variable to generate unique IDs
        counter = 1

        # Create a dictionary to keep track of script tags that have already been seen
        seen_scripts = {}

        # Iterate over the list of URLs
        for url in urls:
            # Set up a counter variable for this URL
            script_counter = 1

            # Generate a unique ID for the current URL
            id = f"id{counter}"

            # Make a request to the URL, following redirects
            response = requests.get(url, allow_redirects=True)

            # Parse the HTML of the page
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all script tags
            script_tags = soup.find_all('script')

            # Generate a unique ID for the current URL
            id = f"id{counter}"

            # Set up a counter variable
            script_counter = 1

            # Extract the text from each script tag and print it
            for script in script_tags:
                # Skip script tags with empty text
                if not script.text.strip():
                    continue

                # Build the xpath string
                xpath = ''
                element = script
                while element is not None:
                    if xpath:
                        xpath = '/' + xpath
                    xpath = element.name + xpath
                    element = element.parent

                # Remove the first '/' character from the xpath string
                xpath = xpath[10:]

                # Check if this script has already been seen
                script_hash = hash(script.text)
                if script_hash in seen_scripts:
                    # If the script has already been seen, add it to the duplicates dictionary
                    duplication = f"({seen_scripts[script_hash]},JS#{script_counter})"
                    key = f"{id},JS#{script_counter}"
                    with open("JS_URL_" + file_name.replace(".txt", ".txt"), "a") as f:
                        duplicates_dict = {key: {"url": url, "duplication": duplication, "xpath": xpath}}
                        json.dump(duplicates_dict, f)
                        f.write("\n")
                else:
                    seen_scripts[script_hash] = id
                    key = f"{id},JS#{script_counter}"
                    with open("JS_URL_" + file_name.replace(".txt", ".txt"), "a") as f:
                        duplicates_dict = {key: {"url": url, "xpath": xpath, }}
                        json.dump(duplicates_dict, f)
                        f.write("\n")
                    with open("JS_Unique_" + file_name, "a") as f:
                        f.write('\n')
                        f.write("---\n")
                        f.write(f"({id},JS#{script_counter}) \n")
                        f.write('\n')  # Always write a newline character before the script code
                        f.write(script.text + '\n')
                        f.write("---\n")

                # Increment the script counter
                script_counter += 1

            # Increment the URL counter
            counter += 1

    # Read in URLs from file
    while True:
        file_name = JS_scanner_file_name
        try:
            with open(file_name, "r") as f:
                urls = f.read().splitlines()
            break  # Exit the loop if the file was successfully opened
        except FileNotFoundError:
            print("Error: file not found. Please try again.\n")

    # Write output to a file
    with open("JS_Unique_" + file_name, "a") as f:
    # INSTRUCTIONS FOR CHAT-GPT
        f.write(textwrap.dedent("""You're working in Cybersecurity. You have been searching vulnerability through source code for 20 years. Your task is now to analyse the following code wile respecting the instructions.

    Instructions: 
    1. A list of javascript code will be provided to you at the bottom, each javascript code is delimited by --- at the start and --- at the end and include a unique identifier (id[X],JS#[X]). (The X here is a place holder)
    2. Analyse the javascript code
    3. DO NOT INCLUDE THE RESPONSE IN THE TEMPLATE IF THE SNIPPET OF CODE IS NOT VULNERABLE
    4. Use the following template to respond using the corresponding id and INCLUDING +++ AT THE START AND +++ AT THE END of each explanations
    5. Do not include ANY other statement after using the template and make sure you have used the template exactly how it supposed to be use

    +++
    (id[X],JS#[X]) 
    Secure: [Vulnerable or Not Vulnerable]

    Text: [Explain SHORTLY, IF vulnerable, why it's vulnerable]
    +++

    DONT FORGET TO ADD THE +++ AT THE END

    The following is all the javascript snippet you need to analyse
    """))
        search_scripts(urls)
        print("")
        print("=" * 45)
# Send the output of the Javascript to ChatGPT (Verification of the vulnerability)
def ChatGPT(JS_Unique_file_name):
    from pyChatGPT import ChatGPT   # More information ---> https://github.com/terry3041/pyChatGPT

    # Authentification via Token
    TOKEN_FILE = "token.txt"
    TOKEN_EXPIRATION_DAYS = 1

    def get_token():
        if os.path.isfile(TOKEN_FILE):
            with open(TOKEN_FILE, "r") as f:
                token, date_str = f.read().split()
                expiration_date = datetime.datetime.strptime(date_str, "%Y-%m-%d") + datetime.timedelta(
                    days=TOKEN_EXPIRATION_DAYS)
                if datetime.datetime.today() < expiration_date:
                    return token
        print("""
        1. Go to https://chat.openai.com/chat and open the developer tools by F12.
        2. Find the __Secure-next-auth.session-token cookie in Application > Storage > Cookies > https://chat.openai.com.
        3. Copy the value in the Cookie Value field.
        """)
        token = input("Enter your ChatGPT token: ")
        with open(TOKEN_FILE, "w") as f:
            f.write(f"{token} {datetime.datetime.today().strftime('%Y-%m-%d')}")
        return token

    # Authentication via Token
    session_token = get_token()
    print("")

    def run_animation(resp):
        spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        while not resp['done']:
            sys.stdout.write("\rChatGPT is reviewing the Javascript codes " + next(spinner))
            sys.stdout.flush()
            time.sleep(0.5)
        print("")

    def make_api_call(text, resp):
        api = ChatGPT(session_token, chrome_args=['--headless, --disable-features=SafeBrowsing, --user-agent'])
        resp.update(api.send_message(text))
        api.clear_conversations()
        resp['done'] = True

    if __name__ == '__main__':
        while True:
            filename = JS_Unique_file_name
            try:
                with open(filename, 'r') as file:
                    text = file.read()
                break  # Exit the loop if the file was successfully opened
            except FileNotFoundError:
                print("Error: file not found. Please try again.\n")

        resp = {'done': False}
        thread = threading.Thread(target=make_api_call, args=(text, resp))
        thread.start()

        run_animation(resp)  # Start the animation

        thread.join()

        chatGPT_output_filename = filename[10:]

        with open('chatGPT_' + chatGPT_output_filename, 'w') as f:
            f.write(resp['message'])
            print("")
            print("=" * 45)

    # Introduce a feature to divide the text in case the file size exceeds the limit
    # Introduce a feature to calculate the seconds it will take to respond (add the estimated number of seconds before each of your response)
# Reformulate the output of ChatGPT
def JS_Output_Filtering(ChatGPT_file_name):
    if __name__ == '__main__':
        while True:
            file_name = ChatGPT_file_name
            try:
                with open(file_name, 'r') as file:
                    text = file.read()
                break  # Exit the loop if the file was successfully opened
            except FileNotFoundError:
                print("Error: file not found. Please try again.\n")

    with open(file_name, 'r') as f:
        file_contents = f.read()

    snippet_regex = re.compile(r'\((id\d+),JS#(\d+)\)\nSecure:\s*(Not Vulnerable|Vulnerable)(?:\n\nText: (.*))?')

    snippet_data = {}

    for match in snippet_regex.finditer(file_contents):
        id_value = match.group(1) + ',' + 'JS#' + match.group(2)
        secure_value = match.group(3)
        text_value = match.group(4) if match.group(4) else None
        if secure_value == "Vulnerable":
            snippet_data[id_value] = {"secure": secure_value, "text": text_value}

    # Write the data to a file
    with open('JS_Vulnerable.txt', 'w') as f:
        for key, value in snippet_data.items():
            f.write("{" + f'"{key}": {value}' + "}\n")
# Interpretation of the results from ChatGPT
def Interpretation(JS_Unique_file_name, JS_URL_file_name):
    file_name_1 = "JS_Vulnerable.txt"
    file_name_2 = JS_URL_file_name
    file_name_3 = JS_Unique_file_name

    # Step 1: Read the contents of the first file and store each line as a string in a list
    with open(file_name_1, "r") as f:
        file1_lines = f.readlines()

    if not file1_lines:
        print("No vulnerability found")
        exit()

    # Step 2: Read the contents of the second file and store each line as a string in a list
    with open(file_name_2, "r") as f:
        file2_lines = f.readlines()

    # Step 3: Read the contents of the third file and store each line as a string in a list
    with open(file_name_3, "r") as f:
        file3_lines = f.readlines()

    # Step 4: Loop through each line in the first file and extract the id and JS values
    output = ""  # initialize output variable
    for line in file1_lines:
        # Extract the id and JS values using string manipulation
        id_js = line.split(":")[0].strip().strip("{").strip('"')
        text = line.split(":")[-1].strip().strip('}').strip().strip('"')
        text = text[1:-1]  # Remove first and last characters
        output += "\nVulnerable ---> " + id_js
        output += "\n"
        output += "\nExplanation: " + text
        output += "\n"

        # Step 6: Loop through each line in the third file and save the lines between the snippet start and end
        found_snippet = False
        file3_lines_copy = file3_lines.copy()  # create a copy of the list to preserve the iterator
        for i, line3 in enumerate(file3_lines_copy):
            if ("(" + id_js + ")") in line3:
                found_snippet = True
                snippet_lines = []
            elif found_snippet and line3.strip() != '---':
                snippet_lines.append(line3)
            elif found_snippet:
                found_snippet = False
                snippet_text = "".join(snippet_lines).strip()
                output += "\n---\n"
                output += snippet_text + "\n"
                output += line3.strip() + "\n"  # print the snippet end line
                break

        # Step 5: Loop through each line in the second file and check if the id and JS values appear
        output += "\n"
        output += "The Following URL's are touched by this vulnerability"
        output += "\n" + '=' * 55 + "\n"
        found = False
        for line2 in file2_lines:
            if id_js in line2:
                found = True
                url = line2.split('"url": "')[1].split('"')[0]
                output += url + "\n"

        if not found:
            output += "Not found\n"

    final_name = "final_" + file_name_2[7:]

    # write output to file named "Final"
    with open(final_name, "w") as f:
        f.write(output)
        print(output)
# Interpretation of the results from ChatGPT
def clean_up_files(Clean_up_file_name):
    for filename in os.listdir('.'):
        if filename.endswith('.txt') and filename not in ['token.txt', Clean_up_file_name]:
            os.remove(filename)


# call the functions to execute the code
URL_Finder(url, max_recursion_level)
JS_Scanner(JS_scanner_file_name)
ChatGPT(JS_Unique_file_name)
JS_Output_Filtering(ChatGPT_file_name)
Interpretation(JS_Unique_file_name, JS_URL_file_name)

# If you desire to not clean-up the file, comment the following
clean_up_files(Clean_up_file_name)
