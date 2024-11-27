# Osintgram-Termux

![Version](https://img.shields.io/badge/version-1.0-blue)
![Python](https://img.shields.io/badge/python-3.x-blue)
![Termux](https://img.shields.io/badge/Termux-Android-green)

Modified by Amulya Srivastava (2024)  
Based on [Datalux/Osintgram](https://github.com/Datalux/Osintgram)

## 📱 Instagram OSINT Tool for Termux

A powerful Instagram OSINT tool optimized for Termux, allowing you to gather information from Instagram accounts directly from your Android device.

### 🚀 Features

- Profile information gathering
- Followers/Following analysis
- Download profile pictures and stories
- Hashtag analysis
- Location data from posts
- Email and phone number finder
- And much more!

### 📲 Termux Installation

```bash
# Update packages
pkg update && pkg upgrade

# Install required packages
pkg install git python

# Clone this repository
git clone https://github.com/amulyasrivastava/Osintgram-Termux

# Navigate to directory
cd Osintgram-Termux

# Run setup script
bash termux_setup.sh
```

### ⚙️ Configuration

1. Edit the credentials file:
```bash
nano config/credentials.ini
```

2. Add your Instagram credentials:
```ini
[Credentials]
username = YOUR_INSTAGRAM_USERNAME
password = YOUR_INSTAGRAM_PASSWORD
```

### 🛠️ Usage

1. Run the tool:
```bash
python3 main.py <target_username>
```

2. Available commands:
- `info` - Get target info
- `followers` - Get target followers
- `followings` - Get users followed by target
- `stories` - Download target's stories
- `propic` - Download profile picture
- Type `list` to see all commands

### 📝 Example Commands

```bash
# Get basic information
python3 main.py target_username
> info

# Download profile picture
python3 main.py target_username
> propic

# Get follower list
python3 main.py target_username
> followers
```

### 📱 Termux-Specific Features

- Optimized for mobile usage
- Easy-to-use interface
- Storage access support
- Efficient resource usage

### ⚠️ Disclaimer

This tool is for educational purposes only. Users are responsible for compliance with local laws and Instagram's Terms of Service.

### 🔄 Updates

Check the [releases page](https://github.com/amulyasrivastava/Osintgram-Termux/releases) for the latest updates.

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/amulyasrivastava/Osintgram-Termux/issues).

### 👤 Author

**Amulya Srivastava**
- GitHub: [@amulyasrivastava](https://github.com/amulyasrivastava)

### 🙏 Acknowledgments

- Original tool by [Datalux](https://github.com/Datalux)
- All contributors to the original project

---
Made with ❤️ for Termux Users
