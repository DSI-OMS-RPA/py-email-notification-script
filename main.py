from smtp_script import send_email, send_email_template
import configparser

def main():

    # Load configuration settings from ini file.
    ini_configs = configparser.ConfigParser()
    ini_configs.read('config.ini')
    smtp_configs = dict(ini_configs.items("SMTP"))

    table_data = [
        {
            'Product': 'Product A',
            'Units Sold': '1,200',
            'Revenue': '$24,000',
            'Growth': '+15%'
        },
        {
            'Product': 'Product B',
            'Units Sold': '800',
            'Revenue': '$32,000',
            'Growth': '+8%'
        },
        {
            'Product': 'Product C',
            'Units Sold': '600',
            'Revenue': '$18,000',
            'Growth': '-3%'
        }
    ]

    # Define the email parameters.
    email_details = {
        'to': 'joselito.coutinho@cvt.cv',
        'subject': 'Test Email',
        'message_body': '<p>This is a test email.</p>',
        'html_body': True,
        'attachment_paths': ['pdf-sample.pdf'],
        'cc': ["eric.tavares@cvt.cv"],
        'bcc': [],
        'from_address': 'DSI-DEV-RPA@cvt.cv'
    }

    # Define the alert parameters for the email template with all options
    alert_info = {
        'alert_type': 'success',  # Options: 'success', 'warning', 'error'
        'alert_title': 'Test Alert',
        'alert_message': 'This is a test alert message.',
        'attachment_paths': ['pdf-sample.pdf'],
        'table_data': table_data,
        'file_names': ['report1.csv', 'report2.xlsx'],  # Files to mention in the alert message
        'alert_link': 'https://your-dashboard-link.com'  # Optional link in the alert
    }

    # Define the report configuration.
    report_config = {
        'from_mail': email_details['from_address'],
        'to': email_details['to'],
        'subject': alert_info['alert_title'],
        'cc': email_details['cc']
    }

    # Send the email.
    send_email(smtp_configs, **email_details)

    # Send the email with template.
    send_email_template(smtp_configs, report_config, **alert_info)

if __name__ == "__main__":
    main()
