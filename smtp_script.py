import os
import re
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
from typing import Tuple, List, Dict, Optional, Union
from jinja2 import Environment, FileSystemLoader

# Set logging for debug.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataRetrievalError(Exception):
    """Custom exception class to handle data retrieval errors."""
    pass

class InvalidDataFormatError(Exception):
    """Custom exception class to handle invalid data format errors."""
    pass

# Constants
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
ALERT_COLORS = {
    'success': '#28a745',
    'warning': '#ffc107',
    'danger': '#dc3545',
    'info': '#17a2b8'
}

def is_valid_email(email: str) -> bool:
    """
    Validate an email address using regex.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if the email address is valid, False otherwise.
    """
    return bool(EMAIL_REGEX.match(email))

def is_image_file(filepath: str) -> bool:
    """
    Check if a file is an image based on its extension.

    Args:
        filepath (str): The path of the file to check.

    Returns:
        bool: True if the file is an image, False otherwise.
    """
    return os.path.splitext(filepath)[1].lower() in IMAGE_EXTENSIONS

def connect_smtp(configs: Dict[str, str]) -> Tuple[smtplib.SMTP, str]:
    """
    Connects to the SMTP server using credentials fetched from a data source.

    Args:
        configs (Dict[str, str]): The configuration settings for the SMTP server.

    Returns:
        Tuple[smtplib.SMTP, str]: A tuple containing the SMTP server object and the username.

    Raises:
        DataRetrievalError: If required parameters are missing.
        smtplib.SMTPException: If connection to SMTP server fails.
    """
    required_params = ['server', 'port']
    if not all(param in configs for param in required_params):
        raise DataRetrievalError("One or more required parameters are missing.")

    server = configs['server']
    port = int(configs['port'])
    username = None if 'username' not in configs else configs['username']
    password = None if 'password' not in configs else configs['password']

    try:
        if username and password:
            smtp_server = smtplib.SMTP_SSL(server, port)
            smtp_server.login(username, password)
        else:
            smtp_server = smtplib.SMTP(server, port)

        smtp_server.ehlo()
        return smtp_server, username
    except smtplib.SMTPException as e:
        logging.error(f"Failed to connect to SMTP server: {e}")
        raise

def attach_image(msg: MIMEMultipart, image_path: str) -> None:
    """
    Attach an image to the email message with a specific Content-ID.

    Args:
        msg (MIMEMultipart): The email message object.
        image_path (str): The path to the image file.
    """
    try:
        with open(image_path, 'rb') as img:
            part = MIMEImage(img.read())
            part.add_header('Content-ID', f"<{os.path.basename(image_path)}>")
            part.add_header('Content-Disposition', 'inline', filename=os.path.basename(image_path))
            msg.attach(part)
    except IOError as e:
        logging.error(f"Failed to attach image {image_path}: {e}")

def send_email(configs: Dict[str, str], to: Union[str, List[str]], subject: str, message_body: str, html_body: bool = False,
               attachment_paths: Optional[List[str]] = None, cc: Optional[List[str]] = None,
               bcc: Optional[List[str]] = None, from_address: Optional[str] = None) -> bool:
    """
    Sends an email with optional attachments.

    Args:
        configs (Dict[str, str]): The configuration settings for the SMTP server.
        to (Union[str, List[str]]): The email address(es) of the recipient(s).
        subject (str): The subject of the email.
        message_body (str): The body of the email.
        html_body (bool): Whether the message body is HTML. Defaults to False.
        attachment_paths (Optional[List[str]]): A list of file paths to attach to the email.
        cc (Optional[List[str]]): A list of email addresses to send a carbon copy to.
        bcc (Optional[List[str]]): A list of email addresses to send a blind carbon copy to.
        from_address (Optional[str]): The email address to send the email from.

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    attachment_paths = attachment_paths or []
    cc = cc or []
    bcc = bcc or []

    try:
        server, username = connect_smtp(configs)

        if from_address and is_valid_email(from_address):
            username = from_address

        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = to if isinstance(to, str) else ', '.join(to)
        msg['Subject'] = subject

        if cc:
            msg['Cc'] = ', '.join(cc)
        if bcc:
            msg['Bcc'] = ', '.join(bcc)

        all_recipients = (to if isinstance(to, list) else [to]) + cc + bcc

        msg.attach(MIMEText(message_body, 'html' if html_body else 'plain', 'utf-8'))

        for attachment_path in attachment_paths:
            if not os.path.exists(attachment_path):
                logging.warning(f"Attachment not found: {attachment_path}")
                continue

            if is_image_file(attachment_path):
                attach_image(msg, attachment_path)
            else:
                try:
                    with open(attachment_path, 'rb') as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(attachment_path)}")
                        msg.attach(part)
                except IOError as e:
                    logging.error(f"Failed to attach file {attachment_path}: {e}")

        send_result = server.sendmail(username, all_recipients, msg.as_string())

        if not send_result:
            logging.info("Email sent successfully.")
            return True
        else:
            logging.error(f"Failed to send email to some or all recipients: {send_result}")
            return False

    except smtplib.SMTPException as e:
        logging.error(f"Error sending email: {str(e)}")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        return False
    finally:
        cleanup_connection(server)

def generate_alert(alert_type: str, alert_title: str, alert_message: str, file_names: Optional[List[str]] = None, alert_link: Optional[str] = None) -> str:
    """
    Generate an HTML alert message using a Jinja template.

    Args:
        alert_type (str): The type of alert (e.g., 'warning', 'danger', 'info', 'success').
        alert_title (str): The title of the alert message.
        alert_message (str): The main content of the alert message.
        file_names (Optional[List[str]]): List of file names to include in the alert.
        alert_link (Optional[str]): A link to include in the alert.

    Returns:
        str: An HTML string representing the alert message.
    """
    alert_color = ALERT_COLORS.get(alert_type, '#333333')

    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('./template/alert_template.html')

    html_output = template.render(
        title='Alerta de Processos ETL',
        alert_type=alert_type,
        alert_title=alert_title,
        alert_message=alert_message,
        file_names=file_names,
        alert_link=alert_link,
        alert_color=alert_color
    )

    return html_output

def send_email_template(smtp_configs: Dict[str, str], report_config: Dict[str, Union[str, List[str]]], alert_type: str, alert_title: str, alert_message: str) -> None:
    """
    Send an email notification based on the outcome of the file processing.
    It generates an alert and sends the email based on the processing status
    (success or warning).

    Args:
        smtp_configs (Dict[str, str]): Dictionary containing SMTP server configuration.
        report_config (Dict[str, Union[str, List[str]]]): Dictionary containing email notification configuration.
        alert_type (str): Type of alert (success or warning).
        alert_title (str): Title of the alert message.
        alert_message (str): Main message content of the alert.
    """
    from_mail = report_config.get("from_mail")
    to = report_config.get("to")
    subject = report_config.get("subject")
    cc_mail = report_config.get("cc")

    message_body = generate_alert(alert_type, alert_title, alert_message)
    logging.info(f"Sending email notification to {to} with subject: {subject}")
    send_email(smtp_configs, to, subject, message_body, html_body=True, cc=cc_mail, from_address=from_mail)

def cleanup_connection(smtp_server: Optional[smtplib.SMTP]) -> None:
    """
    Closes the connection to the SMTP server.

    Args:
        smtp_server (Optional[smtplib.SMTP]): The SMTP server object.
    """
    if smtp_server:
        try:
            smtp_server.quit()
        except smtplib.SMTPException as e:
            logging.error(f"Error closing SMTP connection: {str(e)}")
