import PyInstaller.__main__

VERSION = 'beta'

PyInstaller.__main__.run([
    'main.py',
    '--onedir',
    '--windowed',
    '--icon=icon/cool_robot_emoji.ico',
    f'-n job-crawler-{VERSION}'
])
