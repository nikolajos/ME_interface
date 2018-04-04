EVENTRWDIR = $(shell pwd)
MGOUTPUT = ..


APPLIED = $(shell patch -d $(MGOUTPUT)/Source/MODEL --dry-run -Rf lha_read.f lha_read.f.patch >/dev/null 2>&1 && echo APPLIED)
ifeq ($(APPLIED),APPLIED)
$(info Not applying patch.)
PATCH =
else
$(info Applying patch.)
PATCH = patch
endif

SUBDIRS := $(wildcard $(MGOUTPUT)/SubProcesses/*/.)

all: $(SUBDIRS) ident_card.dat index

ident_card.dat:
	cp $(MGOUTPUT)/Cards/ident_card.dat $(EVENTRWDIR)/

$(SUBDIRS): $(MGOUTPUT)/lib/libmodel.a
	$(MAKE) -C $@ matrix2py.so

index:
	python extract_process.py -i $(MGOUTPUT)/SubProcesses

$(MGOUTPUT)/lib/libmodel.a: $(PATCH)
	$(MAKE) -C $(MGOUTPUT)/Source ../lib/libmodel.a

patch:
	cp $(EVENTRWDIR)/lha_read.f.patch $(MGOUTPUT)/Source/MODEL/
	patch -d $(MGOUTPUT)/Source/MODEL -Nsb lha_read.f lha_read.f.patch


clean:
	rm -f $(MGOUTPUT)/lib/libmodel.a
	for dir in $(SUBDIRS); do rm -f $$dir/matrix2py.so; done
