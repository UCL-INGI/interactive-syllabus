from distutils.core import setup

setup(
    name='interactive_syllabus',
    version='0.1.0',
    packages=['syllabus', 'syllabus.utils'],
    url='',
    license='AGPL',
    author='Michel François, Dubray Alexandre',
    author_email='',
    scripts= ['syllabus-webapp'],
    install_requires=[
        'pyyaml >= 3.12', 'werkzeug >= 0.11.11', 'pygments >= 2.1.3', 'flask >= 0.12', 'docutils >= 0.13.1', 'lti',
        'flask-sqlalchemy >= 2.3.2', 'sqlalchemy','python3-saml', 'GitPython', 'sphinx', 'sphinxcontrib-websupport'
    ],
    include_package_data=True,
    description='This is an interactive syllabus, that allows to write rST pages, with INGInious exercises inside these pages '
)
