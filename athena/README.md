# Class
AWS Athenaはカタログ化したS3データなどを簡単に組み合わせて出力できるので大変便利です。
ただし、ブラウザからではなく、スクリプトの中で使おうとするといろいろと面倒な作業があるので、
そのような作業をClassを作成し、まとめました。

AWS Lambda Layerで使う場合、pythonディレクトリをzipしてアップロードします。

現在は下記のClassがあります
- SingleResult: VIEWの作成や、TABLE/VIEWのデータダウンロードを行います。内部にDataFrameとして結果を保持します。一度に保持できる結果は1つのみです

## SingleResult
インスタンスを作成する際に下記の情報が必要です
- データベースのリージョン
- カタログで設定したデータベース名
- 一次結果ファイルを保存するS3のバケツ
- 一次結果ファイルを保存するS3のプレフィックス
```python
from Athena import SingleResult

DATABASE_REGION = '<aws region>'
DATABASE_NAME = '<database name in glue>'
ATHENA_BUCKET = '<bucket to store athena result / log>'
ATHENA_BUCKET_PREFIX = 'prefix to store athena result / log'

atn = SingleResult(DATABASE_REGION, DATABASE_NAME, ATHENA_BUCKET, ATHENA_BUCKET_PREFIX)
```

クエリを読み込みます
```python
f = '<path to sql file>'
query = atn.load_query_file(f)
```

テキストのクエリを引数に取り、作成したVIEWの名前を返します
```python
view = atn.create_view(query)
```

テキストのクエリを引数に取り、DataFrameに結果を格納します。一次結果ファイルを残すかどうか選択できます
```python
df = atn.read_sql('select * from test_view', keep_result=False)
```

クエリをファイルから読み込んでDataFrameに結果を格納します。
```python
f = '<path to sql file>'
df = atn.read_sql_from_file(f, keep_result=False)
```

S3のバケツとキーを指定して、CSV形式で結果を保存できます
```python
atn.save_result(ATHENA_BUCKET, ATHENA_BUCKET_PREFIX + '/view_result.csv')
```

# クエリ

## 日付
### created_iso_dateが本日より１ヵ月以内
```sql
created_iso_date > CURRENT_DATE - interval '1' month
```

### Expiration_Dateが2018年1月1日以降
```sql
Expiration_Date >= CAST('2018-01-01' AS date)
```

## 文字列
### 連結
```sql
string1 || string2
```

### 切り出し
```sql
substr(string, start(note: 1 origin), length)
```

### 大文字小文字
```sql
UPPER(string1)
LOWER(string2)
```

## 代入
### NULLを埋める
2つ以上の引数を取り、一番最初のNULLでない値を返す
```sql
COALESCE(a, b)
```