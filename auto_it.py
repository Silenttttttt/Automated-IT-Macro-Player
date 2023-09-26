import os
import sys
import openai
import json
import time
from io import StringIO
import re
from datetime import datetime, timedelta
import webbrowser
import pyautogui
from fuzzywuzzy import process
import pyperclip
 
 
 
if sys.platform == 'win32':
    import pygetwindow
 
 
 
 
 
 
 
 
 
 
 
 
customer_devices = {
    "client_1": "\
    [1: connect client_1 main server srv]\
    [2: connect client_1 domain controller dc]\
    [3: connect client_1 meeting pc pscm pc 25]\
    [4: connect client_1 gaming pc pscm pc 17]\
    [5: connect new server srv2]",
    "client_2": "\
    [1: connect client_2 main server srv]\
    [2: connect client_2 domain controller dc01]\
    [3: connect client_2 domain controller dc02]\
    [4: connect client_2 file server fs01]",
    "client_3": "\
    [1: connect client_3 main server srv]\
    [2: connect client_3 hyp01]",
    "client_4": "\
    [1: connect client_4 hyp01]\
    [2: connect client_4 domain controller dc01]\
    [3: connect client_4 file server fs01]",
    "client_5": "\
    [1: connect client_5 main server srv]",
}
 
general_actions = "\
    [32: login into windows admin user]\
    [33: search and open app(33:INPUT)]\
    [34: Wait for a period in seconds(34:INPUT)]\
    [35: Run CMD command(35:INPUT)]\
    [36: Type text(36:INPUT)]\
    [37: Keyboard Shortcut(+ separator)(37:INPUT)]\
    [38: Type file contents(38:INPUT)]\
    [39: for loop keyboard shortcut(39:INPUT;NUM)]\
        "
 #type_file_contents
 

#c
api_key = "GPT_API_KEY"
 
 #78
 
class Chatbot:
    def __init__(self, api_key, model):
        self.api_key = api_key
        self.model = model
 
    def trim_conversation(self, conversation, tokens_to_trim):
        conversation_length = sum(len(msg["content"]) for msg in conversation.messages)
        while conversation_length > 3700 - tokens_to_trim:
            if len(conversation.messages) > 6:
                # Remove the third oldest message (index 2) while keeping the system message
                conversation.messages.pop(2)
           # else:
                # Remove the second oldest message (index 1) while keeping the system message
                #conversation.messages.pop(1)
            conversation_length = sum(len(msg["content"]) for msg in conversation.messages)
            print("removed old message")
            time.sleep(0.2)
    def chat_completion_api(self, conversation):
        openai.api_key = self.api_key
        print("mesage sent to api")
 
        messages = [{"role": message["role"], "content": message["content"]} for message in conversation.messages]
 
        if len(messages) < 2:
            raise ValueError("There must be at least two messages in the conversation.")
 
        tokens_to_trim = 0
        num_tokens = sum(len(msg["content"]) for msg in conversation.messages) // 4
 
        while num_tokens > 3700:
            tokens_to_trim += 200
            self.trim_conversation(conversation, tokens_to_trim)
            num_tokens = sum(len(msg["content"]) for msg in conversation.messages) // 4
 
        while True:
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=messages
                    ##rest of model arguments
                )
                content = response['choices'][0]['message']['content']
 
                conversation.add_message("assistant", content)
                return {"response": content}
            except openai.error.RateLimitError:
                print("Rate limit error encountered. Waiting 10 seconds before retrying...")
                time.sleep(10)
            except openai.error.InvalidRequestError as e:
                print("InvalidRequestError occurred:", e)
                tokens_to_trim += 200
                self.trim_conversation(conversation, tokens_to_trim)
                time.sleep(20)
                return self.chat_completion_api(conversation)
 
 
 
 
 
