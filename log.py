from colorama import init, Fore, Style

init()  # colorama


def log(caller, message, level='log'):
    if level == 'fatal error':
        print(f'[{Fore.MAGENTA}', end='')
    elif level == 'error':
        print(f'[{Fore.RED}', end='')
    elif level == 'warning':
        print(f'[{Fore.YELLOW}', end='')
    elif level == 'log':
        print(f'[{Fore.GREEN}', end='')
    elif level == 'debug':
        print(f'[{Fore.CYAN}', end='')
    else:
        print('[', end='')

    print(f'{caller}{Style.RESET_ALL}] ' + message)
