{% if grains['cpuarch'] == 'AMD64' %}
    {% set PROGRAM_FILES = "c:/Program Files (x86)" %}
{% else %}
    {% set PROGRAM_FILES = "c:/Program Files" %}
{% endif %}


firefox-installed:
    pkg.installed:
        - name: firefox_x86
        - refresh: True
        - version: '55.0.3'


firefox-prefs:
    file.managed:
        - name: "{{ PROGRAM_FILES }}/Mozilla Firefox/defaults/pref/prefs.js"
        - source: salt://appcfg/mozilla/defaults/pref/prefs.js
        - require: [firefox-installed]

firefox-cfg:
    file.managed:
        - name: "{{ PROGRAM_FILES }}/Mozilla Firefox/mozilla.cfg"
        - source: salt://appcfg/mozilla/mozilla.cfg
        - require: [firefox-prefs]

