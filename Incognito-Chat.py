import socket
import threading
import random
import string
import logging
import time
import json
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import scrypt
import base64

# সংস্করণ সংখ্যা
__version__ = "2.1.0"

# লগ ফাইলের জন্য সেটআপ
logging.basicConfig(filename="chat_history.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# এন্ড-টু-এন্ড এনক্রিপশন এর জন্য পাসওয়ার্ড ভিত্তিক কী এবং সল্ট
ENCRYPTION_PASSWORD = "super_secure_password"  # এটা অবশ্যই আরও সুরক্ষিত রাখা উচিত
SALT = get_random_bytes(16)  # প্রতি সেশনে নতুন সল্ট ব্যবহার করুন

# ক্লাসে ব্যবহারকারী তথ্য
class User:
    def __init__(self, code, user_id, username):
        self.code = code
        self.socket = None
        self.user_id = user_id
        self.username = username

# ইনকোগনিটেড কোড জেনারেট করার ফাংশন
def generate_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# ইউনিক এড্রেস জেনারেট করার ফাংশন
def generate_user_id(user_count):
    prefix = 'Ac1q8ku'
    return f"{prefix}{str(user_count).zfill(2)}"

# এনক্রিপ্ট ফাংশন
def encrypt_message(message, key):
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(message.encode())
    return base64.b64encode(cipher.nonce + tag + ciphertext).decode()

# ডিক্রিপ্ট ফাংশন
def decrypt_message(ciphertext, key):
    try:
        raw_data = base64.b64decode(ciphertext)
        nonce, tag, encrypted_msg = raw_data[:16], raw_data[16:32], raw_data[32:]
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(encrypted_msg, tag).decode()
    except Exception as e:
        logging.error(f"Error decrypting message: {e}")
        return None

# কী জেনারেট করার ফাংশন
def generate_encryption_key(password, salt):
    return scrypt(password.encode(), salt, key_len=32, N=2**14, r=8, p=1)

# সময় ফরম্যাটিং ফাংশন
def get_timestamp():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

# ক্লায়েন্টের জন্য ফাংশন
def client_handler(user, addr, users, encryption_key):
    logging.info(f"Connected with {addr}")
    user.socket.send(f"Welcome {user.username}! Type '!help' for commands.".encode())
    print(f"Chat started with {user.username} ({addr}). Type 'exit' to disconnect.")
    
    while True:
        try:
            message = user.socket.recv(1024).decode()
            decrypted_msg = decrypt_message(message, encryption_key)
            if decrypted_msg is None:
                print("Failed to decrypt the message.")
                continue
            if decrypted_msg.lower() == 'exit':
                print(f"{user.username} has disconnected.")
                logging.info(f"{user.username} disconnected.")
                users.remove(user)
                break
            elif decrypted_msg == '!help':
                help_message = "Commands:\n!help - Show commands\n!users - Show active users\n!exit - Disconnect"
                encrypted_help_message = encrypt_message(help_message, encryption_key)
                user.socket.send(encrypted_help_message.encode())
            elif decrypted_msg == '!users':
                active_users = ', '.join([u.username for u in users])
                encrypted_user_list = encrypt_message(f"Active users: {active_users}", encryption_key)
                user.socket.send(encrypted_user_list.encode())
            elif decrypted_msg:
                print(f"{get_timestamp()} - {user.username}: {decrypted_msg}")
                logging.info(f"Received from {user.username}: {decrypted_msg}")
                
                response = input(f"Reply to {user.username}: ")
                if response.lower() == 'exit':
                    encrypted_exit_msg = encrypt_message('exit', encryption_key)
                    user.socket.send(encrypted_exit_msg.encode())
                    print("You disconnected.")
                    break
                elif len(response) > 100:
                    print("Error: Message exceeds maximum length of 100 characters.")
                    continue

                encrypted_response = encrypt_message(response, encryption_key)
                user.socket.send(encrypted_response.encode())
                logging.info(f"Sent to {user.username}: {response}")
        except Exception as e:
            print(f"Error: {e}")
            break
    user.socket.close()

# সার্ভার ফাংশন
def start_server():
    port = random.randint(5000, 9999)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', port))
    server.listen(5)
    print(f"Incognito Chat started on port {port}. Version: {__version__}. Code: {user.code}")
    
    users = []  # সক্রিয় ইউজারদের তালিকা
    user_count = 1  # সংযোগ সংখ্যা ট্র্যাক করার জন্য
    encryption_key = generate_encryption_key(ENCRYPTION_PASSWORD, SALT)  # এনক্রিপশন কী
    
    while True:
        client_socket, addr = server.accept()
        user_id = generate_user_id(user_count)
        username = input("Enter a username: ")
        print(f"Connection from {addr[0]}:{addr[1]} established as {user_id} ({username}).")

        # কোড যাচাই
        for _ in range(3):  # ৩ বার চেষ্টা করার সুযোগ
            code = input("Enter your unique code to connect: ")
            if code == user.code:
                print(f"Code verified! {username} connected.")
                user_count += 1  # সংযোগ সংখ্যা বৃদ্ধি
                new_user = User(user.code, user_id, username)
                new_user.socket = client_socket
                users.append(new_user)  # সক্রিয় ইউজার তালিকায় যোগ করা হচ্ছে
                thread = threading.Thread(target=client_handler, args=(new_user, addr, users, encryption_key))
                thread.start()
                break
            else:
                print("Invalid code! Try again.")
        else:
            print("Maximum attempts reached. Connection denied.")
            client_socket.close()

# সাহায্য ফাংশন
def show_help():
    print(f"""
    Welcome to Incognito Chat!
    
    Commands:
    1. Run the script to generate a connection code.
    2. Other users can connect using this code.
    3. Each user will receive a unique address (ID) and can choose a username.
    4. Type '!help' for commands.
    5. Type '!users' to see active users.
    6. Type 'exit' to disconnect from the chat.
    7. All messages are end-to-end encrypted.
    
    Version: {__version__}
    """)

def main():
    # ASCII আর্ট
    ascii_art = r"""
██ ███    ██  ██████  ██████   ██████  ███    ██ ██ ████████  ██████         ██████ ██   ██  █████  ████████ 
██ ████   ██ ██      ██    ██ ██       ████   ██ ██    ██    ██    ██       ██      ██   ██ ██   ██    ██    
██ ██ ██  ██ ██      ██    ██ ██   ███ ██ ██  ██ ██    ██    ██    ██ █████ ██      ███████ ███████    ██    
██ ██  ██ ██ ██      ██    ██ ██    ██ ██  ██ ██ ██    ██    ██    ██       ██      ██   ██ ██   ██    ██    
██ ██   ████  ██████  ██████   ██████  ██   ████ ██    ██     ██████         ██████ ██   ██ ██   ██    ██    
    """
    
    print(ascii_art)  # ASCII আর্ট প্রদর্শন করুন

    # কোড জেনারেট করুন
    global user
    unique_code = generate_code()
    user = User(unique_code, None, None)  # প্রাথমিকভাবে কোনো user_id এবং username নেই

    show_help()  # সাহায্য দেখান
    print("Generated code:", unique_code)

    # সার্ভার শুরু করুন
    start_server()

if __name__ == "__main__":
    print(f"Incognito Chat Version: {__version__}")
    main()
