#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import argparse
import time
import uuid
import csv
from sys import stdout
from getpass import getpass


ENDPOINT = 'https://api.github.com/users/'
CHARS = "abcdefghijklmnopqrstuvwxyz"
MOVE_TO_BOL = b'\r'
CLEAR_TO_EOL = b'\x1b[K'

def clear_line():
    stdout.buffer.write(b'\x1b[%s' % MOVE_TO_BOL)
    stdout.buffer.write(b'\x1b[%s' % CLEAR_TO_EOL)

def prompt_user_for_github_auth():
    return input('GitHub user: ')

def prompt_pass_for_github_auth(user=None):
    if user:
        return getpass(f'GitHub pass for {user}: ')
    else:
        return getpass('GitHub pass: ')

class GitHubAuthException(Exception):
    pass

def status_char_generator():
    status_chars = list('-/|\\')
    i = 0
    while True:
        yield status_chars[i % len(status_chars)]
        i += 1


def username_generator(length=1):
    def increment_user_string(user=None):
        if user == None:
            user = CHARS[0] * length
            verbose_print('Initializating user to ' + user)
            return user
        else:
            verbose_print('Incrementing ' + user)
            user_list = list(user)
            for a,c in enumerate(user_list):
                i = CHARS.index(c)
                if i >= len(CHARS) - 1:
                    user_list[a] = CHARS[0]
                    continue
                else:
                    user_list[a] = CHARS[i + 1]
                    break
            user = ''.join(user_list)
            verbose_print('Incremented user: ' + user)
            return user
        
    user = None
    while user !=  CHARS[-1] * length:
        user = increment_user_string(user)
        yield user

def write_users_file(users, filename=None):
    if filename == None:
        filename = '/tmp/' + str(uuid.uuid4()) + '.csv'
    verbose_print(f'Writing users to file {filename}', *users)
    with open(filename, "w") as f:
        writer = csv.writer(f)
        writer.writerows([["user", "exists"]])
        writer.writerows(users)
    print(f'Wrote queried users to {filename}')

def query_user(user, auth):
    try: 
        r = requests.get(ENDPOINT + user, auth=auth)

        verbose_print(f'Status code: {r.status_code}')
        verbose_print(f'Query response: {r.text}')

        if r.status_code == 200:
            verbose_print(f'User {user} exists')
            return (user, True)
        elif r.status_code == 404:
            verbose_print(f'User {user} not found')
            return (user, False)
        elif r.status_code == 401:
            verbose_print(f'Authentication for GitHub user {auth[0]} seems to fail')
            raise GitHubAuthException(f'Error authenticating user {auth[0]}')
        else:
            verbose_print(f'Unexpected status code {r.status_code}')
            raise Exception('An unexpected status code was \
                    returned when trying to fetch user ' + user)
    except Exception as e:
        raise e
    finally:
        clear_line()

def main(length, github_user, github_pass, write_results, 
        output_file=None, input_file=None, delay=0.2):

    global verbose_print
    if not verbose_print:
        verbose_print = lambda *a: None

    users = []

    try: 
        if input_file != None:
            fd = open(input_file, 'r')
            username_provider = fd.read().splitlines()
            fd.close()
        else:
            username_provider = username_generator(length=length)

        status_char = status_char_generator()

        for user in username_provider:
            sc = next(status_char)
            clear_line()
            stdout.write(f'[{sc}] Querying user {user}')
            stdout.flush()
            user_row = query_user(user, (github_user, github_pass))
            
            users.append(user_row)

            time.sleep(delay)

    except FileNotFoundError:
        verbose_print('It seems that we cannot find the input file')
        print(f'File {input_file} not found')
    except KeyboardInterrupt:
        print('User interrupted the execution. Going home...')
        return -1
    except GitHubAuthException as e:
        write_results = False
        print(str(e))
        return -1
    except Exception as e:
        raise e
    finally:
        if write_results:
            write_users_file(users, filename=output_file)

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Find free GitHub usernames')
    parser.add_argument('-d', '--delay',
                        type=float, 
                        default=0.2,
                        dest='delay',
                        help='delay between queries')

    parser.add_argument('-l', '--length',
                        type=int, 
                        default=1,
                        dest='length',
                        help='length of usernames')

    parser.add_argument('-o', '--output-file',
                        type=str, 
                        dest='output_file',
                        help='output file')

    parser.add_argument('-i', '--input-file',
                        type=str, 
                        dest='input_file',
                        help='input file with usernames')

    parser.add_argument('--no-output',
                        action='store_false',
                        dest='write_results',
                        help='disable writing results to a file')

    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        dest='verbose',
                        help='enable verbose messages')

    parser.add_argument('-u', '--user',
                        type=str, 
                        dest='github_user',
                        help='GitHub user for authentication')

    parser.add_argument('-p', '--pass',
                        type=str, 
                        dest='github_pass',
                        help='GitHub password for authentication')

    parser.add_argument('--version', action='version', version='%(prog)s 1.0')

    opt = parser.parse_args()
    global verbose_print
    if opt.verbose:
        def verbose_print(*args): 
            for a in args:
                print(f'[*] {a}')
    else:
        verbose_print = lambda *a: None

    github_user = opt.github_user if opt.github_user != None else prompt_user_for_github_auth()
    github_pass = opt.github_pass if opt.github_pass != None else prompt_pass_for_github_auth(github_user)
    verbose_print(f'Using GitHub user for authentication: {github_user}')
    verbose_print(f'Using GitHub endpoint: {ENDPOINT}')
    verbose_print(f'Using a length of {opt.length} characters for usernames')

    main(opt.length, github_user, github_pass, opt.write_results,
            output_file=opt.output_file,
            input_file=opt.input_file,
            delay=opt.delay)
