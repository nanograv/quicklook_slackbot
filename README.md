# NANOGrav "QuickLook" Slackbot

Instructions for setting up the slackbot:

1. Set environment variables for (case sensitive) SLACK_TOKEN (i.e. Bot User OAuth Token) and SIGNING_SECRET. These should be available on api.slack.com for your bot and workspace.
2. (a) Set up a web server with a public facing URL that the bot can listen to for commands and reactions to plots.
(b) Use this URL as the "Request URL" on the "Event Subscriptions" page of api.slack.com for your bot. At the end of the URL, add '/slack/events'. This is the endpoint that the bot uses to listen for events.
(c) Slack will send a `challenge` parameter to this URL to ensure it is working. Once it is verified, click "Save changes" in bottom right, and your bot should be able to listen to events in that workspace.
3. The Flask app is setup to listen to port http://127.0.0.1:5000/ by default. Change if needed, and make sure your web server points to correct local port.
4. To set up slash commands for the bot:
(a) Go to "Slash commands" on api.slack.com and create command (and corresponding code in bot) if none exist.
(b) For existing slash commands, click edit, and update the "Request URL" to point to the web server URL. Append the URL with the name of the command as used in the code so that the Flask app can recognize it and execute properly.
