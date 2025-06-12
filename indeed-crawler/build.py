import PyInstaller.__main__


PyInstaller.__main__.run([
    'main.py',
    '--onedir',
    '--windowed',
    '--icon=icon/cool_robot_emoji.ico',
    '-n job-crawler-beta'
])
