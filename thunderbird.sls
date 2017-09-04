{% if grains['cpuarch'] == 'AMD64' %}
    {% set PROGRAM_FILES = "c:/Program Files (x86)" %}
{% else %}
    {% set PROGRAM_FILES = "c:/Program Files" %}
{% endif %}

thunderbird-installed:
    pkg.installed:
        - name: thunderbird_x86
        - refresh: True
        - version: '52.3.0'

thunderbird-prefs:
    file.managed:
        - name: "{{ PROGRAM_FILES }}/Mozilla Thunderbird/defaults/pref/prefs.js"
        - source: salt://appcfg/mozilla/defaults/pref/prefs.js
        - require: [thunderbird-installed]

thunderbird-cfg:
    file.managed:
        - name: "{{ PROGRAM_FILES }}/Mozilla Thunderbird/mozilla.cfg"
        - source: salt://appcfg/mozilla/mozilla.cfg
        - require: [thunderbird-prefs]

