import re
import os
import sys
import json
import time
import openai
import textwrap
import requests
import itertools
import concurrent.futures
from bs4 import BeautifulSoup
from urllib.parse import urlparse

print("""
██╗   ██╗██╗   ██╗██╗     ███╗   ██╗███████╗ ██████╗ █████╗ ███╗   ██╗    █████╗ ██╗
██║   ██║██║   ██║██║     ████╗  ██║██╔════╝██╔════╝██╔══██╗████╗  ██║   ██╔══██╗██║
██║   ██║██║   ██║██║     ██╔██╗ ██║███████╗██║     ███████║██╔██╗ ██║   ███████║██║
╚██╗ ██╔╝██║   ██║██║     ██║╚██╗██║╚════██║██║     ██╔══██║██║╚██╗██║   ██╔══██║██║
 ╚████╔╝ ╚██████╔╝███████╗██║ ╚████║███████║╚██████╗██║  ██║██║ ╚████║██╗██║  ██║██║
  ╚═══╝   ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝╚═╝  ╚═╝╚═╝                                                                                                
""")

# Set Variables URL & Recursion Level ---> (URL_Finder)
class Set_Variable1():
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
        exit()
    except:
        print('Invalid URL')
url = Set_Variable1.url

# Set file_name (Remove any extension, subdomain are /)
class file_name_integrity():
    # Parse the URL
    parsed_url = urlparse(url)
    # Get the domain name without subdomains
    domain_name = parsed_url.netloc.split('.')[-2] + '.' + parsed_url.netloc.split('.')[-1]
    # Combine the domain name, domain extension, and file extension to create the file name
    file_name = f"{domain_name}.txt"

file_name = file_name_integrity.file_name

#2
class Set_Variable2():
    JS_scanner_file_name = file_name
    instructions = """You're working in Cybersecurity. You have been searching vulnerability through source code for 20 years. Your task is now to analyse the following code while respecting the instructions.

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
    """

#3
class Set_Variable3():
    JS_Unique_file_name = "JS_Unique_" + file_name

    api_key_file = 'API_Key.txt'

    if os.path.exists(api_key_file) and os.path.getsize(api_key_file) > 0:
        with open(api_key_file, 'r') as f:
            api_key = f.read().strip()
    else:
        print('''    1. Go to https://platform.openai.com/account/api-keys.
    2. Create an API key and then proceed to paste it at this location.
            ''')
        api_key = input("Include your OpenAI API key: ")
        with open(api_key_file, 'w') as f:
            f.write(api_key)
            print("")

#4
class Set_Variable4():
    ChatGPT_file_name = "chatGPT_" + file_name

#5
class Set_Variable5():
    JS_Unique_file_name = "JS_Unique_" + file_name
    JS_URL_file_name = "JS_URL_" + file_name

#6
class Set_Variable6():
    Clean_up_file_name = "final_" + file_name

# ============================================================

def URL_Finder(url, max_recursion_level, file_name):

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
        max_recursion_level = int(max_recursion_level)
        while True:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                crawl_future = executor.submit(crawl_website, url, max_recursion_level, visited_urls)
                run_animation()
            urls = crawl_future.result()
            urls.append(url)
            urls.sort()  # Sort the URLs alphabetically

            number_of_urls_found = len(urls)
            print("")
            print("VulnScan has found " + str(number_of_urls_found) + " pages ↓")
            print("")
            for url in urls:
                print(url)

            try:
                with open(file_name, 'w') as f:
                    for url in urls:
                        f.write(url + '\n')
            except IOError:
                print(f"Unable to write to {file_name}")
            break

def Javascript(JS_scanner_file_name, instructions):

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

        return True

    def run_animation(future_search, wait_time):
        print(f"The estimated wait time is {wait_time} seconds.")
        spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        while not future_search.done():
            sys.stdout.write("\rAnalysing Javascript Elements " + next(spinner))
            sys.stdout.flush()
            time.sleep(0.5)
        print("")

    if __name__ == '__main__':
        file_name = JS_scanner_file_name

        # Read in URLs from file
        while True:
            file_name = JS_scanner_file_name
            try:
                with open(file_name, "r") as f:
                    urls = f.read().splitlines()
                    f.seek(0)  # Reset file pointer to the beginning of the file
                    wait_time = int(len(f.readlines()) / 2)
                break  # Exit the loop if the file was successfully opened
            except FileNotFoundError:
                print("Error: file not found. Please try again.\n")
                exit()

        # Write output to a file
        with open("JS_Unique_" + file_name, "a") as f:
            # INSTRUCTIONS FOR CHAT-GPT
            f.write(textwrap.dedent(instructions))

        # Run the search_scripts function using concurrent.futures.ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_search = executor.submit(search_scripts, urls)
            run_animation(future_search, wait_time)

