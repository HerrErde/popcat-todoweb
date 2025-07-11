# Configuration via environment variables

- `MONGODB_HOST` the mongodb host
- `MONGODB_NAME` the mongodb db name
- `MONGODB_USER` the mongodb user
- `MONGODB_PASS` the mongodb password
- `MONGODB_CLUSTER` use when using the mongodb database of cloud.mongodb.com (free plan only one, so "Cluster0")
- `OAUTH2_CLIENT_ID` the id of the web todo list auth client
- `OAUTH2_CLIENT_SECRET` the secret of the web todo list auth client
- `FLASK_SECRET_KEY` a flask secret [https://jwtsecret.com](https://jwtsecret.com/generate)
- `OAUTH2_REDIRECT_URI` the callback url for the web todo list (has to be the same in the discord application)
- `PUBLIC_ALL` There is a error? on the original page, when visiting `https://popcat.xyz/all` you can see all todo list items from any user. Here you can disable it
