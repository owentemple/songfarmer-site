# import libraries
import urllib2
from bs4 import BeautifulSoup

import csv
from datetime import datetime

quote_page = ['http://www.toptenbooks.net/the-list-of-books-view',
              'http://www.toptenbooks.net/the-list-of-books-view?page=1',
              'http://www.toptenbooks.net/the-list-of-books-view?page=2',
              'http://www.toptenbooks.net/the-list-of-books-view?page=3',
              'http://www.toptenbooks.net/the-list-of-books-view?page=4',
              'http://www.toptenbooks.net/the-list-of-books-view?page=5',
              'http://www.toptenbooks.net/the-list-of-books-view?page=6',
              'http://www.toptenbooks.net/the-list-of-books-view?page=7',
              'http://www.toptenbooks.net/the-list-of-books-view?page=8',
              'http://www.toptenbooks.net/the-list-of-books-view?page=9',
              'http://www.toptenbooks.net/the-list-of-books-view?page=10',
              'http://www.toptenbooks.net/the-list-of-books-view?page=11',
              'http://www.toptenbooks.net/the-list-of-books-view?page=12',
              'http://www.toptenbooks.net/the-list-of-books-view?page=13']


# for loop
data = []
for pg in quote_page:
  # query the website and return the html to the variable 'page'
  page = urllib2.urlopen(pg)
  # parse the html using beautiful soap and store in variable `soup`
  soup = BeautifulSoup(page, 'html.parser')
  # Take out the <div> of name and get its value
  name_box_list = soup.find_all('div', attrs={'class': 'field-content top-ten-book-item'})
  for item in name_box_list:
    if item is not None:
      name = item.text.strip()
      name = name.encode('utf-8').decode('ascii', 'ignore')
      score_box = name.split('Total Points: ')
      name = score_box[0]
      votes_box = score_box.split('(')
      votes = votes_box[1:]
      score = votes_box[0]
    else:
      name = "None"
  # get the index price
  #  price_box = soup.find('div', attrs={'class':'price'})
  #  price = price_box.text
  # save the data in tuple
    data.append((name, score, votes))





# open a csv file with append, so old data will not be erased
with open('index.csv', 'a') as csv_file:
  writer = csv.writer(csv_file)
  # The for loop
  for name in data:
    writer.writerow([name, datetime.now()])