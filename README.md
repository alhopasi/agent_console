## Agent Console
Project for a console type webpage, that will be used in an event, where a game is played.

The game is about wits, secret information and secret identities.

If you are participating and found this by coincidence, please do not look further.

####
Deployment:

```flask --app agent_console/app run```

Next steps:
- deploy to render
- create user models
- create login/logout system
- continue developing the application with required features
- create path system for users (post "path" info with request)

note to self: gunicorn don't work with flask-socketio - look for alternates or stay with flask development server ?
