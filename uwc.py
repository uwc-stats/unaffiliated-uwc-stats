from flask import Flask, render_template, redirect, session, url_for
from flask import request
from flask import flash, Markup
app = Flask(__name__)

import sqlite3

app.config['SECRET_KEY'] = '354e1ab4c6d9c6bc661c258a618947bf'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

from uwc_back import UserFilterDavis, blur, construct_filter_query, construct_count_query, correction_filter, construct_correction_filter_query
from uwc_back import construct_charts
from uwc_back import list_school, list_uwc, list_countries

from uwc_back import filter_view_charts

from img_scrap import all_uwc_img_src, all_country_img_src, all_school_img_src


@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():

    filter_query = "SELECT name, country, uwc, school, year FROM scholars"
    count_query = "SELECT COUNT(*) FROM scholars"
    if 'filter_query' in session:
        filter_query = session['filter_query']
        session.pop('filter_query', None)
    if "count_query" in session:
        count_query = session['count_query']
        session.pop('count_query', None)


    # The form submit
    form = UserFilterDavis()
    if form.validate_on_submit():

        # When submit, construct the filter query
        filter_query = construct_filter_query(form)

        # If user actually enter something in the form
        # Store the constructed filter query in session
        if filter_query != "SELECT name, country, uwc, school, year FROM scholars":

            session['filter_query'] = filter_query

            count_query = construct_count_query(form)
            session['count_query'] = count_query

            session['correction_filter_country'] = form.country.data
            session['correction_filter_uwc'] = form.uwc.data
            session['correction_filter_school'] = form.school.data
        
        # User does not enter anything in the form - reload page to give out filter correction
        if filter_query == "SELECT name, country, uwc, school, year FROM scholars":
            construct_correction_filter_query(filter_query)

        return redirect(url_for('home'))    


    # Search databse for the filter output
    conn_scholars = sqlite3.connect('scholars.db')
    c_scholars = conn_scholars.cursor()
    scholars = c_scholars.execute(filter_query).fetchall()
    scholars = blur(scholars)

    # Search database for counting number of output
    conn_count = sqlite3.connect('scholars.db')
    c_count = conn_count.cursor()
    count = c_count.execute(count_query).fetchall()[0][0]

    # Check if need filter correction
    need_correction = False
    combine_correction = ""
    if count == 0:
        all_correction = correction_filter(session['correction_filter_country'], session['correction_filter_uwc'], session['correction_filter_school'])
        session['all_correction'] = all_correction
        # all_correction = [
        #    ["country", (country_name)],
        #    ["uwc", (uwc_name)],
        #    ["school", (school_name)],
        # ]

        # Clear session
        if 'correction_filter_country' in session:
            session.pop('correction_filter_country', None)
        if 'correction_filter_uwc' in session:
            session.pop('correction_filter_uwc', None)
        if 'correction_filter_school' in session:
            session.pop('correction_filter_school', None)    

        need_correction = True

        # Combine correction for display back at home
        for correction in all_correction:
            if combine_correction == "":
                combine_correction = correction[1]
            else:
                combine_correction = combine_correction + " + " + correction[1]


    # view chart from one varibale filter
    if filter_query != "SELECT name, country, uwc, school, year FROM scholars" and count != 0:
        filter_view_charts(filter_query)



    return render_template('home.html', scholars=scholars, form=form, combine_correction = combine_correction, need_correction = need_correction)



@app.route("/uwc", methods=['GET', 'POST'])
def uwc():
   
    from pre_uwc_summary import uwc_output_display_summary
    output_display_summary = uwc_output_display_summary

    list_uwc.append("Empty")
    all_uwc_img_src.append("https://montevista.greatheartsamerica.org/wp-content/uploads/sites/2/2016/11/default-placeholder.png")
    
    desktop_summary_all_uwc = output_display_summary[0]
    tablet_summary_all_uwc = output_display_summary[1]
    phone_summary_all_uwc = output_display_summary[2]


    if request.method == 'POST':
        # construct-charts(phone_summary_all_key, key_line, key_t10, key_t05)
        construct_charts(phone_summary_all_uwc, "uwc", "school", "country")

        return redirect("/detail")
        

    return render_template("uwc.html", desktop_summary_all_uwc = desktop_summary_all_uwc, tablet_summary_all_uwc = tablet_summary_all_uwc, phone_summary_all_uwc = phone_summary_all_uwc, all_uwc_img_src = all_uwc_img_src, list_uwc = list_uwc)


@app.route("/country", methods=['GET', 'POST'])
def country():
    from pre_country_summary import country_output_display_summary
    output_display_summary = country_output_display_summary

    list_countries.append("Empty")
    all_country_img_src.append("https://montevista.greatheartsamerica.org/wp-content/uploads/sites/2/2016/11/default-placeholder.png")

    desktop_summary_all_country = output_display_summary[0]
    tablet_summary_all_country = output_display_summary[1]
    phone_summary_all_country = output_display_summary[2]

    if request.method == 'POST':
        # construct-charts(phone_summary_all_key, key_line, key_t10, key_t05)
        construct_charts(phone_summary_all_country, "country", "school", "uwc")

        return redirect("/detail")


    return render_template("country.html", desktop_summary_all_country = desktop_summary_all_country, tablet_summary_all_country = tablet_summary_all_country, phone_summary_all_country = phone_summary_all_country, all_country_img_src = all_country_img_src, list_countries = list_countries)


@app.route("/undergraduate", methods=['GET', 'POST'])
# On UI it is undergrad
# Backend everything is refer to as school for simplicity
@app.route("/school", methods=['GET', 'POST'])
def school():
    from pre_school_summary import school_output_display_summary
    output_display_summary = school_output_display_summary

    list_school.append("Empty")
    all_school_img_src.append("https://montevista.greatheartsamerica.org/wp-content/uploads/sites/2/2016/11/default-placeholder.png")

    desktop_summary_all_school = output_display_summary[0]
    tablet_summary_all_school = output_display_summary[1]
    phone_summary_all_school = output_display_summary[2]

    if request.method == 'POST':
        # construct-charts(phone_summary_all_key, key_line, key_t10, key_t05)
        construct_charts(phone_summary_all_school, "school", "country", "uwc")

        return redirect("/detail")


    return render_template("school.html", desktop_summary_all_school = desktop_summary_all_school, tablet_summary_all_school = tablet_summary_all_school, phone_summary_all_school = phone_summary_all_school, all_school_img_src = all_school_img_src, list_school = list_school)




@app.route("/detail")
def detail():
    line_chart_JSON = session['line_chart_JSON']
    bart10_chart_JSON = session['bart10_chart_JSON']
    bart05_chart_JSON = session['bart05_chart_JSON']

    key_charts = session['key_charts']
    value_charts = session['value_charts']
    detail_of=[value_charts]
    
    # True if there are charts to be display
    charts = session['charts']

    return render_template("detail.html", charts=charts,detail_of=detail_of, line_chart_JSON=line_chart_JSON, bart10_chart_JSON=bart10_chart_JSON, bart05_chart_JSON=bart05_chart_JSON)




@app.route("/about")
def about():
    return render_template('about.html')




if __name__ == '__main__':
    app.run(debug=True)
