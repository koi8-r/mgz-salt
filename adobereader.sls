adobereader-installed:
    pkg.installed:
        - name: adobereader-xi_x86
        - refresh: True
        - version: '11.0.00'

# adobereader-update-service-disabled:
#     service.dead:
#         - name: AdobeARMservice
#         - enable: False
#         - require: [adobereader-installed]

