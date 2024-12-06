''' Date - 05 Dec 2024

    Author - Poorva Sharma
    
    Title - Key Rotation Management System
    
    Description - this is a program where you can manage your aws kms customer managed keys.
                  You can create a key here and see that key created in your console.
                  you can see the status of the key.
                  You can enable or disable the auto-rotataion.
                  Also you can do manual key rotation which will immediately 
                  create a rotated key of that key in the list as well as the console.
                  if you want you can delete key from the list which can be seen in the deleted key logs 
                  and in the console you can see their status as pending deletion.
                  So, you can basically call it your 'OWN KEY MANAGING PASSBOOK.' '''


from flask import Flask, render_template, request, redirect, url_for, session, flash
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a strong secret key for session security


# Login Page
@app.route('/')
def login():
    return render_template('login.html')


# Handle Login
@app.route('/login', methods=['POST'])
def do_login():
    access_key = request.form['access_key']
    secret_key = request.form['secret_key']
    region = request.form['region']
    
    # Test credentials by listing KMS keys
    try:
        kms_client = boto3.client(
            'kms',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        kms_client.list_keys(Limit=1)  # Test call to validate credentials
        session['access_key'] = access_key
        session['secret_key'] = secret_key
        session['region'] = region
        flash("Login successful!", "success")
        return redirect(url_for('kms_home'))
    except (NoCredentialsError, PartialCredentialsError):
        flash("Invalid AWS credentials. Please try again.", "danger")
        return redirect(url_for('login'))
    except ClientError as e:
        flash(f"AWS Error: {e.response['Error']['Message']}", "danger")
        return redirect(url_for('login'))


# KMS Management Page
@app.route('/kms_home')
def kms_home():
    try:
        kms_client = boto3.client(
            'kms',
            aws_access_key_id=session['access_key'],
            aws_secret_access_key=session['secret_key'],
            region_name=session['region']
        )
        # Fetching KMS keys, split into active and deleted keys
        response = kms_client.list_keys()
        active_keys = []
        deleted_keys = []

        for key in response['Keys']:
            key_details = kms_client.describe_key(KeyId=key['KeyId'])['KeyMetadata']
            key_info = {
                'KeyId': key_details['KeyId'],
                'KeyArn': key_details['Arn'],
                'Description': key_details.get('Description', 'No description'),
                'State': key_details['KeyState']  # Includes Enabled, Disabled, PendingDeletion
            }

            if key_info['State'] == 'PendingDeletion':
                deleted_keys.append(key_info)
            else:
                active_keys.append(key_info)

        return render_template('kms.html', keys=active_keys, deleted_keys=deleted_keys)

    except Exception as e:
        flash(f"Error fetching KMS keys: {str(e)}", "danger")
        return redirect('/login')  # Redirect to login page on error


# Enable Key Rotation
@app.route('/enable_rotation/<key_id>', methods=['POST'])
def enable_rotation(key_id):
    try:
        kms_client = boto3.client(
            'kms',
            aws_access_key_id=session['access_key'],
            aws_secret_access_key=session['secret_key'],
            region_name=session['region']
        )
        kms_client.enable_key_rotation(KeyId=key_id)
        flash(f"Key rotation enabled for Key ID: {key_id}", "success")
    except Exception as e:
        flash(f"Error enabling key rotation: {str(e)}", "danger")
    return redirect(url_for('kms_home'))


# Disable Key Rotation
@app.route('/disable_rotation/<key_id>', methods=['POST'])
def disable_rotation(key_id):
    try:
        kms_client = boto3.client(
            'kms',
            aws_access_key_id=session['access_key'],
            aws_secret_access_key=session['secret_key'],
            region_name=session['region']
        )
        kms_client.disable_key_rotation(KeyId=key_id)
        flash(f"Key rotation disabled for Key ID: {key_id}", "success")
    except Exception as e:
        flash(f"Error disabling key rotation: {str(e)}", "danger")
    return redirect(url_for('kms_home'))


# Create New Key
@app.route('/create_key', methods=['POST'])
def create_key():
    description = request.form.get('description')
    try:
        kms_client = boto3.client(
            'kms',
            aws_access_key_id=session['access_key'],
            aws_secret_access_key=session['secret_key'],
            region_name=session['region']
        )
        
        new_key = kms_client.create_key(
            Description=description,
            KeyUsage='ENCRYPT_DECRYPT',
            CustomerMasterKeySpec='SYMMETRIC_DEFAULT'
        )
        
        # Capture the key description from the form
        description = request.form['description']

        # Create the new key with the provided description
        response = kms_client.create_key(Description=description)

        # Get the new KeyId
        key_id = response['KeyId']
        
        # Optionally, create an alias for the new key to make it more readable
        alias_response = kms_client.create_alias(
            AliasName=f"alias/{description}",
            TargetKeyId=key_id
        )

        flash(f"Key created successfully with ID: {key_id}.", "success")
        return redirect('/kms_home')  # Redirect to the KMS management page after success
    except Exception as e:
        flash(f"Error creating key: {str(e)}", "danger")
        return redirect('/kms_home')  # Redirect to the KMS management page on error


# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))

# manual rotation
@app.route('/manual_rotate_key', methods=['POST'])
def manual_rotate_key():
    key_id = request.form['key_id']
    days = int(request.form['days'])  # Number of days for rotation, user-provided
    
    try:
        kms_client = boto3.client(
            'kms',
            aws_access_key_id=session['access_key'],
            aws_secret_access_key=session['secret_key'],
            region_name=session['region']
        )

        # Step 1: Create a new key
        new_key_response = kms_client.create_key(
            Description=f"Rotated version of key {key_id}",
            KeyUsage='ENCRYPT_DECRYPT',
            CustomerMasterKeySpec='SYMMETRIC_DEFAULT'
        )
        new_key_id = new_key_response['KeyMetadata']['KeyId']
        flash(f"New key created with Key ID: {new_key_id}", "success")

        # Step 2: Notify user to update resources
        flash(f"Update your resources to use the new key (Key ID: {new_key_id}).", "info")

        # Optional Step 3: Schedule the old key for disabling
        if days > 0:
            # Simulate scheduling by adding info to flash (real implementation needs a scheduler)
            flash(f"The old key ({key_id}) will be disabled in {days} days. Implement scheduling logic.", "info")
        else:
            # Disable the old key immediately
            kms_client.disable_key(KeyId=key_id)
            flash(f"Old key (Key ID: {key_id}) has been disabled.", "success")

    except Exception as e:
        flash(f"Error during manual key rotation: {str(e)}", "danger")
    
    return redirect(url_for('kms_home'))


#aliases
def fetch_alias(key_id):
    try:
        kms_client = boto3.client(
            'kms',
            aws_access_key_id=session['access_key'],
            aws_secret_access_key=session['secret_key'],
            region_name=session['region']
        )
        aliases = kms_client.list_aliases(KeyId=key_id)
        for alias in aliases['Aliases']:
            if alias.get('TargetKeyId') == key_id:
                return alias['AliasName']
        return "No Alias"
    except Exception:
        return "Error Fetching Alias"


#delete key
@app.route('/delete_key/<key_id>', methods=['POST'])
def delete_key(key_id):
    try:
        kms_client = boto3.client(
            'kms',
            aws_access_key_id=session['access_key'],
            aws_secret_access_key=session['secret_key'],
            region_name=session['region']
        )
        kms_client.schedule_key_deletion(KeyId=key_id, PendingWindowInDays=7)  # Set the deletion window to 7 days
        flash(f"Key {key_id} scheduled for deletion.", "success")
    except Exception as e:
        flash(f"Error deleting key {key_id}: {str(e)}", "danger")
    return redirect(url_for('kms_home'))

#deleted keys
@app.route('/deleted_keys')
def deleted_keys():
    try:
        kms_client = boto3.client(
            'kms',
            aws_access_key_id=session['access_key'],
            aws_secret_access_key=session['secret_key'],
            region_name=session['region']
        )
        # Fetch all keys from KMS
        response = kms_client.list_keys()
        deleted_keys = []

        for key in response['Keys']:
            # Get detailed info about the key
            key_details = kms_client.describe_key(KeyId=key['KeyId'])['KeyMetadata']
            
            # Check if the key is in 'PendingDeletion' state
            if key_details['KeyState'] == 'PendingDeletion':
                deleted_keys.append({
                    'KeyId': key_details['KeyId'],
                    'KeyArn': key_details['Arn'],
                    'Description': key_details.get('Description', 'No description'),
                    'DeletionDate': key_details.get('DeletionDate', 'No deletion date set')  # Show Deletion Date if available
                })

        return render_template('deleted_keys.html', deleted_keys=deleted_keys)

    except Exception as e:
        flash(f"Error fetching deleted keys: {str(e)}", "danger")
        return redirect('/kms_home')  # Redirect to the main page if there's an error


if __name__ == '__main__':
    app.run(debug=True)
