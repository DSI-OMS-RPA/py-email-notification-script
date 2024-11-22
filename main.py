from email_sender import EmailSender
import configparser

def main():

    # Load configuration settings from ini file
    ini_configs = configparser.ConfigParser()
    ini_configs.read('config.ini')
    smtp_configs = dict(ini_configs.items("SMTP"))

    # Create an instance of EmailSender
    email_sender = EmailSender(smtp_configs)

    # Sample table data
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

    # Define summary data
    summary_data = [
        {"label": "Total Processes", "value": "2"},
        {"label": "Total Records", "value": "3,800"},
        {"label": "Success Rate", "value": "100%"}
    ]

    # Define the alert parameters for the email template
    alert_info = {
        'alert_type': 'success',
        'alert_title': 'ETL Process Complete',
        'alert_message': 'All ETL processes completed successfully.'
    }

    # Define the email parameters
    email_details = {
        'to': 'joselito.coutinho@cvt.cv',
        'subject': 'Test Email',
        'message_body': '<p>This is a test email.</p>',
        'html_body': True,
        'attachment_paths': ['pdf-sample.pdf'],
        'cc': [],
        'bcc': [],
        'from_address': 'DSI-DEV-RPA@cvt.cv'
    }

    # Define the report configuration
    report_config = {
        'from_mail': email_details['from_address'],
        'to': email_details['to'],
        'subject': alert_info['alert_title'],
        'cc': email_details['cc']
    }

    # Define the report configuration
    report_config = {
        'from_mail': email_details['from_address'],
        'to': email_details['to'],
        'subject': alert_info['alert_title'],
        'cc': email_details['cc']
    }



    # Send the regular email
    email_sender.send_email(**email_details)

    # Send the template email with all new features
    email_sender.send_template_email(
        report_config=report_config,
        alert_type=alert_info['alert_type'],
        alert_title=alert_info['alert_title'],
        alert_message=alert_info['alert_message'],
        table_data=table_data,
        company_logo='logo.png',  # Optional
        summary_data=summary_data,
        table_summary=['Total', '3,800', '00:13:08'],
        total_records=2,
        show_pagination=True,
        file_status={'data1.csv': 'Processed', 'data2.csv': 'Completed'},
        error_details=None,  # Optional, for error cases
        action_button={
            'url': 'https://your-dashboard.com',
            'text': 'View Details'
        },
        environment='production',
        timestamp='2024-01-22 15:30:00'
    )

if __name__ == "__main__":
    main()
