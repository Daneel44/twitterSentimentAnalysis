# Testing processing.py

### First you have to have imdb.csv in same folder than processing.py
---

1. Create object model :
```Python
import processing as pc
model=pc.model()
```
2. Training model:

First time using model we need to train it (at the launch of app).
```Python
model.model_training()
```

3. testing 

- without kafka:

We take a review (for exemple : on the imdb website) and preprocess it :
```Python
tweet="(No spoilers here) This movie is fun to watch AND also invokes a lot of anxiety. That combination makes you stay locked-in from beginning to end.It's fun because of the absurdity. There are so many purely absurd, and very accurate, bits that make you laugh - out of humour and out of discomfort. Of course, the performances are perfect. It's pure fun to watch this large cast of movie stars interact.It's anxiety-invoking because... it's true.I liked it :)"
prepared_tweet=model.prepare_tweet(tweet)
```

Then we pass the prepared_tweet to model:
```Python
print(model.model_predict(prepared_tweet))
```

***


## other possibilities :
1. Using kafka :
we can get tweet by using :
```Python
model.get_tweet_from_kafka()
```

2. save tweet + sentiment analysis in database :
```Python
model.send_to_db(tweet)
```

