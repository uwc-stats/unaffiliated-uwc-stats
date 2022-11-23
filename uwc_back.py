from flask import flash, Markup
from flask import session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from fuzzywuzzy import fuzz

from iso3166 import countries

import math
import sqlite3

import pandas as pd
import json
import plotly
import plotly.express as px




class UserFilterDavis(FlaskForm):
    name = StringField('Name')
    country = StringField('Country')
    uwc = StringField('UWC')
    school = StringField('Undergraduate')
    year = StringField('Year')
    submit = SubmitField('Filter Data')


    
def construct_filter_query(form):

    filter_query = 'SELECT name, country, uwc, school, year FROM scholars'

    if form.name.data != "" or form.country.data != "" or form.uwc.data != "" or form.school.data != "" or form.year.data != "":
        filter_query = filter_query + " WHERE"

    # Flash header
    if form.name.data != "":
        filter_query = filter_query + " name = " + "\"" + form.name.data + "\""
        flash(f'Filtering out the database for {form.name.data}', 'success')
    if form.country.data != "":
        if form.name.data != "":
            filter_query = filter_query + " AND"
        filter_query = filter_query + " country = " + "\"" + form.country.data + "\""
        flash(f'Filtering out the database for {form.country.data}', 'success')
    if form.uwc.data != "":
        if form.name.data != "" or form.country.data != "":
            filter_query = filter_query + " AND"
        filter_query = filter_query + " uwc = " + "\"" + form.uwc.data + "\""
        flash(f'Filtering out the database for {form.uwc.data}', 'success')
    if form.school.data != "":
        if form.name.data != "" or form.country.data != "" or form.uwc.data != "":
            filter_query = filter_query + " AND"
        filter_query = filter_query + " school = " + "\"" + form.school.data + "\""
        flash(f'Filtering out the database for {form.school.data}', 'success')
    if form.year.data != "":
        if form.name.data != "" or form.country.data != "" or form.uwc.data != "" or form.school.data != "":
            filter_query = filter_query + " AND"
        filter_query = filter_query + " year = " + "\"" + form.year.data + "\""
        flash(f'Filtering out the database for {form.year.data}', 'success')
    
    return filter_query


def construct_count_query(form):
    count_query = "SELECT COUNT(*) FROM scholars"

    if form.country.data != "" or form.uwc.data != "" or form.school.data != "":
        count_query = count_query + " WHERE"
   
    if form.country.data != "":
        count_query = count_query + " country = " + "\"" + form.country.data + "\""
    if form.uwc.data != "":
        if form.country.data != "":
            count_query = count_query + " AND"
        count_query = count_query + " uwc = " + "\"" + form.uwc.data + "\""
    if form.school.data != "":
        if form.country.data != "" or form.uwc.data != "":
            count_query = count_query + " AND"
        count_query = count_query + " school = " + "\"" + form.school.data + "\""

    return count_query


def blur(sql_scholars):
    scholars = []
    for scholar in sql_scholars:
        scholars.append(list(scholar))

    for scholar in scholars:
        blur_name = scholar[0][0]

        name_length = len(scholar[0])
        show = False
        for i in range(name_length-1):
            if scholar[0][i] == " ":
                blur_name = blur_name + " "
                show = True
            elif show == True:
                blur_name = blur_name + scholar[0][i]
                show = False
            else:
                blur_name = blur_name + "*"

        scholar[0] = blur_name
    
    return scholars


def correction_filter(country, uwc, school):
    all_correction = []
    if country != None:
        cut_off = 100
        while cut_off > 0:
            if fuzzywuzzy_check_w_list(country, list_countries, cut_off) != None:
                result = ["country", fuzzywuzzy_check_w_list(country, list_countries, cut_off)]
                all_correction.append(result)
                break

            cut_off = cut_off - 10
    

    if uwc != None:
        cut_off = 100
        while cut_off > 0:
            if fuzzywuzzy_check_w_list(uwc, list_uwc, cut_off) != None:
                result = ["uwc", fuzzywuzzy_check_w_list(uwc, list_uwc, cut_off)]
                all_correction.append(result)
                break

            cut_off = cut_off - 10
        

    if school != None:
        cut_off = 100
        while cut_off > 0:
            if fuzzywuzzy_check_w_list(school, list_school, cut_off) != None:
                result = ["school", fuzzywuzzy_check_w_list(school, list_school, cut_off)]
                all_correction.append(result)
                break

            cut_off = cut_off - 10
        

    return all_correction


