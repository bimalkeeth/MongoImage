import boto3
from datetime import datetime, timezone ,timedelta
import dateutil


def days_diff(d1, d2):
    return abs((d2 - d1).days)


if __name__ == '__main__':
    client = boto3.client('ec2')

    custom_imagefiler = [
        {
            'Name': 'name',
            'Values': ['*jenkinsvpc-mongo*']
        }
    ]

    imageResult = client.describe_images(Filters=custom_imagefiler)
    print(imageResult)
    for image in imageResult['Images']:

        date = dateutil.parser.parse(image['CreationDate'])
        date.replace(tzinfo=None)
        todayDate = datetime.now(timezone.utc)

        dateDiff = days_diff(date, todayDate)
        if dateDiff > 5:
            response = client.deregister_image(
                ImageId=image['ImageId'],
            )
        else:
            print(image['ImageId'] + '-' + 'is still valid')

    custom_filter = [{
        'Name': 'tag:Name',
        'Values': ['*vpc-mongo*']
    },
        {
            'Name': 'tag:awsbackup',
            'Values': ['yes']
        },
        {
            'Name': 'instance-state-name',
            'Values': ['running']
        }]
    result = client.describe_instances(Filters=custom_filter)
    for item in result['Reservations']:

        name = ''
        for instance in item['Instances']:

            for tag in instance['Tags']:
                if tag['Key'] != '':
                    name = tag['Value']
                    break
            amiName = "jenkins" + name + "-" + datetime.strftime(datetime.utcnow(), '%Y%m%d%H%M%S')
            client.create_image(InstanceId=instance['InstanceId'], Name=amiName, NoReboot=True)
