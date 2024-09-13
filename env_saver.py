import os

def save_dict_to_env_file(dictionary, filename='.env'):
    """
    Saves a dictionary to a .env file.

    Args:
        dictionary (dict): The dictionary to save.
        filename (str, optional): The filename to save to. Defaults to '.env'.
    """
    with open(filename, 'w') as f:
        for key, value in dictionary.items():
            f.write(f"{key}={value}\n")

def read_env_file_to_dict(filename='.env'):
    """
    Reads a .env file and returns a dictionary.

    Args:
        filename (str, optional): The filename to read from. Defaults to '.env'.

    Returns:
        dict: The dictionary read from the file.
    """
    dictionary = {}
    with open(filename, 'r') as f:
        for line in f:
            if line.strip():
                key, value = line.strip().split('=')
                dictionary[key] = value
    return dictionary

def update_env_var(key, value):
    dict = read_env_file_to_dict()
    bkp_filename = f"env_bkp/env_{dict["BACKUP"]}.txt"
    
    save_dict_to_env_file(dict, bkp_filename)
    dict["BACKUP"] = str(int(dict["BACKUP"]) + 1)
    dict[key] = value
    save_dict_to_env_file(dict)

def update_env_vars(new_dict):
    dict = read_env_file_to_dict()
    bkp_filename = f"env_bkp/env_{dict["BACKUP"]}.txt"
    
    save_dict_to_env_file(dict, bkp_filename)
    dict["BACKUP"] = str(int(dict["BACKUP"]) + 1)
    for key, value in new_dict.items():
        dict[key] = value
    save_dict_to_env_file(dict)