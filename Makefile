TARGETPY = $(filter-out iisysgen.py, $(wildcard *.py))
TARGETS = $(TARGETPY:.py=)

all:	$(TARGETS:=.built)

# First, create an environment which can run debootstrap
bootstrap.built:

# Second, use that to run debootstrap stage1, saving result filetree
stage1.tar.xz:	bootstrap.built build-stage1 make-stage1
	./build-stage1

# Now, run debootstrap second stage under qemu
base.built:	base/stage1.tar.xz

base/stage1.tar.xz:	stage1.tar.xz
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
