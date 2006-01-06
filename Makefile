CHECKER=pychecker

README=README
INDEX_HTML=$(HOME)/www/projects/psync/index.html
RUNNING_txt=RUNNING.txt
RUNNING_HTML=$(HOME)/www/projects/psync/running.html
# HTML_DUMP=lynx -dump
HTML_DUMP=links -dump

VERSION=$(shell ./getVersion.py)
TARGZ=dist/psync-$(VERSION).tar.gz
DEB=../psync_$(VERSION)-1_all.deb
RPM_DIR=$(HOME)/src/system/kernel/rpm
RPM_TGZ=$(RPM_DIR)/SOURCES/psync-$(VERSION).tar.gz
RPM_RH=$(RPM_DIR)/RPMS/noarch/psync-$(VERSION)-1.noarch.rpm
RPM_MDK=$(RPM_DIR)/RPMS/noarch/psync-$(VERSION)-1mdk.noarch.rpm
RPM_SUSE=$(RPM_DIR)/RPMS/noarch/psync-$(VERSION)-1suse.noarch.rpm

TARGETS=$(README) $(RUNNING_txt)

instdir=$(install_dir)/usr

all: $(TARGETS)

$(README): $(INDEX_HTML)
	$(HTML_DUMP) $< > $@

$(RUNNING_txt): $(RUNNING_HTML)
	$(HTML_DUMP) $< > $@

install:
	python2.3 setup.py install --prefix=$(instdir)

clean:
	rm -f $(TARGETS)

test:
	$(CHECKER) -t -v -a --changetypes *.py 2>&1 | less -S

check: test

fullcheck:
	$(CHECKER) -t -9 -v -a -8 --changetypes *.py 2>&1 | less -S

dist: $(TARGZ) mk-packer deb-cp rpm-cp

$(TARGZ):
	./setup.py sdist

mk-packer:
	make -C packer

deb-cp: $(DEB)
	mv $< dist/debian

$(DEB): $(TARGZ)
	fakeroot ./debian/rules binary

rpm-cp: $(RPM_RH) $(RPM_MDK) $(RPM_SUSE)
	mv $^ dist/rpm

$(RPM_TGZ): $(TARGZ)
	cp -v $< $@

$(RPM_RH): $(RPM_TGZ)
	rpm -bb rpm/psync-$(VERSION)-1.spec

$(RPM_MDK): $(RPM_TGZ)
	rpm -bb rpm/psync-$(VERSION)-1mdk.spec

$(RPM_SUSE): $(RPM_TGZ)
	rpm -bb rpm/psync-$(VERSION)-1suse.spec

register:
	./setup.py register

.PHONY: all clean test check fullcheck dist deb-cp rpm-cp