class Conversation:
    def __init__(self):
        self.messages = []
 
    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})
 
    def read_from_json(self, filename):
        try:
            with open(filename, "r") as f:
                conversation_json = json.load(f)
            self.messages = conversation_json["messages"]
        except:
            pass
       # print(self.messages)
 
    def write_to_json(self, filename):
        conversation_json = {"messages": self.messages}
        with open(filename, "a") as f:
            json.dump(conversation_json, f, indent=2)
 
    def get_conversation_format(self):
        return [{"role": message["role"], "content": message["content"]} for message in self.messages]
 
 
 
 
# def get_multiline_input(prompt, end_word):
#     lines = []
#     print(prompt)
#     while True:
#         line = input()
#         if line.strip() == end_word:
 
#             lines.append(line)
#     #print("Sent message to API...")
#     return '\n'.join(lines)
 
 
 
##  ACTION FUNCTIONS 
 
 
 
## GENERAL


 ##keybbind, argument and custom separator for second argument

def login_admin_user(customer_name=None, arg=None):
 
    if customer_name == "client_1":
        pyautogui.typewrite("%R3p3!!%")
    else:
        pyautogui.typewrite("%r3p3!!%")
 
    pyautogui.press('enter')
    print(f"*types in password for {customer_name}*")
    return "password"
 
def search_open_app(customer_name=None, arg=None):
    try:
 
        time.sleep(5)
        pyautogui.hotkey('winleft', 'd')
        time.sleep(2)
        pyautogui.press('winleft')
        time.sleep(2)
        pyautogui.typewrite(arg)
        time.sleep(5)
        pyautogui.press('enter')
 
 
        time.sleep(5)
        if "veeam" in arg.lower():
            pyautogui.hotkey('alt', 'y')
 
 
        print(f"*types in app name {arg}*")
    except:
        print(f"error opening app {arg}")
    return "app open"
 
 
 
def wait_and_click_image(image_path, region=None, timeout=60, interval=1, confidence=0.8, double_click=False):
    """Waits for an image to appear on the screen and clicks on it"""
    start_time = time.time()
 
    while time.time() - start_time < timeout:
        location = pyautogui.locateOnScreen("pics/" + image_path, region=region, confidence=confidence)
        if location is not None:
            x, y = pyautogui.center(location)
            pyautogui.click(x, y)
            if double_click:
                pyautogui.click(x, y)
 
                print(f"clicked{image_path}")
            print(f"clicked{image_path}")
            return True
        time.sleep(interval)
       # print(time.time() - start_time)
    return False
 
 
 
def focus_window(app_name):
    try:
        window = pygetwindow.getWindowsWithTitle(app_name)[0]
        window.activate()
        return True
    except IndexError:
        print(f"Window with app name '{app_name}' not found.")
        return False
 
 
def open_website(url):
    webbrowser.open(url)
    time.sleep(5)
   # Click at position (100, 200)
    # pyautogui.click(x=1606, y=227)
    # pyautogui.click(x=1606, y=227)
    wait_and_click_image('connect.png', region=(1045, 190, 1900, 350), double_click=True)
 
    time.sleep(10)
    focus_window("splashtop")
    time.sleep(5)
 
    wait_and_click_image('splashctrlaltdel.png', region=(300, 50, 1350, 550), confidence=0.6, double_click=True)
    time.sleep(10)
 
 
 
def wait_for_seconds(customer_name=None, arg=None):
    if arg is not None:
        time.sleep(int(arg))
    time_waited = "Waited for " + str(arg) + " seconds"
    print(time_waited)
    return time_waited
 
 
 
def run_cmd_command(customer_name=None, arg=None):
 
    try:
        # Win+D (show desktop)
        pyautogui.hotkey('win', 'd')
        time.sleep(3)  # wait 3 seconds
 
        # Win+R (run dialog)
        pyautogui.hotkey('win', 'r')
        time.sleep(3)  # wait 3 seconds
 
        # Type 'cmd' into run dialog
        pyautogui.write('cmd')
        time.sleep(1)  # wait 1 second
 
        # Press 'enter' to run cmd
        pyautogui.press('enter')
        time.sleep(5)  # wait 5 seconds
 
        # Type the 'arg' into cmd
        pyautogui.write(arg)
        time.sleep(2)
        pyautogui.press('enter')
 
        print(f"*running cmd command {arg}*")
    except:
        print(f"error running cmd command {arg}")
    return f"ran cmd command: {arg}"
 
 
