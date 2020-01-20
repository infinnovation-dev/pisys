#!/usr/bin/python3
#=======================================================================
"""
Build base for other Raspberry Pi systems
"""
#=======================================================================

def build(g, cfg):
    user = cfg.get('user',{})
    username = user.get('name','pi')
    userpass = user.get('password','raspberry')
    hostname = cfg.get('hostname','raspberrypi')
    rootdev = '/dev/mmcblk0p2'

    g.from_named('pisys-stage0')

    g.install('raspi-copies-and-fills',
              'fbset',
              'console-setup')
    g.install('keyboard-configuration',
              'debconf-utils',
              'dosfstools',  # fsck.vfat
              'fake-hwclock', #But not for signage (read-only root):
              'apt-transport-https',
              # For the build process:
              'patch',
              )
    # boot-files
    g.write_lines('/boot/cmdline.txt',
                  'dwc_otg.lpm_enable=0 '
                  'console=serial0,115200 console=tty1 '
                  'root=ROOTDEV rootfstype=ext4 '
                  'elevator=deadline fsck.repair=yes rootwait')
    g.copy_file('config.txt', '/boot/config.txt')
    # sys-tweaks
    #d.patch('stage1/01-sys-tweaks/00-patches/01-bashrc.diff')
    g.copy_as_helper('bashrc.sed')
    g.run('sed -f /helpers/bashrc.sed -i /etc/skel/.bashrc')
    g.mkdir('/etc/systemd/system/getty@tty1.service.d')
    g.write_lines('/etc/systemd/system/getty@tty1.service.d/noclear.conf',
                  '[Service]',
                  'TTYVTDisallocate=no')
    g.write_lines('/etc/fstab',
                  'proc            /proc           proc    defaults          0       0',
                  'BOOTDEV  /boot           vfat    defaults          0       2',
                  'ROOTDEV  /               ext4    defaults,noatime  0       1')

    # users
    g.run(['adduser','--disabled-password','--gecos','', username])
    g.run('echo "%s:%s" | chpasswd' % (username, userpass))
    g.run('echo "root:root" | chpasswd')
    # hostname
    g.write_lines('/var/local/hosts',
                  # Written by netbase.postinst but clobbered by docker
                  '127.0.0.1	localhost',
                  '127.0.1.1	%s' % hostname)
    g.write_lines('/var/local/hostname', hostname)
    # network
    g.write_lines('/etc/modprobe.d/ipv6.conf',
                  "# Don't load ipv6 by default",
                  'alias net-pf-10 off',
                  '#alias ipv6 off')

    g.symlink('/dev/null','/etc/systemd/network/99-default.link')
    g.install('dhcpcd5')
    g.mkdir('/etc/systemd/system/dhcpcd.service.d')
    g.write_lines('/etc/systemd/system/dhcpcd.service.d/wait.conf',
                  '[Service]',
                  'ExecStart=',
                  'ExecStart=/usr/lib/dhcpcd5/dhcpcd -q -w')
    # videocore
    g.install('libraspberrypi-bin',
              'libraspberrypi0')
    # console & keyboard
    g.copy_as_helper('console.dc', 'console.dc')
    g.run('debconf-set-selections',stdin='/helpers/console.dc')
    # groups for hardware (referenced by udev rule from raspberrypi-sys-mods)
    hwgrps = ('spi','i2c','gpio')
    for grp in hwgrps:
        g.run(['groupadd','-f','--system', grp])
    g.run(['usermod','--append','--groups', ','.join(hwgrps), username])
    # system
    g.install('sudo',
              'raspberrypi-sys-mods')
#    # users (bis)
    for grp in ('adm','audio','users','sudo','video','input'):
        g.run(['adduser', username, grp])
    if False:
        swapsize = 100*1024*1024
        g.install('dphys-swapfile')
        g.replace('/etc/dphys-swapfile', r'^#\?CONF_SWAPSIZE=.*',
                  'CONF_SWAPSIZE=%d' % (swapsize//(1024*1024)))
    # Generally useful for system management etc.
    g.install('ssh',
              'less',
              'unzip',
              'rsync')

    g.finish()
