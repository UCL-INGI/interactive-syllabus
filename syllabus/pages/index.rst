Voici la table des matières du syllabus de java pour SINF0000.
{% for chapter in structure.keys() %}

- {{ chapter }}
{% for page in structure[chapter] %}
  - {{ hyperlink(page, "/%s/%s" % (chapter, page))|safe }}
{% endfor %}
{% endfor %}

.. table-of-contents::