def type_text(customer_name=None, arg=None):
 
    try:
        time.sleep(1)  # wait 3 seconds

        # Type the 'arg' into cmd
        pyautogui.write(arg)
        time.sleep(1)

        print(f"*typed {arg}*")
    except:
        print(f"error running cmd command {arg}")
    return f"ran cmd command: {arg}"
 
def keyboard_shortcut(customer_name=None, arg=None):
    try:
        time.sleep(0.5)
        if arg is None:
            return  # No argument provided
        
        # Separate the arg string using the + separator
        keys = arg.split('+')
        
        # Execute the keyboard shortcut using pyautogui
        pyautogui.hotkey(*keys)
        print(f"pressed keyborad shorcut: {arg}")
        time.sleep(0.5)
    except:
        print(f"error running keyboard shortcut {arg}")
    return f"ran keyboard shortcut: {arg}"
 


def for_loop_keyboard_shortcut(customer_name=None, arg=None):
    try:
        if arg is None:
            return  # No argument provided
        
        # Check if the argument contains the separator character
        if ';' in arg:
            # Separate the argument string into shortcut and repeat count
            shortcut, repeat_count = arg.split(';')
            repeat_count = int(repeat_count)
        else:
            shortcut = arg
            repeat_count = 1
        
        # Separate the shortcut string using the + separator
        keys = shortcut.split('+')

        # Wait for 5 seconds
        time.sleep(1)

        # Press the keyboard shortcut multiple times
        for _ in range(repeat_count):
            pyautogui.hotkey(*keys)
            time.sleep(0.1)  # Delay between each shortcut press
        
        print(f"Pressed keyboard shortcut: {shortcut} ({repeat_count} times)")

    except Exception as e:
        print(f"Error running keyboard shortcut for loop: {arg}")
        print(f"Exception: {str(e)}")

    return f"Ran keyboard shortcut for loop: {arg}"


def type_file_contents(customer_name=None, arg=None):
    time.sleep(1)
    if arg is None:
        print("No file path provided.")
        return
   
    # Clear the clipboard
    pyperclip.copy(' ')
    pyperclip.copy('')  
    time.sleep(0.1)
    pyautogui.write(" ")
    time.sleep(0.1)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.1)
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.1)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.1)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.1)
    pyautogui.press('backspace')
    time.sleep(0.1)

    try:
        with open(arg, 'r') as file:
            file_contents = file.read()

        pyperclip.copy(file_contents)
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'v')

    except FileNotFoundError:
        print("File not found:", arg)
    print(f"pasted contents of file: {arg}")
    return f"pasted contents of file: {arg}"


##client_1
def get_prof_main_server(customer_name=None, arg=None):
    print("opens main server")
    open_website("https://app.atera.com/new/rmm/device/072bfbd3-2aad-4888-bd80-fdaf20723300/agent")
 
    return "main server"
 
def get_prof_domain_controller(customer_name=None, arg=None):
    #open_website("")
    print("NO DC")
    return "domain controller"
 
def get_prof_meeting_pc(customer_name=None, arg=None):
    open_website("https://app.atera.com/new/rmm/device/6a385883-8826-4068-8918-158f5f596241/agent")
    print("opens pc 25")
    return "meeting room pc25"
 

def get_prof_gaming_pc(customer_name=None, arg=None):
    open_website("https://app.atera.com/new/rmm/device/892e29a6-4ac9-4b0c-bb40-7f70e2b3a9ff/agent")
    print("opens pc 25")
    return "gaming pc17"

