import os
import re
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
from typing import Any, Tuple, List, Dict, Optional, Union
from jinja2 import Environment, FileSystemLoader
from contextlib import contextmanager
from pathlib import Path
from functools import lru_cache

# Set logging for debug with a more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

class EmailError(Exception):
    """Base exception class for email-related errors."""
    pass

class DataRetrievalError(EmailError):
    """Exception class to handle data retrieval errors."""
    pass

class InvalidDataFormatError(EmailError):
    """Exception class to handle invalid data format errors."""
    pass

class SMTPConnectionError(EmailError):
    """Exception class to handle SMTP connection errors."""
    pass

# Constants moved to a class for better organization
class EmailConstants:
    IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    ALERT_COLORS = {
        'success': '#28a745',
        'warning': '#ffc107',
        'danger': '#dc3545',
        'info': '#17a2b8'
    }
    REQUIRED_SMTP_PARAMS = {'server', 'port'}

@contextmanager
def smtp_connection(configs: Dict[str, str]) -> smtplib.SMTP:
    """
    Context manager for SMTP connections.

    Args:
        configs (Dict[str, str]): The configuration settings for the SMTP server.

    Yields:
        smtplib.SMTP: The SMTP connection object.

    Raises:
        SMTPConnectionError: If connection fails.
    """
    smtp_server = None
    try:
        smtp_server, _ = connect_smtp(configs)
        yield smtp_server
    finally:
        cleanup_connection(smtp_server)

def validate_config(configs: Dict[str, str]) -> None:
    """
    Validate SMTP configuration parameters.

    Args:
        configs (Dict[str, str]): The configuration settings to validate.

    Raises:
        DataRetrievalError: If required parameters are missing.
    """
    missing_params = EmailConstants.REQUIRED_SMTP_PARAMS - set(configs.keys())
    if missing_params:
        raise DataRetrievalError(f"Missing required parameters: {missing_params}")

@lru_cache(maxsize=100)
def is_valid_email(email: str) -> bool:
    """
    Validate an email address using regex with caching.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if the email address is valid, False otherwise.
    """
    return bool(EmailConstants.EMAIL_REGEX.match(email))

def is_image_file(filepath: str) -> bool:
    """
    Check if a file is an image based on its extension.

    Args:
        filepath (str): The path of the file to check.

    Returns:
        bool: True if the file is an image, False otherwise.
    """
    return Path(filepath).suffix.lower() in EmailConstants.IMAGE_EXTENSIONS

def connect_smtp(configs: Dict[str, str]) -> Tuple[smtplib.SMTP, str]:
    """
    Connects to the SMTP server using credentials.

    Args:
        configs (Dict[str, str]): The configuration settings for the SMTP server.

    Returns:
        Tuple[smtplib.SMTP, str]: SMTP server object and username.

    Raises:
        SMTPConnectionError: If connection fails.
    """
    validate_config(configs)

    try:
        server = configs['server']
        port = int(configs['port'])
        username = configs.get('username')
        password = configs.get('password')

        if username and password:
            smtp_server = smtplib.SMTP_SSL(server, port)
            smtp_server.login(username, password)
        else:
            smtp_server = smtplib.SMTP(server, port)

        smtp_server.ehlo()
        return smtp_server, username
    except (smtplib.SMTPException, ValueError) as e:
        raise SMTPConnectionError(f"Failed to connect to SMTP server: {e}")

def attach_file(msg: MIMEMultipart, file_path: str) -> None:
    """
    Attach a file to the email message.

    Args:
        msg (MIMEMultipart): The email message object.
        file_path (str): Path to the file to attach.
    """
    if not Path(file_path).exists():
        logger.warning(f"Attachment not found: {file_path}")
        return

    try:
        if is_image_file(file_path):
            with open(file_path, 'rb') as img:
                part = MIMEImage(img.read())
                part.add_header('Content-ID', f"<{Path(file_path).name}>")
                part.add_header('Content-Disposition', 'inline', filename=Path(file_path).name)
        else:
            with open(file_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f"attachment; filename= {Path(file_path).name}")

        msg.attach(part)
    except IOError as e:
        logger.error(f"Failed to attach file {file_path}: {e}")

