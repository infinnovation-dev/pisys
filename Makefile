#=======================================================================
#	Typical usage:
#	  make pwmin.tar.xz
#=======================================================================
IISYSGEN = PYTHONPATH=iisysgen python3 -m iisysgen.cmd

TARGETPY = $(wildcard *.py)
TARGETS = $(TARGETPY:.py=)

ifeq ($(ACNG),localhost)
# Need an external IP address to allow access from within docker
APT_PROXY = http://$(shell hostname -I | sed -e 's/ .*//'):3142
else
ifneq ($(ACNG),)
APT_PROXY = http://$(ACNG):3142
endif
endif

all:	$(TARGETS:=.built)

# First, create an environment which can run debootstrap
bootstrap.built:

# Second, use that to run debootstrap first stage, saving result filetree
prebase.tar.xz:	bootstrap.built build-prebase target-build-prebase
	./build-prebase

# Now, run debootstrap second stage under qemu
base.built:	base/prebase.tar.xz

base/prebase.tar.xz:	prebase.tar.xz
	mkdir -p base
	rm -f $@ && ln $< $@

# Create minimal usable system (pi-gen stage 0)
stage0.built:	base.built \
		raspberrypi.gpg.key locales.dc

# Common starting point for several Raspberry Pi systems
pwmin.built:	stage0.built \
		config.txt bashrc.sed console.dc

# Generic rules
%.tar.xz:	%.built
	docker run \
	    "--env=PISYS_OWNER=$(shell id -u):$(shell id -g)" \
	    -v "$(shell pwd):/host" \
	    pisys-$*:latest \
	    /host/export-tarball \
	      "/host/$@"

%.built:	%/Dockerfile
	docker build -t pisys-$* $*
	touch $@

%/Dockerfile:	%.py
	$(IISYSGEN) generate \
	    $(addprefix -c ,$(wildcard $*.yaml) $(wildcard $*.json)) \
	    -v APT_PROXY=$(APT_PROXY) \
	    $*

# Depend on any configuration files
define cfg_template =
$(1)/Dockerfile:	$(wildcard $(1).yaml) $(wildcard $(1).json)
endef

$(foreach t,$(TARGETS),$(eval $(call cfg_template,$(t))))

$(addsuffix /Dockerfile,$(TARGETS)):	iisysgen/iisysgen/*.py

.PRECIOUS:	%/Dockerfile
