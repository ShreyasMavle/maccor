# External library
import json

from beep.structure import MaccorDatapath
import boto3

# Standard library
import os
import base64
import time

TEMP_PATH = "/tmp/"
s3 = boto3.client('s3')
bucket = "maccor-files"
token = "8072e96a74a1b860874d82e5ea980e05"


def handler(event, context):
    print("inside handler")
    filename = event['headers'].get('filename')
    if filename is None:
        return send_response(400, "Need to pass 'filename' in header")

    ip_token = event['headers'].get('token')
    if ip_token is None:
        return send_response(400, "Need to pass 'token' in header")

    if ip_token != token:
        return send_response(400, "Authorization failed")

    if 'body' not in event:
        return send_response(400, "Please upload file")

    if 'expiry' in event['headers']:
        expiry = event['headers'].get('expiry')
        if expiry.isdigit() is False:
            return send_response(400, "Please pass valid expiry")

        else:
            expiry = int(expiry)
    else:
        # Default expiry
        expiry = 60

    decoded_file = base64.b64decode(event['body'])
    timestr = time.strftime("%Y%m%d-%H%M%S")
    op_file = f"{timestr}.xlsx"
    fp = os.path.join(TEMP_PATH, filename)
    with open(fp, "wb") as f:
        f.write(decoded_file)
    datapath = MaccorDatapath.from_file(fp)
    datapath.autostructure()
    op = os.path.join(TEMP_PATH, op_file)
    datapath.structured_summary.to_excel(op, index=False)
    s3.upload_file(op, bucket, op_file)
    response = s3.generate_presigned_url('get_object',
                                         Params={'Bucket': bucket,
                                                 'Key': op_file},
                                         ExpiresIn=expiry)
    return send_response(200, response)


def send_response(status, message):
    return {
        'statusCode': status,
        'body': json.dumps({
            'status_code': status,
            'body': message
        })
    }
