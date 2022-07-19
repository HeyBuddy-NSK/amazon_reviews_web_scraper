import requests
from bs4 import BeautifulSoup
import pandas as pd
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
from fake_useragent import UserAgent
import time
# getting useragents for browser headers
ua = UserAgent(cache=False)
agents = ua.chrome

app = Flask(__name__)

@app.route('/',methods=['GET'])
@cross_origin()
def search_product():
    return render_template('index.html')
    
    
@app.route('/reviews',methods=['GET','POST'])
@cross_origin()
def reviews():
    if request.method == 'POST':
        try:
            
            # user product input
            query = request.form['search'].replace(" ","")
            
            
            # print(query)
            # print("welcome to the query search")
            
            ## url for searching
            url = f"https://www.amazon.in/s?k={query}"
            
            # Creating headers for faking browser visit
            payload={}
            headers = { 'User-Agent':agents,
            'Accept-Language':'en-US,en;q=0.9',
            }
            
            # requesting from amazon or url
            response = requests.request("GET", url, headers=headers, data=payload)
            
            # checking if successfully get request
            print("response code :: ",response.status_code)
            
            ## Beautify the raw text obtained from url
            amazon_soup = BeautifulSoup(response.text,features='lxml')
            
            # Getting product data
            raw_product_names = amazon_soup.find_all("a", "a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal")
            raw_product_reviews = amazon_soup.find_all("a", "a-popover-trigger a-declarative")
            rating_count = amazon_soup.find_all("span","a-size-base s-underline-text")
            
            # extracting or beautifying the product data
            product_names = [x.text for x in raw_product_names]
            product_ratings = [x.text if x else 0 for x in raw_product_reviews]
            product_links = ["https://www.amazon.in"+x['href'] for x in raw_product_names]
            product_rating_ct = [x.text if x else 0 for x in rating_count]
            
            ## Extracting data for 1 product
            one_product_name = product_names[2]
            product_rating = product_ratings[2]
            rating_ct = product_rating_ct[2]
            one_product_link = product_links[2]
            
            ## getting page of one product
            one = requests.request("GET", one_product_link, headers=headers, data=payload)
            print('one product response status :: ',one.status_code)
            
            ## making soup for one product
            product_soup = BeautifulSoup(one.text,features='lxml')
            
            ## Getting price of that product
            product_price = product_soup.find('span','a-price-whole').text
            
            ## Getting delivery time of product
            delivery_time = product_soup.find('span',attrs={"data-csa-c-mir-type": "DELIVERY"}).text
            delivery_time = delivery_time.split('.')[0].strip()
            
            # Getting top reviews from india
            reviews = product_soup.find('div',attrs={'id':'cm-cr-dp-review-list'})
            
            ## Getting customer names
            customer_names=[]
            for name in reviews.find_all('span',attrs={'class':"a-profile-name"}):
                if name.text in customer_names:
                    continue
                else:
                    customer_names.append(name.text)
            
            ## Getting review titles and links
            review_titles = []
            review_links = []
            for title in reviews.find_all('a',attrs={"data-hook":"review-title"}):
                link = "https://www.amazon.in"+title['href']
                review_links.append(link)
                review_titles.append(title.text.strip())
                
            ## Getting ratings of review
            rating_stars = []
            for stars in reviews.find_all('i',attrs={"data-hook":"review-star-rating"}):
                rating_stars.append(stars.text)
            
            ## Extracting review body
            review_data = []
            for d in reviews.find_all('span',attrs={"data-hook":"review-body"}):
                r_text = d.text.strip()
                r_text = r_text.split('\n')[0]
                review_data.append(r_text)
            
            all_reviews = []
            for i in range(len(review_data)):
                review_dict = {"SearchedString":query,"productName":one_product_name,"customerName":customer_names[i],"ratings":rating_stars[i],"reviewTitle":review_titles[i], "data":review_data[i], "link":review_links[i]}
                all_reviews.append(review_dict)                         
                
            # print(all_reviews)
            return render_template('reviews.html',reviews=all_reviews[0:(len(all_reviews)-1)])
        except Exception as e:
            print(e)
            return "something is wrong"
            
              
    # return render_template('reviews.html')

if __name__=="__main__":
    app.run(host='127.0.0.1',port=9000, debug=True)
