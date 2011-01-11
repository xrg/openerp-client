LANG=fr
PYTHON_FILES=$(shell find bin/ -name "*py")
PYTHONC_FILES=$(shell find -name "*pyc")
APP=openerp-client
LANGS=$(shell for i in `find bin/po -name "*.po"`; do basename $$i | cut -d'.' -f1; done;)

all:

clean:
	rm -f bin/*bak $(PYTHONC_FILES)
	rm -f bin/openerp.gladep

translate_get:
	xgettext -k_ -kN_ \
		--copyright-holder="OpenERP SA." \
		--package-name="OpenERP GTK client" \
		--package-version="6.0.0rc2" \
		--msgid-bugs-address="openerp-expert-localization@lists.launchpad.net" \
		-o bin/po/$(APP).pot \
		$(PYTHON_FILES) bin/openerp.glade bin/win_error.glade

translate_set:
	for i in $(LANGS); do \
		if [ ! -d bin/share/locale/$$i/LC_MESSAGES/ ] ; then \
			mkdir -p bin/share/locale/$$i/LC_MESSAGES/ || exit $? ; \
		fi ;\
		msgfmt bin/po/$$i.po -o bin/share/locale/$$i/LC_MESSAGES/$(APP).mo; \
		done

merge:
	for i in $(LANGS); do msgmerge bin/po/$$i.po bin/po/$(APP).pot -o bin/po/$$i.po --strict; done;

test:
	echo $(LANGS)

