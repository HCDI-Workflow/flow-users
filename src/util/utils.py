import bcrypt

def hash_password(password):
    """
    Inputs:
    - password (str)

    Returns:
    - (str): hashed pass for storage
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def check_password(user_password,hashed_password):
    """
    Inputs:
    - user_password (str): password presented by user for verification
    - hashed_password (str): hashed pass in table 

    Returns:
    - (bool): True if valid pass
    """
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password.encode('utf-8'))