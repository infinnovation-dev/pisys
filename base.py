def build(g, cfg):
    g.from_tarball('prebase.tar.xz')
    # debootstrap does not need to (and cannot in docker) mount /proc
    g.run('mv /bin/mount /bin/mount.orig')
    g.copy_file('fakemount','/bin/mount', mode='755')
    # Now run the second stage of debootstrap to install packages properly
    # (somewhat slow as all executables are run via qemu-arm-static)
    g.run(['/debootstrap/debootstrap','--second-stage'])
    # Unpatch the mount command
    g.run('mv /bin/mount.orig /bin/mount')
    g.finish()
