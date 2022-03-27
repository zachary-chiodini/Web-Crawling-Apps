import PyInstaller.__main__

PyInstaller.__main__.run([
    'job-crawler.py',
    '--onefile',
    '--windowed',
    '--icon=icon/cool_robot_emoji.ico'
])