def construct_correction_filter_query(filter_query):
    if 'all_correction' in session:
        all_correction = session['all_correction']
        session.pop('all_correction', None)

        add_AND = False
        filter_query = filter_query + " WHERE"

        for correction in all_correction:

            if add_AND == True:
                filter_query = filter_query + " AND"

            key = correction[0]
            value = correction[1]

            filter_query = filter_query + " " + key + " = " + "\"" + value + "\""

            add_AND = True

            flash(f'Filtering out the database for {value}', 'success')
        
        session['filter_query'] = filter_query


# https://www.datacamp.com/tutorial/fuzzy-string-python
def fuzzywuzzy_check_w_list(str2Match, list_x, cut_off):
    for strOption in list_x:

                Ratios = fuzz.ratio(str2Match, strOption)
                Partial_ratio = fuzz.partial_ratio(str2Match, strOption)
                Token_Sort_Ratio = fuzz.token_sort_ratio(str2Match, strOption)
                Token_Set_Ratio = fuzz.token_set_ratio(str2Match, strOption)

                if Ratios > cut_off or Partial_ratio > cut_off or Token_Sort_Ratio > cut_off or Token_Set_Ratio > cut_off:
                    return strOption



def fuzzywuzzy_check_w_string(str2Match, strOption, cut_off):
    Ratios = fuzz.ratio(str2Match, strOption)
    Partial_ratio = fuzz.partial_ratio(str2Match, strOption)
    Token_Sort_Ratio = fuzz.token_sort_ratio(str2Match, strOption)
    Token_Set_Ratio = fuzz.token_set_ratio(str2Match, strOption)

    if Ratios > cut_off or Partial_ratio > cut_off or Token_Sort_Ratio > cut_off or Token_Set_Ratio > cut_off:
        return strOption



# Construct a list of countries from the library
list_countries = []
for country in countries:
    list_countries.append(country[0])

# Alternative country name
list_countries_alt = [
    ("USA", "United States"),
    ("Vietnam", "Viet Nam"),
    ("Chechnya", "Russian Federation"),
    ("South Korea", "Korea Republic of"),
    ("Korea", "Korea Republic of"),
    ("Laos", "The Lao People's Democratic"),
    ("Venezuela", "The Bolivarian Republic of Venezuela")
]

# Previous country name
list_previous_countries = [
    ("Swaziland", "Eswatini"),
    ("Cape Verde", "The epublic of Cabo Verde")
]

# Hard code country naame
list_countries.append("Tibet")


# List of all UWC keyword
list_uwc = [
    "UWC Atlantic",
    "Pearson",
    "South East Asia",
    "Waterford Kamhlaba Southern Africa",
    "USA",
    "Adriatic",
    "Li Po Chun",
    "Red Cross Nordic",
    "Mahindra",
    "Costa Rica",
    "Mostar",
    "Maastricht",
    "Robert Bosch",
    "Dilijan",
    "Changshu China",
    "Thailand",
    "ISAK Japan",
    "East Africa",
    "Simon Bolivar UWC of Agriculture"
]
list_uwc.sort()



# List of all School
list_school = []

# Alternative school name
list_school_alt = [
    ("Massachusetts Institute of Technology", "MIT"),
    ("St. Johnâ€™s College", "St. John's College"),
    ("Harvard College", "Harvard University"),
    ("Wesleyan College", "Wesleyan University"),
    ("St. Lawrence College", "St. Lawrence University")
]

# with open('davis_scholar_database.csv', 'r') as csv_file:
#     csv_reader = csv.DictReader(csv_file)

#     for line in csv_reader:
#         school = line['School']

#         # School already exist in the school list
#         if fuzzywuzzy_check_w_list(school, list_school, 90) != None:
#             # print(school + "---->" + fuzzywuzzy_check_w_list(school, list_school, 90))
#             school = fuzzywuzzy_check_w_list(school, list_school, 90)
#         else:

#             # Checking if school is an outlier
#             outlier_school = False

