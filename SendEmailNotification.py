import email, smtplib, ssl, socket
import traceback

import InvestigateFile
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def notify_errors(file_path, event_type, err_date, error_line):
    subject = InvestigateFile.get_value_from_properties_file_by_key("EMAILSUBJECT")
    # body = InvestigateFile.get_value_from_properties("BODY_MSG")
    body = "<html><body>" + InvestigateFile.get_value_from_properties_file_by_key(
        "BODY_MSG") + " <b>" + err_date + "</b> <p style='background-color:yellow;'><b>Errorline:</b> " + error_line + "</p> <br><br>" + InvestigateFile.get_value_from_properties_file_by_key(
        "FOOTER") + "</body></html> "
    sender_email = InvestigateFile.get_value_from_properties_file_by_key("SENDEREMAIL")
    to_emails = InvestigateFile.get_value_from_properties_file_by_key("RECIEVEREMAILS").split(",")
    cc_emails = InvestigateFile.get_value_from_properties_file_by_key("CC_RECEIVERS").split(",")
    bcc_emails = InvestigateFile.get_value_from_properties_file_by_key("BCC_RECEIVERS").split(",")
    password = InvestigateFile.get_value_from_properties_file_by_key("SENDEREMAILPASSWORD")
    smtp_details = InvestigateFile.get_value_from_properties_file_by_key("SMTP")
    smtp_port = InvestigateFile.get_value_from_properties_file_by_key("PORT")
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = ", ".join(to_emails)
    message["Cc"] = ", ".join(cc_emails)
    message["Bcc"] = ", ".join(bcc_emails)
    message["Subject"] = subject + " " + socket.gethostname();
    # Add body to email
    # message.attach(MIMEText(body, "plain"))
    message.attach(MIMEText(body, "html"))
    mail_body = message.as_string()
    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_details, smtp_port, context=context) as server:
        try:
            server.login(sender_email, password)
        except Exception:
            print("Unable to login to smtp server")
            traceback.print_exc()
        try:
            server.sendmail(sender_email, to_emails, mail_body)
            print("Email sent successfully")
        except Exception:
            print("Unable to send email")
            traceback.print_exc()
        server.quit()
