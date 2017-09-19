EVENTRWDIR = $(shell pwd)
PROCDIR = ..


APPLIED = $(shell patch -d $(PROCDIR)/Source/MODEL --dry-run -Rf lha_read.f lha_read.f.patch >/dev/null 2>&1 && echo APPLIED)
ifeq ($(APPLIED),APPLIED)
$(info Not applying patch.)
PATCH =
else
$(info Applying patch.)
PATCH = patch
endif

SUBDIRS := $(wildcard $(PROCDIR)/SubProcesses/*/.)

all: $(SUBDIRS) ident_card.dat

ident_card.dat:
	cp $(PROCDIR)/Cards/ident_card.dat $(EVENTRWDIR)/

$(SUBDIRS): $(PROCDIR)/lib/libmodel.a
	$(MAKE) -C $@ matrix2py.so

$(PROCDIR)/lib/libmodel.a: $(PATCH)
	$(MAKE) -C $(PROCDIR)/Source ../lib/libmodel.a

patch:
	cp $(EVENTRWDIR)/lha_read.f.patch $(PROCDIR)/Source/MODEL/
	patch -d $(PROCDIR)/Source/MODEL -Nsb lha_read.f lha_read.f.patch


clean:
	rm -f $(PROCDIR)/lib/libmodel.a
	for dir in $(SUBDIRS); do rm -f $$dir/matrix2py.so; done
