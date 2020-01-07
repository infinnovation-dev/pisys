TARGETPY = $(filter-out iisysgen.py, $(wildcard *.py))
TARGETS = $(TARGETPY:.py=)

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
	ln $< $@

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
	PYTHONPATH=iisysgen python3 -m iisysgen build -c $*.yaml $*

$(addsuffix /Dockerfile,$(TARGETS)):	%/Dockerfile:	%.yaml

$(addsuffix /Dockerfile,$(TARGETS)):	iisysgen/iisysgen.py

.PRECIOUS:	%/Dockerfile
