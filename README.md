# Fluency Friend - A language-learning companion

Social anxiety is hard, and it makes it incredibly hard when you're trying to learn a new language.

But with a bot, users feel free to make mistakes freely and learn from them.

Our bot works on constrained conversation: task-oriented dialogue like Google Assistant or Alexa devices. In the future, we'd love to expand to more conversational dialogue.

For now, we use DialogFlow and Heroku as a webhook to create conversation with the bot. If the user provides a request in English, the bot tells how to say that response in Spanish. If they make the grammatically correct request in Spanish, the app will perform the action. If the request is an ungrammatical Spanish utterance, the bot lets the user know the correct way to make the request. The user then tries again in Spanish. 