#             # Enter an invalid or non-string as School
#             if len(school) == 0 or school == None:
#                 outlier_school = True
#             # Enter UWC as School
#             elif fuzzywuzzy_check_w_list(school, list_uwc, 90) != None:
#                 outlier_school = True
#             # Enter Country as School
#             elif fuzzywuzzy_check_w_list(school, list_countries, 90) != None:
#                 outlier_school = True
#             elif fuzzywuzzy_check_w_list(school, list_countries, 90) == None:
#                 for alt in list_countries_alt:
#                     if fuzzywuzzy_check_w_string(school, alt[0], 90) != None:
#                         outlier_school = True
#                         break
#                 for previous in list_previous_countries:
#                     if fuzzywuzzy_check_w_string(school, previous[0], 90) != None:
#                         outlier_school = True
#                         break

#             # Check for Alt School name
#             is_alt = False
#             for alt in list_school_alt:
#                 if fuzzywuzzy_check_w_string(school, alt[0], 90) != None:
#                     is_alt = True
#                     break
            
#             # If it is not an outlier and not an alt name
#             # Then it does not exist and need to add to the list
#             if outlier_school == False and is_alt == False:
#                 list_school.append(school)
    
#     print(list_school)



#####################################################
# Run uwc_back.py in above line to print out the list
#####################################################
list_school = ['Princeton University', 'College of the Atlantic', 'Wellesley College', 'Colby College', 'Middlebury College', 'San Francisco Art Institute', 'Connecticut College', 'Carleton College', 'University of Virginia', 'Hood College', 'Hamilton College', 'Johns Hopkins University', 'Methodist University', 'Earlham College', 'Swarthmore College', 'Macalester', 'Westminster College', 'Harvard University', 'Cornell University', 'Lake Forest College', 'Vassar College', 'Skidmore College', 'Dickinson College', 'Brown University', 'Bates College', 'School of the Art Institute of Chicago', 'Wesleyan University', 'Smith College', 'Dartmouth College', 'Yale University', 'St. Lawrence University', 'Whitman College', 'Williams College', 'Colorado College', 'Oberlin College', 'Mount Holyoke College', 'Lafayette College', 'University of Richmond', 'Franklin and Marshall College', 'Bryn Mawr College', 'Lewis and Clark College', 'Washington and Lee University', 'Colgate University', 'Amherst College', 'Tufts University', 'Brandeis University', 'University of Florida', 'Wheaton College', 'Luther College', 'Grinnell College', 'The Boston Conservatory', 'Barnard College', 'Bucknell University', 'Bowdoin College', 'Lehigh University', 'Union College', 'Columbia University', 'Kenyon College', 'Denison University', 'Trinity College', 'Haverford College', 'Claremont McKenna College', 'University of Pennsylvania', 'Northwestern University', 'Notre Dame of Maryland', 'The College of Idaho', 'University of Chicago', 'Gettysburg College', 'Duke University', 'Agnes Scott College', 'University of North Carolina at Chapel Hill', 'College of the Holy Cross', 'Wartburg College', 'Simmons College', 'Clark University', 'Ringling College of Art and Design', 'Stanford University', 'University of Oklahoma', 'Reed College', 'Scripps College', 'Kalamazoo College', 'University of Notre Dame', 'University of Michigan', 'Georgetown University', 'St. Olaf College', 'Occidental College', 'Pomona College', 'Randolph-Macon College', 'New York University', 'MIT', 'Bennington College', 'Savannah College of Art and Design', 'Davidson College', 'University of Rochester', 'University of California Berkeley', 'Pitzer College', 'Emory University', 'Case Western Reserve University', 'Worcester Polytechnic Institute', 'Babson College', 'George Washington University']
list_school.sort()


