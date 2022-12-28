class Config:
    api_id = 2813091
    api_hash = "afed039a8fa0870e1bf0ca9638b93d60"


    help_message = """
    
      Skip to line 4 if you are already logged in
    
        1. Go to <Website>
        2. Login using your phone number
        3. Get the session file
        4. Send the session file here
    
    Unlocking Messages
    
        5. Go to the restricted message
        6. Copy the message link and paste it here.
                
        ex: https://t.me/c/1895736852/18
    
    Unlocking multiple messages
        
        7. Replace the end of the message with the ids of the first and the last post.
        
        ex : https://t.me/c/1895736852/18-25
    """

    phone_request = """
        Send your Phone number to log in.
        \n[*]  With the country code\n[*]  with '+' \n[*]  without any spaces\n
        \nex: +1408XXXXXXX
    """

    code_request = """
        Please Send the conformation code.
        \n[*]  IMPORTANT: Please make sure you keep a space in between every number to avoid Telegram Restrictions.\n
        ex: 1 4 5 2 3
    """

    password_request = """
        Two step verification is enabled. Please Send the password with a password tag\n
        \nex: /password mypassword1234                
    """

    phone_regex = "\+(9[976]\d|8[987530]\d|6[987]\d|5[90]\d|42\d|3[875]\d|2[98654321]\d|9[8543210]|8[6421]|6[6543210]|5[87654321]|4[987654310]|3[9643210]|2[70]|7|1)\d{1,14}$"