def get_prof_new_srv(customer_name=None, arg=None):
    open_website("https://app.atera.com/new/rmm/device/087a10ce-44d7-4a78-832a-54476e856bf0/agent")
    print("opens new srv")
    return "new srv"


##client_2
def get_reso_main_server(customer_name=None, arg=None):
    open_website("https://app.atera.com/new/rmm/device/76a8481b-cd3b-4b36-a8fa-46fd2cefd1f1/agent")
    return "main server"
 
def get_reso_dc_01(customer_name=None, arg=None):
    open_website("https://app.atera.com/new/rmm/device/a4b52144-2637-4b44-bd6c-5535a05ebf1e/agent")
    return "dc 01"
 
def get_reso_dc_02(customer_name=None, arg=None):
    open_website("https://app.atera.com/new/rmm/device/27a2ab9c-0051-4897-8b15-8bd23ee862ac/agent")
    return "dc 02"
 
def get_reso_fs_01(customer_name=None, arg=None):
    print("NO FS")
 #   open_website("")
    return "fs 01"
 
 
##client_3
def get_rece_main_server(customer_name=None, arg=None):
    open_website("https://app.atera.com/new/rmm/device/55f6facf-f135-437f-8824-f2e701ff9548/agent")
    return "main server"
 
def get_rece_hyp_01(customer_name=None, arg=None):
    open_website("https://app.atera.com/new/rmm/device/81b7a667-f1cc-4171-8bc9-3f6afa70a112/agent")
    return "hyp 01"
 
## client_4
 
 
def get_uber_hyp_01(customer_name=None, arg=None):
    open_website("https://app.atera.com/new/rmm/device/dd3b0130-5548-4104-a635-72be466f1e12/agent")
    return "ur-hyp1"
 
def get_uber_dc_01(customer_name=None, arg=None):
    open_website("https://app.atera.com/new/rmm/device/28056bb3-7fe6-4ae6-b37b-5307e80209fc/agent")
    return "ur-dc1"
 
 
def get_uber_fs_01(customer_name=None, arg=None):
    open_website("https://app.atera.com/new/rmm/device/9a875645-cfb8-4ebe-b1d3-7b97c236119a/agent")
    return "ur-fs1"
 
 
 
# THE client_5 FILMS
 
def get_tvf_srv(customer_name=None, arg=None):
    open_website("https://app.atera.com/new/rmm/device/c73646b5-77d6-4e99-ad8a-c4992b65cad8/agent")
    return "tvf-srv"
 
 
 
FUNCTIONS = {
    "client_1": {
        1: get_prof_main_server,
        2: get_prof_domain_controller,
        3: get_prof_meeting_pc,
        4: get_prof_gaming_pc,
        4: get_prof_new_srv,
    },
    "client_2": {
        1: get_reso_main_server,
        2: get_reso_dc_01,
        3: get_reso_dc_02,
        4: get_reso_fs_01,
    },
    "client_3": {
        1: get_rece_main_server,
        2: get_rece_hyp_01,
    },
    "client_4": {
        1: get_uber_hyp_01,
        2: get_uber_dc_01,
        3: get_uber_fs_01,
    },
    "client_5": {
        1: get_tvf_srv,
    },
    "general": {
        32: login_admin_user,
        33: search_open_app,
        34: wait_for_seconds,
        35: run_cmd_command,
        36: type_text,
        37: keyboard_shortcut,
        38: type_file_contents,
        39: for_loop_keyboard_shortcut,
    },
}
 
 
## END ACTION FUNCTIONS
 
 
 
 
 
 
def read_actions_from_json(filename, no_prompt=False):
    """
    Reads actions and their labels from a JSON file and returns them as a list of tuples
    """
    full_path = os.path.join(os.getcwd(), filename)
    with open(full_path, "r") as f:
        data = json.load(f)
        actions = data.get('actions', [])
        customer_name = data.get('customer_name', '')
        composite_label = data.get('composite_label', '')
    print("------")
    print(f"Customer name: {customer_name}")
    print(f"Actions to execute: {composite_label}")
    print("------")
  #  print("Actions in the file:")
  #  for action in actions:
 #       print(f"Label: {action[0]}, Result: {action[1]}")
    if not no_prompt:
        execute = input("Do you want to execute these actions? (Y/n): ")
    if no_prompt or  execute.lower() == "y" :
        # Extract only the action part of each tuple
        actions = [action[1] for action in actions]
        return actions, customer_name
    else:
        print("Actions will not be executed.")
        return None, None
 
 
 
 
 
 
