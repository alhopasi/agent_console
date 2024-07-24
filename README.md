## Agent Console
Project for a console type webpage, that will be used in an event, where a game is played.

The game is about wits, secret information and secret identities.

If you are participating and found this by coincidence, please do not look further.

####
Deployment:
```flask --app agent_console run -h 0.0.0.0```

Next steps:
- change output / command language to finnish
- import admin command to change password
- import admin commands to manage database / users  (halfway done)
- import message system and commands
- import task board and way to solve tasks
- import admin commands to manage task board
- continue developing the application with required features

note to self: gunicorn don't work with flask-socketio - look for alternates or stay with flask development server ?
