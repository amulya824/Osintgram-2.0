import datetime
import json
import sys
import urllib
import os
import codecs
import time
from pathlib import Path

import requests
import ssl
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

from geopy.geocoders import Nominatim
from instagram_private_api import Client as AppClient
from instagram_private_api import ClientCookieExpiredError, ClientLoginRequiredError, ClientError, ClientThrottledError

from prettytable import PrettyTable

from src import printcolors as pc
from src import config

class Osintgram:
    def __init__(self, target, is_file=False, is_json=False, command=None, output_dir=None, clear_cookies=False):
        self.api = None
        self.api2 = None
        self.geolocator = Nominatim(user_agent="http")
        self.user_id = None
        self.target_id = None
        self.is_private = True
        self.following = False
        self.target = target
        self.writeFile = is_file
        self.jsonDump = is_json
        self.cli_mode = False if command is None else True
        self.output_dir = output_dir if output_dir else "output"
        
        # Create the output directory if it doesn't exist
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        if clear_cookies:
            self.clear_cookies()
        
        # Login to Instagram
        try:
            self.login()
        except Exception as e:
            print(f"Error logging in: {str(e)}")
            sys.exit(1)

    def clear_cookies(self):
        """Clear cookies stored in the config directory"""
        try:
            config_path = Path('config')
            if config_path.exists():
                for cookie_file in config_path.glob('*.json'):
                    cookie_file.unlink()
            pc.printout("Cookies cleared\n", pc.GREEN)
        except Exception as e:
            pc.printout(f"Error clearing cookies: {str(e)}\n", pc.RED)

    def login(self):
        """Login to Instagram using credentials from config"""
        try:
            username = config.getUsername()
            password = config.getPassword()

            pc.printout(f"Attempting to login with username: {username}\n", pc.YELLOW)

            settings_file = "config/settings.json"
            if not os.path.isfile(settings_file):
                pc.printout("No saved session found, creating new login session...\n", pc.YELLOW)
                # Create initial login
                try:
                    self.api = AppClient(auto_patch=True, authenticate=True, 
                                       username=username, 
                                       password=password)
                    # Save the settings
                    self.api.settings_file = settings_file
                    self.api.save_settings()
                    pc.printout("Successfully logged in and saved session\n", pc.GREEN)
                except ClientError as e:
                    if 'bad_password' in str(e):
                        pc.printout("Error: Incorrect password. Please verify your credentials in config/credentials.ini\n", pc.RED)
                    elif 'challenge_required' in str(e):
                        pc.printout("Error: Instagram requires additional verification. Please log in through the website first\n", pc.RED)
                    else:
                        pc.printout(f"Login Error: {str(e)}\n", pc.RED)
                    sys.exit(1)
            else:
                pc.printout("Found saved session, attempting to reuse...\n", pc.YELLOW)
                try:
                    # Reuse saved settings
                    self.api = AppClient(
                        username=username,
                        password=password,
                        settings_file=settings_file)
                    pc.printout("Successfully logged in using saved session\n", pc.GREEN)
                except Exception as e:
                    pc.printout(f"Error using saved session: {str(e)}\nTrying to create new session...\n", pc.YELLOW)
                    # If reusing fails, delete the settings file and try fresh login
                    if os.path.exists(settings_file):
                        os.remove(settings_file)
                    return self.login()

            # Get target user info
            # Modified by Amulya Srivastava (2024)
            # Original tool by Datalux
            user_info = self.api.username_info(self.target)
            self.target_id = user_info['user']['pk']
            self.is_private = user_info['user']['is_private']
            self.following = user_info['user']['friendship_status']['following']

        except ClientCookieExpiredError:
            pc.printout("Cookie expired, login again..\n", pc.RED)
            self.clear_cookies()
            self.login()
        except ClientLoginRequiredError:
            pc.printout("Login required, trying to login again..\n", pc.RED)
            self.clear_cookies()
            self.login()
        except ClientError as e:
            pc.printout(f'Client Error: {e}\n', pc.RED)
            sys.exit(1)
        except Exception as e:
            pc.printout(f'Login Error: {e}\n', pc.RED)
            sys.exit(1)

    def check_private_profile(self):
        """Check if the target's profile is private and handle accordingly"""
        if self.is_private and not self.following:
            pc.printout("This account is private and you are not following it!\n", pc.RED)
            return True
        return False

    def get_followers_info(self):
        """Get both email and phone number information for followers"""
        if self.check_private_profile():
            return

        followers = []
        
        try:
            pc.printout("Searching for emails and phone numbers of target followers... this can take a few minutes\n")

            rank_token = AppClient.generate_uuid()
            data = self.api.user_followers(str(self.target_id), rank_token=rank_token)

            for user in data.get('users', []):
                u = {
                    'id': user['pk'],
                    'username': user['username'],
                    'full_name': user['full_name'],
                    'email': '',
                    'phone': ''
                }
                followers.append(u)

            next_max_id = data.get('next_max_id')
            while next_max_id:
                sys.stdout.write("\rCatched %i followers" % len(followers))
                sys.stdout.flush()
                results = self.api.user_followers(str(self.target_id), rank_token=rank_token, max_id=next_max_id)
                
                for user in results.get('users', []):
                    u = {
                        'id': user['pk'],
                        'username': user['username'],
                        'full_name': user['full_name'],
                        'email': '',
                        'phone': ''
                    }
                    followers.append(u)

                next_max_id = results.get('next_max_id')
            
            print("\n")

            results = []
            
            pc.printout("Do you want to get all information? y/n: ", pc.YELLOW)
            value = input()
            
            if value == str("y") or value == str("yes") or value == str("Yes") or value == str("YES"):
                value = len(followers)
            elif value == str(""):
                print("\n")
                return
            elif value == str("n") or value == str("no") or value == str("No") or value == str("NO"):
                while True:
                    try:
                        pc.printout("How many users info do you want to get? ", pc.YELLOW)
                        new_value = int(input())
                        value = new_value - 1
                        break
                    except ValueError:
                        pc.printout("Error! Please enter a valid integer!", pc.RED)
                        print("\n")
                        return
            else:
                pc.printout("Error! Please enter y/n :-)", pc.RED)
                print("\n")
                return

            for follow in followers:
                try:
                    user = self.api.user_info(str(follow['id']))
                    if 'public_email' in user['user'] and user['user']['public_email']:
                        follow['email'] = user['user']['public_email']
                    if 'contact_phone_number' in user['user'] and user['user']['contact_phone_number']:
                        follow['phone'] = user['user']['contact_phone_number']
                    if follow['email'] or follow['phone']:  # Only add if either email or phone exists
                        if len(results) > value:
                            break
                        results.append(follow)
                    # Add delay to avoid rate limiting
                    time.sleep(2)
                except ClientThrottledError:
                    pc.printout("\nRate limited by Instagram. Waiting 60 seconds...\n", pc.YELLOW)
                    time.sleep(60)
                    continue

        except ClientThrottledError as e:
            pc.printout("\nError: Instagram blocked the requests. Please wait a few minutes before you try again.", pc.RED)
            pc.printout("\n")

        if len(results) > 0:
            t = PrettyTable(['ID', 'Username', 'Full Name', 'Email', 'Phone'])
            t.align["ID"] = "l"
            t.align["Username"] = "l"
            t.align["Full Name"] = "l"
            t.align["Email"] = "l"
            t.align["Phone"] = "l"

            json_data = {}

            for node in results:
                t.add_row([
                    str(node['id']), 
                    node['username'], 
                    node['full_name'], 
                    node['email'] or 'Not available',
                    node['phone'] or 'Not available'
                ])

            if self.writeFile:
                file_name = self.output_dir + "/" + self.target + "_followers_info.txt"
                file = open(file_name, "w")
                file.write(str(t))
                file.close()

            if self.jsonDump:
                json_data['followers_info'] = results
                json_file_name = self.output_dir + "/" + self.target + "_followers_info.json"
                with open(json_file_name, 'w') as f:
                    json.dump(json_data, f)

            print(t)
        else:
            pc.printout("Sorry! No results found :-(\n", pc.RED)

    def get_following_info(self):
        """Get both email and phone number information for users followed by target"""
        if self.check_private_profile():
            return

        followings = []

        try:
            pc.printout("Searching for emails and phone numbers of users followed by target... this can take a few minutes\n")

            rank_token = AppClient.generate_uuid()
            data = self.api.user_following(str(self.target_id), rank_token=rank_token)

            for user in data.get('users', []):
                u = {
                    'id': user['pk'],
                    'username': user['username'],
                    'full_name': user['full_name'],
                    'email': '',
                    'phone': ''
                }
                followings.append(u)

            next_max_id = data.get('next_max_id')
            
            while next_max_id:
                sys.stdout.write("\rCatched %i following" % len(followings))
                sys.stdout.flush()
                results = self.api.user_following(str(self.target_id), rank_token=rank_token, max_id=next_max_id)

                for user in results.get('users', []):
                    u = {
                        'id': user['pk'],
                        'username': user['username'],
                        'full_name': user['full_name'],
                        'email': '',
                        'phone': ''
                    }
                    followings.append(u)

                next_max_id = results.get('next_max_id')

            print("\n")
            results = []
            
            pc.printout("Do you want to get all information? y/n: ", pc.YELLOW)
            value = input()
            
            if value == str("y") or value == str("yes") or value == str("Yes") or value == str("YES"):
                value = len(followings)
            elif value == str(""):
                print("\n")
                return
            elif value == str("n") or value == str("no") or value == str("No") or value == str("NO"):
                while True:
                    try:
                        pc.printout("How many users info do you want to get? ", pc.YELLOW)
                        new_value = int(input())
                        value = new_value - 1
                        break
                    except ValueError:
                        pc.printout("Error! Please enter a valid integer!", pc.RED)
                        print("\n")
                        return
            else:
                pc.printout("Error! Please enter y/n :-)", pc.RED)
                print("\n")
                return

            for follow in followings:
                try:
                    user = self.api.user_info(str(follow['id']))
                    if 'public_email' in user['user'] and user['user']['public_email']:
                        follow['email'] = user['user']['public_email']
                    if 'contact_phone_number' in user['user'] and user['user']['contact_phone_number']:
                        follow['phone'] = user['user']['contact_phone_number']
                    if follow['email'] or follow['phone']:  # Only add if either email or phone exists
                        if len(results) > value:
                            break
                        results.append(follow)
                    # Add delay to avoid rate limiting
                    time.sleep(2)
                except ClientThrottledError:
                    pc.printout("\nRate limited by Instagram. Waiting 60 seconds...\n", pc.YELLOW)
                    time.sleep(60)
                    continue
        
        except ClientThrottledError as e:
            pc.printout("\nError: Instagram blocked the requests. Please wait a few minutes before you try again.", pc.RED)
            pc.printout("\n")
        
        print("\n")

        if len(results) > 0:
            t = PrettyTable(['ID', 'Username', 'Full Name', 'Email', 'Phone'])
            t.align["ID"] = "l"
            t.align["Username"] = "l"
            t.align["Full Name"] = "l"
            t.align["Email"] = "l"
            t.align["Phone"] = "l"

            json_data = {}

            for node in results:
                t.add_row([
                    str(node['id']), 
                    node['username'], 
                    node['full_name'], 
                    node['email'] or 'Not available',
                    node['phone'] or 'Not available'
                ])

            if self.writeFile:
                file_name = self.output_dir + "/" + self.target + "_following_info.txt"
                file = open(file_name, "w")
                file.write(str(t))
                file.close()

            if self.jsonDump:
                json_data['following_info'] = results
                json_file_name = self.output_dir + "/" + self.target + "_following_info.json"
                with open(json_file_name, 'w') as f:
                    json.dump(json_data, f)

            print(t)
        else:
            pc.printout("Sorry! No results found :-(\n", pc.RED)

    def get_contact_info(self):
        """Get both email and phone number information for followers and following"""
        if self.check_private_profile():
            return

        pc.printout("Choose what you want to analyze:\n")
        pc.printout("1. Followers contact info\n")
        pc.printout("2. Following contact info\n")
        pc.printout("3. Both\n")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == "1":
            self.get_followers_info()
        elif choice == "2":
            self.get_following_info()
        elif choice == "3":
            pc.printout("\nGetting followers contact info...\n")
            self.get_followers_info()
            pc.printout("\nGetting following contact info...\n")
            self.get_following_info()
        else:
            pc.printout("Invalid choice! Please enter 1, 2 or 3\n", pc.RED)
            return