def save_actions_to_json(actions_list, customer_name, user_input, filename):
    """
    Saves actions and their labels to a JSON file
    """
    full_path = os.path.join(os.getcwd(), filename)
    composite_label = []
 
    # Create a dictionary mapping action numbers to their labels
    action_labels = {}
    for device_actions in [customer_devices[customer_name], general_actions]:
        for match in re.finditer(r"\[(\d+): ([^\]]+)\]", device_actions):
            action_labels[int(match.group(1))] = match.group(2)
 
    # Create the composite label
    for action in actions_list:
        if action[1][0] in action_labels:
            # If the action has an arg, append it to the label
            if action[1][1]:
                composite_label.append(f"{action_labels[action[1][0]]}:{action[1][1]}")
            else:
                composite_label.append(action_labels[action[1][0]])
 
    data = {
        "customer_name": customer_name,
        "prompt": user_input,
        "composite_label": " -> ".join(composite_label),
        "actions": actions_list,
    }
 
    with open(full_path, "w") as f:
        json.dump(data, f, indent=4)
 
def label_actions(actions_list, functions_dict, customer_name):
    labels = []
    if not actions_list:
        return labels
    for index, arg in actions_list:
        if index < 30:
            try:
                func = functions_dict[customer_name][index]
                label = f"{func.__name__}({customer_name}, {arg if arg else ''})"
                labels.append(label)
            except:
                print(f"error labeling: {index}")
 
        else:  # General function
            func = functions_dict["general"][index]
            label = f"{func.__name__}({customer_name}, {arg if arg else ''})"
            labels.append(label)
    return labels
 
def execute_actions(actions_list, functions_dict, customer_name):
    results = []
    if not actions_list:
        return results
    for index, arg in actions_list:
        try:
            if index < 30:
 
                func = functions_dict[customer_name][index]
                if arg:
                    result = func(customer_name=customer_name, arg=arg)
                else:
                    result = func(customer_name)
                results.append(result)
            else:  # General function
                func = functions_dict["general"][index]
                if arg:
                    result = func(customer_name=customer_name, arg=arg)
                else:
                    result = func(customer_name)
                results.append(result)
 
        except KeyboardInterrupt:
            print("Interrupted by user.")
            sys.exit(42)
 
        except:
            print(f"error executing: {index}")
    return results
 
 
def get_action_list_from_chatbot_response(response_content):
    """Extract action indexes and additional arguments from chatbot response using '|' as separator and ':' for arguments"""
    action_indexes = re.findall(r"\b(\d+)(?::([^\|]+))?", response_content)
    return [(int(index), arg.strip() if arg else None) for index, arg in action_indexes]
 
 
def parse_action_list(action_list_string):
    """Parses a string of actions into a list of tuples."""
    actions = []
    for action in action_list_string.split("|"):
        index = None
        arg = None
        if ":" in action:
            index_arg = action.split(":", 1)
            index = int(index_arg[0])
            arg = index_arg[1]
        else:
            index = int(action)
        actions.append((index, arg))
    return actions


 
