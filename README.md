# Email Notification Script

## Description

The Email Notification Script is a Python-based tool designed to simplify the process of sending both standard and templated email notifications. It's particularly useful for automated reporting systems, alert mechanisms, and any scenario where programmatic email sending is required.

## Features

- Send standard emails with attachments
- Send templated email alerts with customizable styles
- Support for CC and BCC recipients
- Configurable SMTP settings via INI file
- Flexible alert types (success, warning, danger, info)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/email-notification-system.git
   ```
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration

1. Rename `config.ini.example` to `config.ini`
2. Edit `config.ini` and add your SMTP server details:
   ```
   [SMTP]
   server = your_smtp_server
   port = your_smtp_port
   username = your_username
   password = your_password
   ```

## Usage

Run the main script:

```
python main.py
```

This will send a test email and a test alert using the configuration specified in the script.

To use in your own projects, import the necessary functions:

```python
from smtp_script import send_email, send_email_template
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
