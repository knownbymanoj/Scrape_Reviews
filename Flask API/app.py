from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

app = Flask(__name__)

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            amazon_url = "https://www.amazon.it/s?k=" + searchString
            uClient = uReq(amazon_url)
            AmazonPage = uClient.read()
            uClient.close()
            amazon_html = bs(AmazonPage, "html.parser")
            bigboxes = amazon_html.findAll("div", {"class":"sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 sg-col s-widget-spacing-small sg-col-4-of-20"})
            #del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.amazon.it" + box.div.div.h2.a['href']
            prodRes = requests.get(productLink)
            prodRes.encoding='utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            print(prod_html)
            price = prod_html.find_all('span', {'class': 'a-offscreen'})[0].text
            commentboxes = prod_html.find_all('div', {'class':'a-section celwidget'})
            del commentboxes[0]
            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            for commentbox in commentboxes:
                try:
                    #name.encode(encoding='utf-8')
                    name = commentbox.find_all('div',{'class':"a-profile-content"})[0].text

                except:
                    name = 'No Name'

                try:
                    #rating.encode(encoding='utf-8')
                    rating = commentbox.find_all('span', {'class':"a-icon-alt"})[0].text


                except:
                    rating = 'No Rating'

                try:
                    #commentHead.encode(encoding='utf-8')
                    commentHead = bs(commentbox.find_all('div',{'class':"a-expander-content reviewText review-text-content a-expander-partial-collapse-content"})[0].text,'html.parser')

                except:
                    commentHead = 'No Comment Heading'
                try:
                    if bool(len(commentbox.find_all('a', {'class': "a-size-base a-link-normal review-title a-color-base review-title-content a-text-bold"}))):
                        custComment = bs(commentbox.find_all('a', {'class': "a-size-base a-link-normal review-title a-color-base review-title-content a-text-bold"})[
                                                0].text, 'html.parser')
                    else:
                        custComment = commentbox.find_all('span', {'class': "cr-original-review-content"})[0].text

                except Exception as e:
                    print("Exception while creating dictionary: ",e)

                mydict = {"Product": searchString,"Price": price, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                print('**************')
                print(mydict)
                print('**************')
                reviews.append(mydict)
            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')

if __name__ == "__main__":
    #app.run(host='127.0.0.1', port=8001, debug=True)
	app.run(debug=True)
