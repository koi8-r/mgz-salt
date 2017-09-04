{% if grains['osfinger'] == 'Windows-XP' %}
    {% set v = '7.36.0.150' %}
{% else %}
    {% set v = '7.36.0.101' %}
{% endif  %}

# ms-vcpp-2015-installed:
#    pkg.installed:
#        - name: ms-vcpp-2015-redist_x86
#        - refresh: True
#        - version: 14.0.24215.1

skype-installed:
    pkg.installed:
        - name: skype_x86
        - refresh: True
        - version: "{{ v }}"

