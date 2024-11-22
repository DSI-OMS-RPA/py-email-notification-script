# Python Email Notification System

## Description

The Email Notification System is a robust, feature-rich Python library for sending professional-grade email notifications with advanced templating capabilities. It's specifically designed for enterprise environments, supporting both simple emails and complex templated notifications with rich formatting, tables, and status tracking.

## Features

### Core Functionality
- Object-oriented design with robust error handling
- Support for both regular and templated emails
- SSL/TLS support for secure email transmission
- Configurable SMTP settings via INI file
- Comprehensive logging and error tracking

### Email Features
- HTML and plain text email support
- File attachments with automatic MIME type detection
- CC and BCC recipient support
- Custom sender address configuration
- Support for inline images and company logos

### Template Features
- Professional alert templates with customizable styles
- Multiple alert types (success, warning, danger, info)
- Dynamic color schemes with custom color support
- Responsive design for mobile compatibility
- Built-in date formatting and time zone support

### Data Visualization
- Built-in table formatting with alternating row colors
- Summary statistics display
- Pagination support for large datasets
- Custom status badges and icons
- File processing status tracking

### Advanced Features
- Interactive action buttons with custom URLs
- File status tracking with color-coded indicators
- Environment indicators (production, development, etc.)
- Metadata support for file processing
- Timestamp formatting and customization

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/python-email-notification-system.git
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Create a `config.ini` file with your SMTP settings:
```ini
[SMTP]
server = smtp.your-server.com
port = 587
username = your_username@domain.com
password = your_password
```

## Usage Examples

### Basic Email
```python
from email_sender import EmailSender

# Initialize the sender
email_sender = EmailSender(smtp_configs)

# Send a simple email
email_details = {
    'to': 'recipient@domain.com',
    'subject': 'Test Email',
    'message_body': '<p>This is a test email.</p>',
    'html_body': True,
    'attachment_paths': ['document.pdf'],
    'from_address': 'sender@domain.com'
}

email_sender.send_email(**email_details)
```

### Templated Alert with Tables and Files
```python
# Define table data
table_data = [
    {
        "Process": "ETL-001",
        "Status": "Completed",
        "Records": 1500,
        "Duration": "00:05:23"
    },
    {
        "Process": "ETL-002",
        "Status": "Completed",
        "Records": 2300,
        "Duration": "00:07:45"
    }
]

# Define summary statistics
summary_data = [
    {"label": "Total Processes", "value": "2"},
    {"label": "Total Records", "value": "3,800"},
    {"label": "Success Rate", "value": "100%"}
]

# Define file status information
file_data = {
    'data1.csv': {
        'status': 'Completed',
        'metadata': '2.5 MB, 1,500 records'
    },
    'data2.xlsx': {
        'status': 'Processing',
        'metadata': '1.8 MB, 800 records'
    }
}

# Send templated email
email_sender.send_template_email(
    report_config={
        'from_mail': 'sender@domain.com',
        'to': 'recipient@domain.com',
        'subject': 'ETL Process Report'
    },
    alert_type='success',
    alert_title='ETL Process Complete',
    alert_message='All ETL processes completed successfully.',
    table_data=table_data,
    summary_data=summary_data,
    file_names=list(file_data.keys()),
    file_status={name: data['status'] for name, data in file_data.items()},
    file_metadata={name: data['metadata'] for name, data in file_data.items()},
    action_button={
        'url': 'https://your-dashboard.com',
        'text': 'View Details',
        'icon': '👉'
    },
    environment='production'
)
```

## Template Customization

The system includes a customizable HTML template (`alert_template.html`) that supports:
- Company branding with logo
- Color-coded alert types
- Responsive tables
- Status indicators
- Action buttons
- File processing status
- Environmental indicators

## Error Handling

The system includes comprehensive error handling with custom exceptions:
- `EmailError`: Base exception class
- `DataRetrievalError`: For configuration and data issues
- `InvalidDataFormatError`: For format validation errors
- `SMTPConnectionError`: For connection-related issues

## Logging

Built-in logging provides detailed information about:
- Email sending status
- Template rendering
- SMTP connections
- File attachments
- Error details

## Requirements

- Python 3.7+
- Jinja2
- email
- smtplib
- logging

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please:
- Open an issue in the GitHub repository
- Check the documentation
- Review the example code in the `examples` directory
