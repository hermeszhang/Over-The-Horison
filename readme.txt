This program intended to create a 3D flying simulating third person shooting game.
Players will drive a ship in the universe at the low orbit near the earth and fight 
with NPC ships. It's a really fun and intense game.

main file YPFF.PY




Package used - 
python 3.4  (other versions might lead to strange behavior)
	pyglet 1.2.4
	avbin
	openAL

1.pyglet 1.2.4 can be found in Installation folder, simply enter the directory with Terminal


python3 setup.py install


will install pyglet 1.2.4 for your python3
if you have pip you can use terminal command

pip install pyglet

or 

python3 -m pip install pyglet  for microsoft power shell


###
before installing AVbin and openAL,  you might want to try the code and see of exception raised
chances that AVbin and openAL is already installed on your machine, especially for Mac and Linux,
if bug aries, please install required compnents.
###

2.AVbin installation

avbin installation for linux
try:
sudo apt-get install libavbin-dev libavbin0

x64
installation/install-avbin-linux-x86-64-v10
x32 
installation/install-avbin-linux-x86-32-v10

avbin installation for Mac OSX
installation/AVbin10.pkg


avbin installation for windows x86
AVbin10-win32.exe
note - this is a x86 installation package, but it is also required for x64 platform, tested on Windows 7
	avbin.dll included in root folder is the runtime library for avbin in x86, if installation failed,
copy this file to %SYSTEMDIR%system32

avbin installation for windows x64
please install both
AVbin10-win32.exe
AVbin10-win64.exe

3.openAL installation

for Windows paltform
run the oalinst.exe in oalinst.zip

on linux and mac
sudo apt-get install libopenal0a libopenal-dev
#from http://stackoverflow.com/questions/3907064/installing-opengl-and-openal-in-ubuntu