def chatGPT_API(JS_Unique_file_name, api_key):
    openai.api_key = api_key

    def makeCall(message_arr):
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=message_arr)
        return completion.choices[0].message

    def conversation():
        message_array = []
        while True:
            filename = JS_Unique_file_name
            try:
                with open(filename, 'r') as file:
                    user_input = file.read()
                break  # Exit the loop if the file was successfully opened
            except FileNotFoundError:
                print("Error: The API key you provided is not valid, or the API_KEY.txt file is not accessible. Please check your API key and try again.\n")
            exit()

        chatGPT_output_filename = filename[10:]

        message_obj = {"role": "user", "content": user_input}
        message_array.append(message_obj)

        resp = makeCall(message_array)
        resp_str = str(resp)
        resp_json = json.loads(resp_str)
        content = resp_json["content"].strip()

        with open('chatGPT_' + chatGPT_output_filename, 'w') as f:
            f.write(content)

    def run_animation(future_conversation):
        spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        while not future_conversation.done():
            sys.stdout.write("\rChatGPT is reviewing your Javascript codes " + next(spinner))
            sys.stdout.flush()
            time.sleep(0.5)
        print("")

    if __name__ == '__main__':

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_conversation = executor.submit(conversation)
            run_animation(future_conversation)

def JS_Output_Filtering(ChatGPT_file_name):
    if __name__ == '__main__':
        while True:
            file_name = ChatGPT_file_name
            try:
                with open(file_name, 'r') as file:
                    text = file.read()
                break  # Exit the loop if the file was successfully opened
            except FileNotFoundError:
                print("Error: File size exceeds ChatGPT's capacity.\n")
                exit()

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
    with open('Individual_JS_Vulnerable.txt', 'w') as f:
        for key, value in snippet_data.items():
            f.write("{" + f'"{key}": {value}' + "}\n")

def Interpretation(JS_Unique_file_name, JS_URL_file_name):
    file_name_1 = "Individual_JS_Vulnerable.txt"
    file_name_2 = JS_URL_file_name
    file_name_3 = JS_Unique_file_name

    # Step 1: Read the contents of the first file and store each line as a string in a list
    with open(file_name_1, "r") as f:
        file1_lines = f.readlines()

    if not file1_lines:
        print("\033[1m\033[32mNo vulnerability found\033[0m")
        return

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
        output += "\n\033[1m\033[31mThe JS code below may contain a vulnerability. ---> " + id_js + "\033[0m"
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
        output += "The Following URL's are touched by this potential vulnerability"
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

def clean_up_files(Clean_up_file_name):
    for filename in os.listdir('.'):
        if filename.endswith('.txt') and filename not in ['API_Key.txt', Clean_up_file_name]:
            os.remove(filename)

# ============================================================

# Recall Variables
max_recursion_level = Set_Variable1.max_recursion_level
url = Set_Variable1.url

JS_scanner_file_name = Set_Variable2.JS_scanner_file_name
instructions = Set_Variable2.instructions

JS_Unique_file_name = Set_Variable3.JS_Unique_file_name
api_key = Set_Variable3.api_key

ChatGPT_file_name = Set_Variable4.ChatGPT_file_name

JS_URL_file_name = Set_Variable5.JS_URL_file_name
Clean_up_file_name = Set_Variable6.Clean_up_file_name


# Launch Functions
class start_UI():
    print("=" * 45)
    print("")
URL_Finder(url, max_recursion_level, file_name)
class end_UI():
    print("")
    print("=" * 45)

class start_UI():
    print("")
Javascript(JS_scanner_file_name, instructions)
class end_UI():
    print("")
    print("=" * 45)

class start_UI():
    print("")
chatGPT_API(JS_Unique_file_name, api_key)
class end_UI():
    print("")
    print("=" * 45)

JS_Output_Filtering(ChatGPT_file_name)

class start_UI():
    print("")
Interpretation(JS_Unique_file_name, JS_URL_file_name)
clean_up_files(Clean_up_file_name)
