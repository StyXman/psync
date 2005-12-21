CHECKER=pychecker

README=README.txt
INDEX=$(HOME)/www/projects/psync/index.html

all: $(README)

$(README): $(INDEX)
	lynx -dump $< > $@

test:
	$(CHECKER) -t -v -a --changetypes *.py 2>&1 | less -S

check: test

fullcheck:
	$(CHECKER) -t -9 -v -a -8 --changetypes *.py 2>&1 | less -S

dist:
	./setup.py sdist

.PHONY: test check fullcheck dist
