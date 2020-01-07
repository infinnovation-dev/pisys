#!/usr/bin/python3
#=======================================================================
"""
Build minimal Raspberry Pi system - equivalent to pi-gen stage0
"""
#=======================================================================

def build(g, cfg):
    g.from_named('pisys-base')

    g.env('DEBIAN_FRONTEND','noninteractive')
    # 00-configure-apt
    ## 00-run.sh
    g.write_lines('/etc/apt/sources.list',
                  'deb http://raspbian.raspberrypi.org/raspbian/ stretch main contrib non-free rpi',
                  "# Uncomment line below then 'apt-get update' to enable 'apt-get source'",
                  '#deb-src http://raspbian.raspberrypi.org/raspbian/ stretch main contrib non-free rpi')
    g.write_lines('/etc/apt/sources.list.d/raspi.list',
                  'deb http://archive.raspberrypi.org/debian/ stretch main ui staging',
                  "# Uncomment line below then 'apt-get update' to enable 'apt-get source'",
                  '#deb-src http://archive.raspberrypi.org/debian/ stretch main ui')
    proxy = cfg.get('APT_PROXY')
    if proxy:
        g.write_lines('/etc/apt/apt.conf.d/51cache',
                      'Acquire::http { Proxy "%s"; };' % proxy)
    else:
        g.run('rm -f /etc/apt/apt.conf.d/51cache')
    g.copy_file('raspberrypi.gpg.key','/helpers/')
    g.run('apt-key add -', stdin='/helpers/raspberrypi.gpg.key')
    g.run('apt-get update')
    g.run('apt-get dist-upgrade -y')

    # 01-locale
    ## 00-debconf
    g.copy_as_helper('locales.dc','locales.dc')
    g.run('debconf-set-selections',stdin='/helpers/locales.dc')
    ## 00-packages
    g.install('locales')

    # 02-firmware
    ## 01-packages
    g.install('raspberrypi-bootloader',
              'raspberrypi-kernel')

    g.finish()
