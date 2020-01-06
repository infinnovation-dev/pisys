#!/usr/bin/python3
import iisysgen

def build(g, cfg):
    g.from_named('debian:stretch-slim')
    g.env('DEBIAN_FRONTEND','noninteractive')
    g.run('apt-get update')
    g.install('debootstrap',
              'qemu-user-static',
              'bsdtar')
    g.install('xz-utils')
#    g.install('fakechroot',
#              'fakeroot')
    g.finish()
