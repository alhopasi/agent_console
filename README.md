## Agent Console
Project for a console type webpage, that will be used in an event, where a game is played.

The game is about wits, secret information and secret identities.

If you are participating and found this by coincidence, please do not look further.

####
Deployment:
```flask --app agent_console run -h 0.0.0.0```

Next steps:
- import secret challenge
  if secret challenge started - show on all player info
  possibility for player to enter the secret code for next challenge for their alliance
- continue developing the application with required features

note to self: gunicorn don't work with flask-socketio - look for alternates or stay with flask development server ?
