AWS LambdaにCLIを使ってスクリプトをデプロイするためのスクリプト。

ディレクトリの構成は以下
```bash
$ tree /F
sample_function
├─deploy
│      config.json  : デプロイ先に関する情報を保持するファイル
│      update.py    : src以下にあるファイルをアップデートするための実行ファイル
│
└─src               : スクリプトを保管するディレクトリ
        lambda_function.py
```
