# hyperSmart
Smart Home controller device with Raspberry Pi and [Pimoroni HyperPixel Weirdly Square](https://shop.pimoroni.com/products/hyperpixel-4-square) Touch display

## Dependencies
* [hyperpixel4](https://github.com/pimoroni/hyperpixel4)
* [pygame](https://www.pygame.org/)
* [pynanosvg](https://github.com/ethanhs/pynanosvg)
  * [cython](https://cython.org/)
  * [nanosvg](https://github.com/memononen/nanosvg/)
* [phue](https://github.com/studioimaginaire/phue)
* [python-miio](https://github.com/rytilahti/python-miio)
** libffi-dev
** libssl-dev

## Notes on Usage
In order to run on Raspbian Lite OS:
* install hyperpixel4 as per instructions on their github page, _not_ the instructions on their shop page as https is now default.
* pygame needs to be installed from the Package manager, verison from pip is _not_ compatible with Raspbian.
* running user needs to be member of the tty and video groups.
* tty files needs 660 access rights, modified via udev rules.
* Perhpas unecessarily but [patched](https://www.raspberrypi.org/forums/viewtopic.php?t=250001) libsdl for tocuhscreens. 
* touchevents was inverted, fixed by modifying /etc/ts.conf with module `invert x0=720 y0=720`.
