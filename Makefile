LANG=fr
PYTHON_FILES=$(shell find -name "*py")
PYTHONC_FILES=$(shell find -name "*pyc")
LANGS = es fr hu it pt ro ru sv uk zh al cs de

all:

clean:
	rm -f bin/*bak $(PYTHONC_FILES)
	rm -f bin/openerp.gladep

translate_get:
	xgettext -k_ -kN_ -o bin/po/terp-msg.pot $(PYTHON_FILES) bin/openerp.glade

translate_set2:
	msgfmt bin/po/fr.po -o bin/po/fr/LC_MESSAGES/terp.mo

translate_set:
	msgfmt bin/po/es.po -o bin/po/es/LC_MESSAGES/terp.mo
	msgfmt bin/po/fr.po -o bin/po/fr/LC_MESSAGES/terp.mo
	msgfmt bin/po/hu.po -o bin/po/hu/LC_MESSAGES/terp.mo
	msgfmt bin/po/it.po -o bin/po/it/LC_MESSAGES/terp.mo
	msgfmt bin/po/pt.po -o bin/po/pt/LC_MESSAGES/terp.mo
	msgfmt bin/po/ro.po -o bin/po/ro/LC_MESSAGES/terp.mo
	msgfmt bin/po/ru.po -o bin/po/ru/LC_MESSAGES/terp.mo
	msgfmt bin/po/sv.po -o bin/po/sv/LC_MESSAGES/terp.mo
	msgfmt bin/po/uk.po -o bin/po/uk/LC_MESSAGES/terp.mo
	msgfmt bin/po/zh.po -o bin/po/zh/LC_MESSAGES/terp.mo
	msgfmt bin/po/al.po -o bin/po/al/LC_MESSAGES/terp.mo
	msgfmt bin/po/cs.po -o bin/po/cs/LC_MESSAGES/terp.mo
	msgfmt bin/po/de.po -o bin/po/de/LC_MESSAGES/terp.mo

merge:
	msgmerge bin/po/es.po bin/po/terp-msg.pot -o bin/po/es.po --strict
	msgmerge bin/po/fr.po bin/po/terp-msg.pot -o bin/po/fr.po --strict
	msgmerge bin/po/hu.po bin/po/terp-msg.pot -o bin/po/hu.po --strict
	msgmerge bin/po/it.po bin/po/terp-msg.pot -o bin/po/it.po --strict
	msgmerge bin/po/pt.po bin/po/terp-msg.pot -o bin/po/pt.po --strict
	msgmerge bin/po/ro.po bin/po/terp-msg.pot -o bin/po/ro.po --strict
	msgmerge bin/po/ru.po bin/po/terp-msg.pot -o bin/po/ru.po --strict
	msgmerge bin/po/sv.po bin/po/terp-msg.pot -o bin/po/sv.po --strict
	msgmerge bin/po/uk.po bin/po/terp-msg.pot -o bin/po/uk.po --strict
	msgmerge bin/po/zh.po bin/po/terp-msg.pot -o bin/po/zh.po --strict
	msgmerge bin/po/al.po bin/po/terp-msg.pot -o bin/po/al.po --strict
	msgmerge bin/po/cs.po bin/po/terp-msg.pot -o bin/po/cs.po --strict
	msgmerge bin/po/de.po bin/po/terp-msg.pot -o bin/po/de.po --strict
