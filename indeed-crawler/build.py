import PyInstaller.__main__

VERSION = 'beta-1.0'

PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--windowed',
    '--icon=icon/cool_robot_emoji.ico',
    f'-n job-crawler-{VERSION}'
])
