#!/bin/sh
test -f SonkwoInstaller.dmg && rm SonkwoInstaller.dmg
~/projects/yoursway-create-dmg/create-dmg \
--volname "CE-Asia Sonkwo" \
--background sonkwo/installbg.jpg \
--window-pos 400 320 \
--window-size 661 470 \
--icon-size 100 \
--icon Sonkwo.app 156 229 \
--hide-extension Sonkwo.app \
--app-drop-link 495 229 \
--eula sonkwo/eula.txt \
SonkwoInstaller.dmg \
~/projects/sonkwodist
