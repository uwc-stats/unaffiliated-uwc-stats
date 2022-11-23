import sqlite3, csv

from uwc_back import fuzzywuzzy_check_w_list, fuzzywuzzy_check_w_string
from uwc_back import list_countries, list_previous_countries, list_countries_alt
from uwc_back import list_uwc
from uwc_back import list_school, list_school_alt


conn = sqlite3.connect('scholars.db')
list_invalid_scholars = []

c = conn.cursor()


c.execute("""
DROP TABLE scholars
""")

c.execute("""CREATE TABLE scholars (
            id integer primary key autoincrement,
            name text,
            country text,
            uwc text,
            school text,
            year text
)""")






#davis_scholar_database.csv
# ï»¿Name
with open('davis_scholar_database.csv', 'r') as csv_file:
    csv_reader = csv.DictReader(csv_file)

    for line in csv_reader:
        name = line['ï»¿Name']
        country = line['Country']
        uwc = line['UWC School']
        school = line['School']
        year = line['Year']



        if name == "" or country == "" or uwc == "" or school == "" or year == "":
            print("Enter Empty String as input")
            print(str(name) + "||" + str(country) + "||" + str(uwc) + "||" + str(school) + "||" + str(year))
            list_invalid_scholars.append([str(name), str(country), str(uwc), str(school), str(year)])
            continue
        if name == None or country == None or uwc == None or school == None or year == None:
            print("Enter None as input")
            print(str(name) + "||" + str(country) + "||" + str(uwc) + "||" + str(school) + "||" + str(year))
            list_invalid_scholars.append([str(name), str(country), str(uwc), str(school), str(year)])
            continue
        if name == "None" or country == "None" or uwc == "None" or school == "None" or year == "None":
            print("Enter None as input")
            print(str(name) + "||" + str(country) + "||" + str(uwc) + "||" + str(school) + "||" + str(year))
            list_invalid_scholars.append([str(name), str(country), str(uwc), str(school), str(year)])
            continue
        



        # Cleaning Country
        if country in list_countries:
            country = country
        else:
    
            # Hard code country with edge-case name
            if "Korea" in country:
                if "Democratic" in country:
                    country = "Korea, Democratic People's Republic of"
                else:
                    country = "Korea, Republic of"
            elif "Congo" in country:
                if "Democratic" in country:
                    country = "Congo, Democratic Republic of the"
                else:
                    country = "Congo"
            else:
        
                # Previous name
                for change in list_previous_countries:
                    if change[0] == country:
                        country = change[1]
                
                # Alternative name
                for alt in list_countries_alt:
                    if fuzzywuzzy_check_w_string(country, alt[0], 90) != None:
                        country = alt[1]
                        
                # Enter UWC as Country
                if fuzzywuzzy_check_w_list(country, list_uwc, 90) != None:
                    print("Enter UWC as Country")
                    print(str(name) + "||" + str(country) + "||" + str(uwc) + "||" + str(school) + "||" + str(year))
                    list_invalid_scholars.append([str(name), str(country), str(uwc), str(school), str(year)])
                    continue

                # Columbia Univesity is confused as a country name Columbia
                if fuzzywuzzy_check_w_list(country, list_school, 90) != "Columbia University":
                    
                    # Enter School as Country
                    if fuzzywuzzy_check_w_list(country, list_school, 90) != None:
                        print("Enter School as Country")
                        print(str(name) + "||" + str(country) + "||" + str(uwc) + "||" + str(school) + "||" + str(year))
                        list_invalid_scholars.append([str(name), str(country), str(uwc), str(school), str(year)])
                        continue
                    # Enter Alt School as Coutry
                    for alt in list_school_alt:
                        if fuzzywuzzy_check_w_string(country, alt[0], 90) != None:
                            print("Enter School as Country")
                            print(str(name) + "||" + str(country) + "||" + str(uwc) + "||" + str(school) + "||" + str(year))
                            list_invalid_scholars.append([str(name), str(country), str(uwc), str(school), str(year)])
                            continue
                
                country = fuzzywuzzy_check_w_list(country, list_countries, 90)




        # Cleaning UWC
        if uwc in list_uwc:
            uwc = uwc

        elif fuzzywuzzy_check_w_list(uwc, list_uwc, 90) != None:
            uwc = fuzzywuzzy_check_w_list(uwc, list_uwc, 90) 
    
        else:

            # Hard code UWC with edge-case name
            if fuzzywuzzy_check_w_string(uwc, "Waterford KaMhlaba UWC, Swaziland", 90) != None:
                uwc = "Waterford Kamhlaba Southern Africa"
            elif fuzzywuzzy_check_w_string(uwc, "UWC of Southeast Asia, Singapore", 90) != None:
                uwc = "South East Asia"
            elif fuzzywuzzy_check_w_string(uwc, "Simon Bolivar UWC of Agriculture of Venezuela", 90) != None:
                uwc = "Simon Bolivar UWC of Agriculture"
            
            else:

                # Enter Country as UWC
                if fuzzywuzzy_check_w_list(uwc, list_countries, 90) != None:
                    print("Enter Country as UWC")
                    print(str(name) + "||" + str(country) + "||" + str(uwc) + "||" + str(school) + "||" + str(year))
                    list_invalid_scholars.append([str(name), str(country), str(uwc), str(school), str(year)])
                    continue
                # Enter Alt Country as UWC
                for alt in list_countries_alt:
                    if fuzzywuzzy_check_w_string(uwc, alt[0], 90) != None:
                        print("Enter Country as UWC")
                        print(str(name) + "||" + str(country) + "||" + str(uwc) + "||" + str(school) + "||" + str(year))
                        list_invalid_scholars.append([str(name), str(country), str(uwc), str(school), str(year)])
                        continue
                # Enter Old Country as UWC
                for previous in list_previous_countries:
                    if fuzzywuzzy_check_w_string(uwc, previous[0], 90) != None:
                        print("Enter Country as UWC")
                        print(str(name) + "||" + str(country) + "||" + str(uwc) + "||" + str(school) + "||" + str(year))
                        list_invalid_scholars.append([str(name), str(country), str(uwc), str(school), str(year)])
                        continue
                
                # Enter School as UWC
                if fuzzywuzzy_check_w_list(uwc, list_school, 90) != None:
                    print("Enter School as UWC")
                    print(str(name) + "||" + str(country) + "||" + str(uwc) + "||" + str(school) + "||" + str(year))
                    list_invalid_scholars.append([str(name), str(country), str(uwc), str(school), str(year)])
                    continue
                # Enter Alt school name as UWC
                for alt in list_school_alt:
                    if fuzzywuzzy_check_w_string(uwc, alt[0], 90) != None:
                        print("Enter School as UWC")
                        print(str(name) + "||" + str(country) + "||" + str(uwc) + "||" + str(school) + "||" + str(year))
                        list_invalid_scholars.append([str(name), str(country), str(uwc), str(school), str(year)])
                        continue
        



        # Cleaning School
        if school in list_school:
            school = school

        # Hard code School with edge-case name
        elif fuzzywuzzy_check_w_string(school, "College of the Atlantic", 90) != None:
            school = "College of the Atlantic"
        
        # Mispell school name
        elif fuzzywuzzy_check_w_list(school, list_school, 90) != None:
            school = fuzzywuzzy_check_w_list(school, list_school, 90)
        
        elif fuzzywuzzy_check_w_list(school, list_school, 90) == None:
            # Alt School name
            for alt in list_school_alt:
                if fuzzywuzzy_check_w_string(school, alt[0], 90) != None:
                    school = alt[1]
                    break
            
            # Enter UWC as School
            if fuzzywuzzy_check_w_list(school,list_uwc, 90) != None:
                print("Enter UWC as School")
                print(str(name) + "||" + str(country) + "||" + str(uwc) + "||" + str(school) + "||" + str(year))
                list_invalid_scholars.append([str(name), str(country), str(uwc), str(school), str(year)])
                continue

            # Enter Country as School
            if fuzzywuzzy_check_w_list(school, list_countries, 90) != None:
                print("Enter Country as School")
                print(str(name) + "||" + str(country) + "||" + str(uwc) + "||" + str(school) + "||" + str(year))
                list_invalid_scholars.append([str(name), str(country), str(uwc), str(school), str(year)])
                continue
            # Enter Alt Country as School
            for alt in list_countries_alt:
                if fuzzywuzzy_check_w_string(school, alt[0], 90) != None:
                    print("Enter Country as School")
                    print(str(name) + "||" + str(country) + "||" + str(uwc) + "||" + str(school) + "||" + str(year))
                    list_invalid_scholars.append([str(name), str(country), str(uwc), str(school), str(year)])
                    continue
            # Enter Old Country as School
            for previous in list_previous_countries:
                if fuzzywuzzy_check_w_string(school, previous[0], 90) != None:
                    print("Enter Country as UWC")
                    print(str(name) + "||" + str(country) + "||" + str(uwc) + "||" + str(school) + "||" + str(year))
                    list_invalid_scholars.append([str(name), str(country), str(uwc), str(school), str(year)])
                    continue


        c.execute("INSERT INTO scholars (name, country, uwc, school, year) VALUES(?, ?, ?, ?, ?)", (name, country, uwc, school, year))

conn.commit()
conn.close()




###################################
##########INVALID SCHOLARS#########
###################################

conn = sqlite3.connect('invalidscholars.db')

c = conn.cursor()


c.execute("""
DROP TABLE invalidscholars
""")

c.execute("""CREATE TABLE invalidscholars (
            id integer primary key autoincrement,
            name text,
            country text,
            uwc text,
            school text,
            year text
)""")

for scholar in list_invalid_scholars:
    print(str(scholar))
    name = scholar[0]
    country = scholar[1]
    uwc = scholar[2]
    school = scholar[3]
    year = scholar[4]

    c.execute("INSERT INTO invalidscholars (name, country, uwc, school, year) VALUES(?, ?, ?, ?, ?)", (name, country, uwc, school, year))

conn.commit()
conn.close()



