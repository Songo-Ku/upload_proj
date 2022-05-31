Description:

    Api based on DRF with uploading functionalities for 3 tiers plan (basic, premium, eterprise) and format png, jpg. 
    Project contain implemented expire link, custom user with plan field, fields are validating according to project
    Auth: /api-token-auth for obtain-auth-token. 
    Only user with defined one of 3 plans can create uploading and read his list of uploaded files.  
    User can use actions: list, post(create upload and token). 
    Main libraries: Pillow, DRF, Django, Drf.auth, Django environ.

Test:

    80% of current code contains working tests.
    tests requires implementing better practices for working with files and photos

What is not done:
    
    Custom django admin feature require corrections, 
    configuration with docker, 
    run on heroku
    postgres

Installation Prerequisition:

    Python
    Django / Django REST Framework

Setup:

    Clone repository and fill .env file placed in root directory, with variables:
    SECRET_KEY
    DOMAIN_URL 
    DEBUG

This is example of .env file:

    SECRET_KEY='django-insecure-)-a1bb98%ga8k17+s&40r&=%q@l^t=csk7winebcxepzin80b!'
    DEBUG=False
    DOMAIN_URL='http://127.0.0.1:8000/'