def send_email(configs: Dict[str, str], to: Union[str, List[str]], subject: str,
               message_body: str, html_body: bool = False,
               attachment_paths: Optional[List[str]] = None,
               cc: Optional[List[str]] = None,
               bcc: Optional[List[str]] = None,
               from_address: Optional[str] = None) -> bool:
    """
    Sends an email with optional attachments.
    """
    attachment_paths = attachment_paths or []
    cc = cc or []
    bcc = bcc or []

    try:
        with smtp_connection(configs) as server:
            msg = MIMEMultipart()
            username = from_address if from_address and is_valid_email(from_address) else configs.get('username')

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
                attach_file(msg, attachment_path)

            server.sendmail(username, all_recipients, msg.as_string())
            logger.info("Email sent successfully")
            return True

    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False

def get_rgba_color(hex_color: str, opacity: float = 1.0) -> str:
    """
    Convert hex color to rgba color with opacity.

    Args:
        hex_color (str): Hex color code (e.g., '#28a745' or '28a745')
        opacity (float): Opacity value between 0 and 1

    Returns:
        str: RGBA color string
    """
    # Remove '#' if present
    hex_color = hex_color.lstrip('#')

    # Convert hex to RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    # Return rgba string
    return f"rgba({r}, {g}, {b}, {opacity})"

@lru_cache(maxsize=1)
def get_template_env() -> Environment:
    """
    Get Jinja2 environment with caching.

    Returns:
        Environment: Configured Jinja2 environment.
    """
    template_dir = Path(__file__).parent
    return Environment(loader=FileSystemLoader(template_dir))

def generate_alert(
    alert_type: str,
    alert_title: str,
    alert_message: str,
    file_names: Optional[List[str]] = None,
    alert_link: Optional[str] = None,
    table_data: Optional[List[Dict[str, Any]]] = None) -> str:
    """
    Generate an HTML alert message using a Jinja template.

    Args:
        alert_type (str): Type of alert ('success', 'warning', 'danger', 'info')
        alert_title (str): Title of the alert
        alert_message (str): Main message content
        file_names (Optional[List[str]]): List of processed file names
        alert_link (Optional[str]): URL for the detail button
        table_data (Optional[List[Dict[str, Any]]]): List of dictionaries containing the table data where dict keys are column headers

    Returns:
        str: Rendered HTML template
    """
    alert_color = EmailConstants.ALERT_COLORS.get(alert_type, '#333333')
    env = get_template_env()
    template = env.get_template('./template/alert_template.html')

    # Extract headers from the first row if table data exists
    table_headers = list(table_data[0].keys()) if table_data else None

    return template.render(
        html_title='Alert Notification',
        alert_type=alert_type,
        alert_title=alert_title,
        alert_message=alert_message,
        file_names=file_names,
        alert_link=alert_link,
        alert_color=alert_color,
        table_headers=table_headers,
        table_data=table_data
    )

def send_email_template(smtp_configs: Dict[str, str],
    report_config: Dict[str, Union[str, List[str]]],
    alert_type: str,
    alert_title: str,
    alert_message: str,
    attachment_paths: Optional[List[str]] = None,
    file_names: Optional[List[str]] = None,
    alert_link: Optional[str] = None,
    table_data: Optional[List[Dict[str, Any]]] = None) -> bool:
    """
    Send an email notification with a template.

    Args:
        smtp_configs: SMTP server configuration
        report_config: Email report configuration
        alert_type: Type of alert ('success', 'warning', 'danger', 'info')
        alert_title: Title of the alert
        alert_message: Main message content
        attachment_paths: List of file paths to attach
        file_names: List of processed file names to display
        alert_link: URL for the detail button
        table_data: List of dictionaries containing the table data where dict keys are column headers

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        message_body = generate_alert(
            alert_type=alert_type,
            alert_title=alert_title,
            alert_message=alert_message,
            file_names=file_names,
            alert_link=alert_link,
            table_data=table_data
        )

        logger.info(f"Sending template email notification to {report_config['to']}")

        return send_email(
            smtp_configs,
            report_config['to'],
            report_config['subject'],
            message_body,
            html_body=True,
            cc=report_config.get('cc'),
            from_address=report_config.get('from_mail'),
            attachment_paths=attachment_paths
        )

    except Exception as e:
        logger.error(f"Failed to send template email: {str(e)}")
        return False

def cleanup_connection(smtp_server: Optional[smtplib.SMTP]) -> None:
    """
    Closes the connection to the SMTP server.
    """
    if smtp_server:
        try:
            smtp_server.quit()
        except smtplib.SMTPException as e:
            logger.error(f"Error closing SMTP connection: {str(e)}")
