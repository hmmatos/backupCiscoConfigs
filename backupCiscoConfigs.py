import os
from netmiko import ConnectHandler
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# email configuration
SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587  # or 465 for SSL
FROM_EMAIL = "from@example.com"
TO_EMAIL = "to@example.com"
SMTP_USERNAME = "username"
SMTP_PASSWORD = "password"

def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = TO_EMAIL
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
             server.starttls()
             server.login(SMTP_USERNAME, SMTP_PASSWORD)
             server.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

def backup_config(device):
    try:
        # Settings for public key authentication
        net_connect = ConnectHandler(
            device_type=device['device_type'],
            ip=device['ip'],
            username=device['username'],
            use_keys=True,  # use ssh key
            key_file="/path/to/your/private_key.pem",  # Path to private key
            allow_agent=False,  # Disable SSH agent
        )
        net_connect.enable()
        
        # commands to run in the switch
        commands = ['show running-config', 'show version', 'show inventory']
        
        hostname = net_connect.find_prompt().strip('#')
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

        # path to save the backup files 
        backup_dir = "/path/to/your/backup_folder/"
        filename = os.path.join(backup_dir, f"{hostname}_{timestamp}.txt")
        
        with open(filename, "w") as f:
            for command in commands:
                output = net_connect.send_command(command)
                f.write(f"### {command} ###\n")
                f.write(output)
                f.write("\n\n")
        
        results.append(f"Backup successfully done for: {hostname}")
    
    except Exception as e:
        print(f"Error connecting to device {device['ip']}: {str(e)}")
        send_email(f"Backup of {device['ip']} failed", f"Error backing up device {device['ip']}: {str(e)}")
    
    finally:
        if 'net_connect' in locals():
            net_connect.disconnect()

    return results

# common settings for all devices
common_config = {
    'device_type': 'cisco_ios',
    'username': 'admin',  # user for whom the public key was configured on the device
}

# list of device IPs
ips = ['192.168.1.1', 
       '192.168.1.2'
      ] # Add more IPs as needed

# creates a list of devices
devices = [{**common_config, 'ip': ip} for ip in ips]

# store all results
all_results = []

# perform backup for each devices
for device in devices:
    all_results.extend(backup_config(device))

# email body
body = "\n".join(all_results)

# send backup report
send_email("Cisco Backup Report", body)