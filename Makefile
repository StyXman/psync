CHECKER=pychecker

README=README
INDEX_HTML=$(HOME)/www/projects/psync/index.html
RUNNING_txt=RUNNING.txt
RUNNING_HTML=$(HOME)/www/projects/psync/running.html
# HTML_DUMP=lynx -dump
HTML_DUMP=links -dump

TARGETS=$(README) $(RUNNING_txt)

all: $(TARGETS)

$(README): $(INDEX_HTML)
	$(HTML_DUMP) $< > $@

$(RUNNING_txt): $(RUNNING_HTML)
	$(HTML_DUMP) $< > $@

clean:
	rm -f $(TARGETS)

test:
	$(CHECKER) -t -v -a --changetypes *.py 2>&1 | less -S

check: test

fullcheck:
	$(CHECKER) -t -9 -v -a -8 --changetypes *.py 2>&1 | less -S

dist:
	./setup.py sdist

.PHONY: all clean test check fullcheck dist