def interact_chat(conversation, chatbot, filename, index_string, customer_name, sys_message=None, action_list_string=None):
    try:
        if sys_message is None:
            sys_message = "You are the action list bot, you look at the user request and you create a list of appropriate actions, and only output the number list of the correct actions, without explaining your answer. Paying attention to detail, then output the number of the appropriate actions, close matches count. Use the custom separator \"|\" for the actions index, and if the action requires additional argument like this: (INDEX:INPUT), use the separator \":\". Do not describe the actions, only give the action list and arguments like this: \"1|3|35:test command\". Here is the action list:\n"
        sys_message += index_string
        conversation.add_message("system", sys_message)
 
        if action_list_string is None:
            user_input = input("Enter your message: ")
            conversation.add_message("user", "What are the index numbers for the actions to solve the problem: \"" + user_input + "\"")
            response = chatbot.chat_completion_api(conversation)
            content = response["response"]
            num_tokens = sum(len(msg["content"]) for msg in conversation.messages) // 4
            print(f"Number of tokens after response: {num_tokens}")
            print(f"Bot: {content}")
            actions_list = get_action_list_from_chatbot_response(content)
        else:
            actions_list = parse_action_list(action_list_string)
            user_input = "Custom action list: " + action_list_string
        print(f"Actions list: {actions_list}")
        labels = label_actions(actions_list, FUNCTIONS, customer_name)
        save_actions_to_json(list(zip(labels, actions_list)), customer_name, user_input, filename)
        print(actions_list)
        execute = input("Do you want to execute these actions? (Y/n): ")
        if execute.lower() == "y" :

            results = execute_actions(actions_list, FUNCTIONS, customer_name)
            print("Results:", results)
            print("---")

    except KeyboardInterrupt:
        print("Interrupted by user.")
 
 
 
 
def get_index_string(customer_name):
    """Return the index string for a given user name"""
    return customer_devices.get(customer_name, "Unknown customer name") + general_actions
 
def get_closest_customer_name(input_customer_name):
    """Return the closest customer name to the input, based on fuzzy string matching"""
    customer_names = ["client_1", "client_2", "client_3", "client_4", "client_5"]
    closest_match, _ = process.extractOne(input_customer_name, customer_names)
    return closest_match
 
 
 

 
def main(api_key):
    action_list_string = None
    skip_message = None
    if len(sys.argv) > 1:
        if sys.argv[1] == "-al":
            json_filename = "actions/" + input("Enter the name of a JSON file to save: ") + ".json"
            input_customer_name = input("Enter customer name: ")
            customer_name = get_closest_customer_name(input_customer_name)
            print(customer_name)
            action_list_string = input("Enter action list: ")
            
            
            
        
            
            
        else:
            
            json_filename = "actions/" + sys.argv[1] + ".json"
            print(json_filename)
            if os.path.exists(json_filename):
                print("Reading from file...")
                actions, customer_name = read_actions_from_json(json_filename, no_prompt=True)
    
                if actions is not None:
                    results = execute_actions(actions, FUNCTIONS, customer_name)
                    print("Results:", results)
                    print("---")
                skip_message = True
            else:
                print("JSON file does not exist.")
    else:
        
        
        json_filename = "actions/" + input("Enter the name of a JSON file to read: ") + ".json"
        print(json_filename)
        if os.path.exists(json_filename):
            print("Reading from file...")
            actions, customer_name = read_actions_from_json(json_filename)
 
            if actions is not None:
                results = execute_actions(actions, FUNCTIONS, customer_name)
                print("Results:", results)
                print("---")
            skip_message = True
        else:
            print("JSON file does not exist. Creating action...")
            print("No JSON file specified. Creating action...")
 
       
        input_customer_name = input("Enter customer name: ")
        customer_name = get_closest_customer_name(input_customer_name)
        print(customer_name)

    if not skip_message:
        index_string = get_index_string(customer_name)
        conversation = Conversation()
        model = "gpt-3.5-turbo"
        chatbot = Chatbot(api_key, model)
        sys_message = None

        interact_chat(conversation, chatbot, json_filename, index_string, customer_name, sys_message, action_list_string)

if __name__ == "__main__":
    main(api_key)