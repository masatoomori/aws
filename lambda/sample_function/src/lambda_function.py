def lambda_handler(event, context):
    'sample script'


def test():
    event = {
        # 'region': 'us-west-2'
        'region': 'local',
        'source': 'test'
    }
    context = {}
    lambda_handler(event, context)


if __name__ == '__main__':
    test()
