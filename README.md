# Eve Canary
This web-application allows to find a killmail information in the systems nearby the player.
You can specify the number of jumps you want to search and go through and you also can specify how far (in hours) you want to check the info.

### APIs used:
Eve API:
https://github.com/Kyria/EsiPy   
ZkillBoard API:
https://github.com/zKillboard/RedisQ    
Template webapp:
https://github.com/Kyria/flask-esipy-example

### Dependencies:
Specified in requirements.txt

### Setup:   

`export FLASK_APP=app.py`

`flask db upgrade`

`flask run`
