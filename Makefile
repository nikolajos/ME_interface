EVENTRWDIR = $(shell pwd)
PROCDIR = ..

all: SubProcesses

SubProcesses: patch model
	cd $(PROCDIR)/SubProcesses
	for dir in */; do cd $dir; make matrix2py.so; cd ..; done
	cd $(EVENTRWDIR)

model: patch
	cd $(PROCDIR)/Source && $(MAKE) ../lib/libmodel.a

patch: lha_read.f.patch
	patch $(PROCDIR)/Source/MODEL/lha_read.f lha_read.f.patch

clean:
	cd $(PROCDIR)/SubProcesses
	for dir in */; do cd $dir; make clean; cd ..; done
	cd $(EVENTRWDIR)