def summary(type_key, type_value_1, type_value_2, list_key, list_value_1, list_value_2):

    conn = sqlite3.connect('scholars.db')
    c = conn.cursor()

    summary_all = []

    for key in list_key:
        # Number of scholars from that UWC
        total_scholars = c.execute(f"""SELECT COUNT(*) FROM scholars WHERE {type_key} = \"{key}\"""").fetchall()[0][0]

        # Data format
        # key_to_value_1 = {
        #     "Tufts university": 10,
        #     "MIT": 5,
        #     ...
        #     "Harvard University": 15
        # }


        # Create a dict with school as key and nummber of student as value
        key_to_value_1 = {}
        for value_1 in list_value_1:
            count = c.execute(f"""SELECT COUNT(*) FROM scholars WHERE {type_key} = ? AND {type_value_1} = ?""", (key, value_1)).fetchall()[0][0]
            key_to_value_1.update({f"{value_1}": count})

        # Most popular School
        # key_to_value_1
        k = list(key_to_value_1.keys())
        v = list(key_to_value_1.values())
        popular_value_1 = k[v.index(max(v))]
        if total_scholars == 0:
            value_1_out_of_key = 0
        else:
            value_1_out_of_key = round((max(v)/total_scholars) * 100)


        # Data format
        # key_to_value_2 = {
        #     "Cambodia": 10,
        #     "USA": 5,
        #     ...
        #     "Thailand": 15
        # }

        # Create a dict with school as key and number of student as value
        key_to_value_2 = {}
        for value_2 in list_value_2:
            count = c.execute(f"SELECT COUNT(*) FROM scholars WHERE {type_key} = ? AND {type_value_2} = ?", (key, value_2)).fetchall()[0][0]
            key_to_value_2.update({f"{value_2}": count})

        # Most popular Country
        # uwc_to_country
        k = list(key_to_value_2.keys())
        v = list(key_to_value_2.values())
        popular_value_2 = k[v.index(max(v))]
        if total_scholars == 0:
            value_2_out_of_key = 0
        else:
            value_2_out_of_key = round((max(v)/total_scholars) * 100)


        summary_key = [key, total_scholars, popular_value_1, value_1_out_of_key, popular_value_2, value_2_out_of_key]
        summary_all.append(summary_key)

        # print(" ")
        # print(f"{uwc} has a total of {total_scholars} Davis Scholars")
        # print(f"Most popular school is {popular_school}")
        # print(f"with average of {school_acceptance_among_uwc}% acceptance among the school")
        # print(f"Most popular country is {popular_country}")
        # print(f"with average of {country_acceptance_among_uwc}% acceptance among the school")


    conn.commit()

    return summary_all



def display_summary(all_key_img_src, type_key, type_value_1, type_value_2, list_key, list_value_1, list_value_2):

    # Empty Card
    empty_card = ["Empty", "0", "?", "0", "?", "0"]

    # Data to display on phone
    phone_summary_all_type_key = summary(type_key, type_value_1, type_value_2, list_key, list_value_1, list_value_2)

    # Data to display on desktop
    num_grid_row = math.ceil(len(phone_summary_all_type_key) / 3)
    desktop_summary_all_type_key = []
    row = 0
    ii = 0
    while row < num_grid_row:

        if len(phone_summary_all_type_key) <= (ii+1):
            row_data = [phone_summary_all_type_key[ii], empty_card, empty_card]
            desktop_summary_all_type_key.append(row_data)
            break
        elif len(phone_summary_all_type_key) <= (ii+2):
            row_data = [phone_summary_all_type_key[ii], phone_summary_all_type_key[ii+1], empty_card]
            desktop_summary_all_type_key.append(row_data)
            break

        row_data = [phone_summary_all_type_key[ii], phone_summary_all_type_key[ii+1], phone_summary_all_type_key[ii+2]]
        desktop_summary_all_type_key.append(row_data)
        row += 1
        ii = 3*row

    # Data to display on tablet
    num_grid_row = math.ceil(len(phone_summary_all_type_key) / 2)
    tablet_summary_all_type_key = []
    row = 0
    ii = 0
    while row < num_grid_row:

        if len(phone_summary_all_type_key) <= (ii+1):
            row_data = [phone_summary_all_type_key[ii], empty_card]
            tablet_summary_all_type_key.append(row_data)
            break

        row_data = [phone_summary_all_type_key[ii], phone_summary_all_type_key[ii+1]]
        tablet_summary_all_type_key.append(row_data)
        row += 1
        ii = 2*row

    ############################################################################
    # Add Empty to the list where the fuction display summary is being call
    # # Adding in empty UWC to the list for empty card
    # list_key.append("Empty")
    # all_key_img_src.append("https://montevista.greatheartsamerica.org/wp-content/uploads/sites/2/2016/11/default-placeholder.png")
    ############################################################################

    output_display_summary = [desktop_summary_all_type_key, tablet_summary_all_type_key, phone_summary_all_type_key]

    return output_display_summary



# The value from submit button only return one word
# "University of California"
# Will only return "University"
# It take in other info and double check to see which one is the correct one
from flask import request

