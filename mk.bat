cd src
rgbasm -onova.obj nova.z80
rgblink -t -m../nova.map -n../nova.sym -o../nova.gb nova.obj
rgbfix -p0 -v ../nova.gb
pause