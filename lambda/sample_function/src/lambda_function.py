def lambda_handler(event, context):
    'sample script'


def test():
    event = {
        'Records': [{
            'eventVersion': '2.1',
            'eventSource': 'aws:s3',
            'awsRegion': 'us-west-2',
            'eventTime': '2020-06-25T15:04:13.462Z',
            'eventName': 'ObjectCreated:Put',
            'userIdentity': {'principalId': 'AWS:XXXXXXXXXXXXXXXXXXXXX'},
            'requestParameters': {'sourceIPAddress': '000.000.000.000'},
            'responseElements': {
                'x-amz-request-id': 'XXXXXXXXXXXXXXXX',
                'x-amz-id-2': 'XXXXXXXXXXXXXXXXXXXXXX+XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX='
    },
            's3': {
                's3SchemaVersion': '1.0',
                'configurationId': 'XXXXXXXX-XXXX-XXXX-XXXXXXXXXXXXXXXXX',
                'bucket': {
                    'name': '<bucket name>',
                    'ownerIdentity': {'principalId': 'XXXXXXXXXXXXX'},
                    'arn': 'arn:aws:s3:::<bucket name>'
                },
                'object': {
                    'key': '<key name>',
                    'size': 0,
                    'eTag': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
                    'sequencer': 'XXXXXXXXXXXXXXXXXX'
                }
            }
        }]
    }
    context = {}
    lambda_handler(event, context)


if __name__ == '__main__':
    test()