def check_detail_of(phone_summary_all_x):
    detail_of = request.form.get('view_detail')
    safety_check1 = request.form.get('safety_check1')
    safety_check3 = request.form.get('safety_check3')
    safety_check5 = request.form.get('safety_check5')

    for data in phone_summary_all_x:
        if data[0] == detail_of:
            break
        
        fw_detail_of = data[0].split()
        fw_detail_of = fw_detail_of[0]

        gt = str(data[1])+str(data[3])+str(data[5])
        given = str(safety_check1)+str(safety_check3)+str(safety_check5)
        if gt == given and fw_detail_of == detail_of:
            detail_of = data[0] 
            break
    
    return detail_of



# Get current year 
from datetime import date
CUR_YEAR = date.today().year

import pandas as pd
import plotly.express as px


def find_start_year(key, value):
    filter_query = "SELECT year FROM scholars WHERE"
    filter_query = filter_query + " " + key + " = " + "\"" + value + "\""
    conn = sqlite3.connect('scholars.db')
    c = conn.cursor()

    if len(c.execute(filter_query).fetchall()) == 0:
        return None

    START_YEAR = int(c.execute(filter_query).fetchall()[0][0])

    return START_YEAR


# Example: construct line chart with input key=uwc, value="Japan"
# Line chart will show x=year and y=number_scholar
def construct_line_chart(key, value):

    year = find_start_year(key, value)

    data = []
    while year <= CUR_YEAR:

        # Construct filter query
        filter_query = "SELECT COUNT(*) FROM scholars WHERE"
        filter_query = filter_query + " " + key + " = " + "\"" + value + "\""
        filter_query = filter_query + " AND year = " + "\"" + str(year) + "\""

        conn = sqlite3.connect('scholars.db')
        c = conn.cursor()
        line_data = c.execute(filter_query).fetchall()[0]

        data.append([year, line_data[0]])

        year = year + 1

    index = []
    for i in range(len(data)):
        index.append(i)
    
    columns = ["year", "scholar"]

    df = pd.DataFrame(data, index, columns)

    line_chart = px.line(
        df,
        x="year",
        y="scholar",
        title="Total number of Davis scholars by year",
        labels={
            "year": "Year",
            "scholar": "# Davis scholars"
        }
    )

    line_chart.update_layout(
        xaxis={'tickformat': ',d'},
        font_family="Courier",
        hoverlabel=dict(
            bgcolor="white",
            font_family="Courier"
        )
    )

    return line_chart



# key = uwc
# t10_key = school
def construct_bart10_chart(key, value, t10_key, t10_list):

    conn = sqlite3.connect('scholars.db')
    c = conn.cursor()

    # Total number of scholar
    total_scholar = "SELECT COUNT(*) FROM scholars WHERE"
    total_scholar = total_scholar + " " + key + " = " + "\"" + value + "\""
    total_scholar = c.execute(total_scholar).fetchall()[0][0]

    data_t10 = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    columns_t10 = [None, None, None, None, None, None, None, None, None]
    for t10_value in t10_list:
        filter_query = "SELECT COUNT(*) FROM scholars WHERE"
        filter_query = filter_query + " " + key + " = " + "\"" + value + "\""
        filter_query = filter_query + " AND " + t10_key + " = " + "\"" + t10_value + "\""

        bar_data = c.execute(filter_query).fetchall()[0]

        scholars_at_t10_key = bar_data[0]

        for i in range(9):

            if scholars_at_t10_key > data_t10[i]:
                data_t10[i] = scholars_at_t10_key
                columns_t10[i] = t10_value
                break
    
    data = []
    for i in range(9):
        data.append([columns_t10[8-i], round((data_t10[8-i]/total_scholar)*100)])

    # Add in remaining of other for reference
    remain = 100
    for i in data:
        remain = remain - i[1]
    data.append(["Others", remain])
    

    columns = [t10_key, "scholar"]

    index = []
    for i in range(10):
        index.append(i)

    df = pd.DataFrame(data, index, columns)

    bar_chart_t10 = px.bar(
        df,
        x="scholar",
        y=t10_key,
        orientation="h",
        title= f"Total number of Davis scholars by {t10_key}",
        labels={
            "scholar": "Total Davis scholars (%)",
            t10_key: ""
        },
        hover_data={
            t10_key: False
        },
    )

    bar_chart_t10.update_layout(
        font_family="Courier",
        hoverlabel=dict(
            bgcolor="white",
            font_family="Courier"
        )
    )

    return bar_chart_t10


