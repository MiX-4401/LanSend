pyinstaller --onefile --distpath=./Installer/ --name=lansend cli.py
pyinstaller --onefile --distpath=./Installer/ --name=service receiver.py
rm ./*.spec
rm -R ./build
