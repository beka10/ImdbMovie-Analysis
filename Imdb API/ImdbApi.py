
'''
Author: Beka Beriashvili


'''

def main():
    import ssl
    import urllib.request
    from bs4 import BeautifulSoup as bto
    import json
    import csv
    import pandas as pd


    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE


    # Read the HTML from the URL and pass on to BeautifulSoup
    url = ['https://www.imdb.com/list/ls003073623/']


    # In this part I used beautiful soup and parsed html file. I found movie ids by tag values and created an 
    # empty list in which I kept all Movie Id values
    Movie_Id = []
    for i in range(0, len(url)):
        uh= urllib.request.urlopen(url[i], context=ctx)
        html =uh.read().decode()
        print("Reading done. Total {} characters read.".format(len(html)))
        soup = bto(html, 'html.parser')
        movies=[]
        for tag in soup.find_all('img'):    # 'img' was the tag name for Ids
            movies.append(tag.get('data-tconst'))
        Movie_Id.append(movies)

    # I had nested lists in a list and I decided to combine them in one big list
    Movie_Id = [y for x in Movie_Id for y in x]

    # I had none values in the list and decided to remove all of them
    Movie_Id = [x for x in Movie_Id if x != None]


    # Base URL
    urlbase = 'http://www.omdbapi.com/'
    # Empty data dictionary
    text_data = dict()
    # I had url for each movie and parsed it. I created a dictionary in which I collected the whole data
    # about the movies
    for i in range(5):
        movies_html = '?i=' + Movie_Id[i] + '&apikey=b492996f'
        url_to_get = urlbase + movies_html 
        # Read the HTML from the URL and pass on to BeautifulSoup
        try:
            html = urllib.request.urlopen(url_to_get, context=ctx).read()
        except:
            print("Could not connect to {}".format(url_to_get))
        soup = bto(html, 'html.parser')
        txt = soup.get_text()
        text_data[Movie_Id[i]] = txt

    # I loaded text values in json file 
    def convert_to_dict(text_data, idx):
        s = text_data[idx]
        json_acceptable_string = s.replace("'", "\"")
        json_acceptable_string = s.replace("' ", ",")
        d = json.loads(json_acceptable_string)
        return d

    # Here I created a list of values where I have all the information about movies
    dict_list = []
    for i in range(5):
        idx = Movie_Id[i]
        val = convert_to_dict(text_data, idx)
        dict_list.append(val)

    # I wanted to calculate inflation rate. I had a column called released date where the values were 
    # like "24 Apr 2010" but for inflation website I had to use values this way "201004". 2010 would be year
    # and 04 would be April and this dictionary will help me to convert months into numbers.
    months = {"Jan": "01", "Feb": "02", "Mar": "03",
              "Apr": "04", "May": "05", "Jun": "06",
              "Jul": "07", "Aug": "08", "Sep": "09",
              "Oct": "10", "Nov": "11", "Dec": "12"}


        
    



    # All rows in released column had same structure. I took out year and month for
    # each movie
    dates_list = []
    for dictionary in dict_list:
        releasedMovie = dictionary["Released"]
        if releasedMovie != "N/A":
            released1 = releasedMovie[3:]
            date_val = months[released1[:3]]
            year_val = released1[4:]
            dates_list.append(date_val + " " + year_val)
        else:
            movie_1 = releasedMovie.replace(releasedMovie, "27 Apr 1925")
            movie_2 = movie_1[3:]
            movie_3 = months[movie_2[:3]]
            movie_4 = movie_2[4:]
            dates_list.append(movie_3 + " " + movie_4)

    


    # Here I made full url for inflation rate for each movie by its released month and year. 
    # Also I parsed the data and got the value called "Answer" where I had the calculated value for inflation
    urlbase1 = 'https://data.bls.gov/cgi-bin/cpicalc.pl?cost1=1.00&year1='
    list1 = []
    for i in range(5):
        cpi_inflation = urlbase1 + dates_list[i][3:] + dates_list[i][:2] + '&year2=201808'
        uh1 = urllib.request.urlopen(cpi_inflation, context=ctx)
        html1 = uh1.read().decode()
        soup1 = bto(html1, 'html.parser')
        cpi = []
        for tag in soup1.find_all('span'):
            cpi.append(tag.get_text())
            list1.append(float(cpi[0][1:]))

    
    # I calculated inflation rate for each movie and multiplied by boxoffice value. 
    # In this list I calculated Adjusted box office value for each movie.
    idx = 0
    cpi_box = []
    print(dict_list)
    for dictionary in dict_list:
        try:
            box_office = dictionary["BoxOffice"]
        except Exception:
            pass
        if box_office != "N/A":
            box_office = float(box_office[1:].replace(',', ''))
            box_office *= float(list1[idx])
            cpi_box.append(box_office)
            idx += 1

    print(cpi_box)
    # Creating csv file
    writer = csv.writer(open("Imdb_Movie.csv", 'w'))
    # Creating columns and rows for csv value
    csv_header = []
    csv_values = []

    # I was converting values and rows from the list into a csv file
    count = 0
    for dictionary in dict_list:
        lst = []
        count += 1
        for key in dictionary.keys():
            if count == 1:
                csv_header.append(key)
            lst.append(dictionary[key])
            csv_values.append(lst)

    # Created adjusted box office for values inflation * box office values
    csv_header.append("Adjusted Box Office")
    # print(csv_header)

    writer.writerow(csv_header)

    # remove duplicates from the list
    csv_values1 = []
    for row in csv_values:
        if row not in csv_values1:
            csv_values1.append(row)



    csv_values2 = []
    new_idx = 0
    # cpi_box
    # Some movies had unkown values for box office column. If I had a value for box office, I created 
    # a new column called " Adjusted Box Office" and put the box office value multiplied by
    # inflation rate. If I did not have a value for box office I kept the Value "N/A"

    for row in csv_values1:
        temp = row
        if row[-4] != "N/A":
            try:
                temp.append(cpi_box[new_idx])
            except Exception:
                pass
            new_idx += 1
        else:
            temp.append("0")
        csv_values2.append(temp)
    # To write all the values into csv file
    for row in csv_values2:
        writer.writerow(row)
    print("Creating CSV file is done.")    

if __name__=='__main__':
    main()    