def construct_bart05_chart(key, value, t05_key, t05_list):

    conn = sqlite3.connect('scholars.db')
    c = conn.cursor()

    # Total number of scholar
    total_scholar = "SELECT COUNT(*) FROM scholars WHERE"
    total_scholar = total_scholar + " " + key + " = " + "\"" + value + "\""
    total_scholar = c.execute(total_scholar).fetchall()[0][0]


    data_t05 = [0, 0, 0, 0]
    columns_t05 = [None, None, None, None]
    for t05_value in t05_list:
        filter_query = "SELECT COUNT(*) FROM scholars WHERE"
        filter_query = filter_query + " " + key + " = " + "\"" + value + "\""
        filter_query = filter_query + " AND " + t05_key + " = " + "\"" + t05_value + "\""

        bar_data = c.execute(filter_query).fetchall()[0]

        scholars_at_t05_key = bar_data[0]

        for i in range(4):

            if scholars_at_t05_key > data_t05[i]:
                data_t05[i] = scholars_at_t05_key
                columns_t05[i] = t05_value
                break
    
    data = []
    for i in range(4):
        data.append([columns_t05[3-i], round((data_t05[3-i]/total_scholar)*100)])
    
    # Add in remainin of other for reference
    remain = 100
    for i in data:
        remain = remain - i[1]
    data.append(["Others", remain])

    columns = [t05_key, "scholar"]

    index = []
    for i in range(5):
        index.append(i)

    df = pd.DataFrame(data, index, columns)

    bar_chart_t05 = px.bar(
        df,
        x="scholar",
        y=t05_key,
        orientation="h",
        title= f"Total number of Davis scholars by {t05_key}",
        labels={
            "scholar": "Total Davis scholars (%)",
            t05_key: ""
        },
        hover_data={
            t05_key: False
        },
    )

    bar_chart_t05.update_layout(
        font_family="Courier",
        hoverlabel=dict(
            bgcolor="white",
            font_family="Courier"
        )
    )

    return bar_chart_t05



def construct_charts(determine_detail_to_view, key_line, key_t10, key_t05):

    if len(determine_detail_to_view) == 1:
        view_detail = determine_detail_to_view[0]
    else: 
        view_detail = check_detail_of(determine_detail_to_view)
    session['key_charts'] = key_line
    session['value_charts'] = view_detail

    # No data in database
    # Thus no charts to display
    if find_start_year(key_line, view_detail) == None:
        session['charts'] = False
        return None

    line_chart = construct_line_chart(key_line, view_detail)
    line_chart_JSON = json.dumps(line_chart, cls=plotly.utils.PlotlyJSONEncoder)
    session['line_chart_JSON'] = line_chart_JSON

    if key_t10 == "uwc":
        list_t10 = list_uwc
    elif key_t10 == "country":
        list_t10 = list_countries
    elif key_t10 == "school":
        list_t10 = list_school
    bart10_chart = construct_bart10_chart(key_line, view_detail, key_t10, list_t10)
    bart10_chart_JSON = json.dumps(bart10_chart, cls=plotly.utils.PlotlyJSONEncoder)
    session['bart10_chart_JSON'] = bart10_chart_JSON

    if key_t05 == "uwc":
        list_t05 = list_uwc
    elif key_t05 == "country":
        list_t05 = list_countries
    elif key_t05 == "school":
        list_t05 = list_school
    bart05_chart = construct_bart05_chart(key_line, view_detail, key_t05, list_t05)
    bart05_chart_JSON = json.dumps(bart05_chart, cls=plotly.utils.PlotlyJSONEncoder)
    session['bart05_chart_JSON'] = bart05_chart_JSON

    session['charts'] = True
    return 1



def filter_view_charts(filter_query):
    # extract value of the key uwc
    start_index = filter_query.index("\"")
    filter_query = filter_query.replace("\"", "")
    value = filter_query[start_index:]

    # View chart from filter if we are only filtering one keyword at a time
    if "AND" not in filter_query and "WHERE name" not in filter_query and "WHERE year" not in filter_query:
        if "WHERE uwc" in filter_query:
            construct_charts([value], "uwc", "school", "country")
        elif "WHERE country" in filter_query:
            construct_charts([value], "country", "school", "uwc")
        elif "WHERE school" in filter_query:
            construct_charts([value], "school", "country", "uwc")

        flash(Markup('<a href="/detail" class="nav-link"> (click here to view in detail) </a>'), 'success')

