```markdown
# Incognito Chat

Incognito Chat is a secure, end-to-end encrypted chat application built in Python using sockets. Users can connect and communicate with each other anonymously while ensuring their messages are kept private.

## Features

- **End-to-End Encryption**: All messages are encrypted using AES.
- **Unique Connection Codes**: Each session requires a unique code for connection.
- **Active User List**: View currently connected users.
- **User-Friendly Commands**: Simple commands for assistance and user management.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Commands](#commands)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/hackinter/Incognito-Chat.git
   cd Incognito-Chat
   ```

2. **Install Required Libraries**:
   Make sure you have Python 3.x installed. Then install the required libraries using pip:
   ```bash
   pip install pycryptodome
   ```

3. **Run the Application**:
   Execute the following command to start the server:
   ```bash
   python chat_server.py
   ```

## Usage

1. **Start the Server**:
   Run the server script, and it will generate a unique connection code. Share this code with other users to allow them to connect.

2. **Connect as a Client**:
   Other users can run the client script and enter the connection code to join the chat.

3. **Commands**:
   Use the following commands in the chat:
   - `!help` - Show available commands.
   - `!users` - Display a list of active users.
   - `exit` - Disconnect from the chat.

## Commands

### Available Commands:
- `!help`: Displays help information and available commands.
- `!users`: Lists all currently connected users.
- `exit`: Disconnects from the chat session.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or inquiries, please contact [HACKINTER](no2.hackinter@sendnow.win).

---

Enjoy chatting securely with Incognito Chat!
```

Feel free to change any part of it, especially the contact section and any other details that might be specific to your project!
