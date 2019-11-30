import os
import shutil
import json

TARGET_SOURCE_DIR = os.path.join(os.pardir, 'src')
DEPLOY_DIR = os.curdir
BUILD_FILE_PREFIX = 'lambda'
BUILD_FILE = os.path.join(DEPLOY_DIR, '{}.zip'.format(BUILD_FILE_PREFIX))
CONFIG_FILE = 'config.json'

with open(CONFIG_FILE, 'r') as F:
    CONFIG = json.load(F)


def main():
    if os.path.exists(BUILD_FILE):
        os.remove(BUILD_FILE)

    shutil.make_archive(os.path.join(DEPLOY_DIR, BUILD_FILE_PREFIX), 'zip', root_dir=TARGET_SOURCE_DIR)

    aws_cmd = "aws lambda update-function-code " \
              "--region {r} --function-name {f} --zip-file fileb://{z}".format(r=CONFIG['region'],
                                                                               f=CONFIG['function'],
                                                                               z=BUILD_FILE)
    os.system(aws_cmd)
    os.system("rm {}".format(BUILD_FILE))


if __name__ == '__main__':
    main()
