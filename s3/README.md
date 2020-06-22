
## JSON ファイルのロード
```python
import json
import boto3

BUCKET = '<bucket name>'
FILE_KEY = '<prefix>/<file name>.json'
OBJ = boto3.resource('s3').Object(BUCKET, FILE_KEY)
CONF = json.loads(OBJ.get()['Body'].read().decode('utf8'))
```
