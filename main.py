from flask import Flask, jsonify, request
import pandas as pd
from demographic_filtering import output
from content_filtering import get_recommendations

articles_data = pd.read_csv('articles.csv')
all_articles = articles_data[['url' , 'title' , 'text' , 'lang' , 'total_events']]
liked_articles = []
not_liked_articles = []

app = Flask(__name__)

def assign_val():
    m_data = {
        "url": all_articles.iloc[0,0],
        "title": all_articles.iloc[0,1],
        "text": all_articles.iloc[0,2] or "N/A",
        "lang": all_articles.iloc[0,3],
        "total_events": all_articles.iloc[0,4]
    }
    return m_data

@app.route("/get-article")
def get_article():

    article_info = assign_val()
    return jsonify({
        "data": article_info,
        "status": "success"
    })

@app.route("/liked-article")
def liked_article():
    global all_articles
    article_info = assign_val()
    liked_articles.append(article_info)
    all_articles.drop([0], inplace=True)
    all_articles = all_articles.reset_index(drop=True)
    return jsonify({
        "status": "success"
    })

@app.route("/unliked-article")
def unliked_article():
    global all_articles
    article_info = assign_val()
    not_liked_articles.append(article_info)
    all_articles.drop([0], inplace=True)
    all_articles = all_articles.reset_index(drop=True)
    return jsonify({
        "status": "success"
    })

# API para retornar os artigos mais populares.
@app.route("/popular-articles")
def popular_articles():
    popular_articles_data=[]
    for index,row in output.iterrows():
        p_articles={
            "url":row["url"],
            "title":row["title"],
            "text":row["text"] or "N/A",
            "lang":row["lang"],
            "total_events":row["total_events"],
            }
        popular_articles_data.append(p_articles)
    return jsonify({
        "data":popular_articles_data,
        "status":"success",
    }),200 
    
    #return "Os 20 principais artigos usando o método de filtragem demográfica" 

# API para retornar os 10 principais artigos semelhantes usando o método de filtragem baseado em conteúdo.
@app.route("/recommended-articles")
def recommended_articles():
    global liked_articles
    col_names=['url','title','text','lang','total_events']
    all_recommended=pd.DataFrame(columns=col_names)
    for article in liked_articles:
        output=get_recommendations(article["title"])
        all_recommended=pd.concat([all_recommended,output], axis=0)
    all_recommended.drop_duplicates(subset=["title"], inplace=True)
    recommended_article_data=[]
    for index,row in all_recommended.iterrows():
        r_article={
            "url":row["url"],
            "title":row["title"],
            "text":row["text"] or "N/A",
            "lang":row["lang"],
            "total_events":row["total_events"],
            }
        recommended_article_data.append(r_article)
    return jsonify({
        "data": recommended_article_data,
        "status":"success"
    }),200
    
    #return "Os 10 principais artigos usando o método de filtragem baseado em conteúdo"

if __name__ == "__main__":
    app.run()