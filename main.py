from smtp_script import send_email, send_email_template
import configparser

def main():

    # Load configuration settings from ini file.
    ini_configs = configparser.ConfigParser()
    ini_configs.read('config.ini')
    smtp_configs = dict(ini_configs.items("SMPT"))

    # Define the email parameters.
    email_details = {
        'to': 'joselito.coutinho@cvt.cv',
        'subject': 'Test Email',
        'message_body': '<p>This is a test email.</p>',
        'html_body': False,
        'attachment_paths': ['pdf-sample.pdf'],
        'cc': [],
        'bcc': [],
        'from_address': 'DSI-DEV-RPA@cvt.cv'
    }

    # Define the alert parameters for the email template.
    alert_info = {
        'alert_type': 'success',
        'alert_title': 'Test Alert',
        'alert_message': 'This is a test alert message.'
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
