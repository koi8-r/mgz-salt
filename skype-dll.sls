{% if grains['cpuarch'] == 'AMD64' %}
    {% set PROGRAM_FILES = "c:/Program Files (x86)" %}
{% else %}
    {% set PROGRAM_FILES = "c:/Program Files" %}
{% endif %}


dll:
    file.recurse:
        - name: "{{ PROGRAM_FILES }}/Skype/Phone/"
        - source: salt://files/skype/dll/

