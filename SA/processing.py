import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from sklearn import preprocessing
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import svm
import mysql.connector
from kafka import KafkaConsumer
import json

class model:
  
  
  def __init__(self):
    self._model=self.create_model()
    self.model_training()
    
  
  
  def get_tweet_from_kafka(self):
    topic_name = 'YOUR KAFKA TOPIC"'

    consumer = KafkaConsumer(
        topic_name,
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='latest',
        enable_auto_commit=True,
        auto_commit_interval_ms =  5000,
        fetch_max_bytes = 128,
        max_poll_records = 100,

        value_deserializer=lambda x: json.loads(x.decode('utf-8')))

    for message in consumer:
      tweets = json.loads(json.dumps(message.value))
    print(tweets)
    return(tweets)



  #####create model
  def create_model(self):
    clf = svm.LinearSVC(C=0.1)
    return(clf)


  #####return only sigificant words from a sentence
  def tokenizing(self,sentence):
    punc = '''!()-[]{};:'"\, <>./?@#$%^&*_~`'''
    tokens = nltk.word_tokenize(sentence)
    stop_words = set(stopwords.words('english'))
    tokens_l = [w.lower() for w in tokens]
    token_final=[]
    for item in tokens_l : 
      item= item.strip(punc)
      if item not in stop_words and item !="":
       token_final.append(item)
    text = nltk.Text(tokens)
    final_text=""
    for wd in token_final:
      final_text=final_text+wd+" " 
    return [final_text, token_final]


  #######preprocessing imdb database and fit model to be launch at start###################""
  def model_training(self):
    all=pd.read_csv("imdb.csv",encoding='unicode_escape')
    all=all.loc[all['label']!="unsup"]

    X_test=(all.loc[all['type']=='test']).loc[:,['review']]
    y_test=(all.loc[all['type']=='test']).loc[:,['label']]

    X_train=(all.loc[all['type']=='train']).loc[:,['review']]
    y_train=(all.loc[all['type']=='train']).loc[:,['label']]

    test_reviews=X_test.to_dict()
    train_reviews=X_train.to_dict()

    actual_test_text=dict()
    for x in test_reviews['review']:
      actual_review=test_reviews['review'][x]
      txt=self.tokenizing(actual_review)[0]
      actual_test_text[x]=txt

    actual_train_text=dict()
    for x in train_reviews['review']:
      actual_review=train_reviews['review'][x]
      txt=self.tokenizing(actual_review)[0]
      actual_train_text[x]=txt

    le = preprocessing.LabelEncoder()
    le.fit(y_test["label"])
    y_test=le.transform(y_test["label"])

    le.fit(y_train["label"])
    y_train=le.transform(y_train["label"])
    
    df_test_text=pd.DataFrame.from_dict(actual_test_text, orient="index", columns=["review"])
    df_train_text=pd.DataFrame.from_dict(actual_train_text, orient="index", columns=["review"])

    vectorizer = TfidfVectorizer(max_features=6000,
                                  min_df = 5,
                                  max_df = 0.8,
                                  sublinear_tf = True,
                                  use_idf = True)
    self._vectorizer = vectorizer
    x_train_vectors = vectorizer.fit_transform(df_train_text['review']).toarray()
    x_test_vectors = vectorizer.transform(df_test_text['review']).toarray()
    self._model.fit(x_train_vectors, y_train)
  
  
  
  
  #####define if a sentence is positive or negative (89%)######
  def model_predict(self,prepared_tweet):
    result=self._model.predict(prepared_tweet)
    if result[0]== 0:
      sentiment="negative"
    else:
      sentiment="positive"
    return(sentiment)
  
  
  
  
  def prepare_tweet(self,tweet):
    tok =self.tokenizing(tweet)[0]
    prepared_tweet=self._vectorizer.transform([tok]).toarray()
    return (prepared_tweet)



  ###send tweet + sentiment_analysis to database
  def send_to_db(self,tweet):
    prepared_tweet=self.prepare_tweet(tweet)
    sentiment=self.model_predict(prepared_tweet)
    
    cnx = mysql.connector.connect(user='root', database='sentiment_analysis')
    cursor = cnx.cursor()
    add_tweet = ("INSERT INTO analysed_tweet "
                  "(tweet, sentiment)"
                  "VALUES (%s, %s)")
    
    
    cursor.execute(add_tweet, [tweet,sentiment])
    cnx.commit()
    cursor.close()
    cnx.close()
    return(True)
