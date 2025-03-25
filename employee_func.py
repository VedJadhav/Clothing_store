"""This module will be used for functionalities of the employee"""
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mpl_dates
import PySimpleGUI as sg
import numpy as np
import mysql.connector as sqltor
from mysql.connector import errors as mysql_errors
import mplcursors

matplotlib.use('Tkagg')
plt.style.use('seaborn-v0_8')
file=open('settings.txt')
data=file.readlines()
file.close()
for i in range(len(data)):
    data[i]=data[i][:-1]
mycon = sqltor.connect(host=data[0], user=data[1], passwd=data[2],database=data[3])
cursor = mycon.cursor()

# Set the PysimpleGUI theme and font
sg.theme("DarkAmber")
main_font_title=("Times New Roman", "12")
main_font_normal=("Times New Roman", "11")

def main(emp = ''):
    """This Function is responsible for the display of Employee Screen"""
    global data
    global data_product
    stck_data = display_stock()
    stats = revenue_analysis()
    customer_det = cust_details()
    layout = [
        [sg.Text(f"Welcome {emp}", font=main_font_title)],
        [sg.Text('Please choose the function', font=main_font_normal)],
        [sg.TabGroup([
        [sg.Tab("Edit Stock Data",stck_data,key = 'Edit', font=main_font_normal),
            sg.Tab("Statistics",stats, font=main_font_normal),sg.Tab("See Customer Details",customer_det, font=main_font_normal)]],key='Tabs')],
        [sg.Text("", font=main_font_normal)]
    ]
    win = sg.Window('Welcome',layout)
    while True:
        event,value = win.read()
        if event in (None, 'Exit'):
            break
        if event == 'Add':
            add_stock()
            cursor.execute("SELECT * FROM PRODUCTS")
            dataNew = cursor.fetchall()
            win['Table'].update(dataNew)
            data_product = list(dataNew)
        elif event == 'Update':
            try:
                prod_clicked = value['Table'][0]
                prod_click_id = int(data_product[prod_clicked][0])
                update_data(prod_click_id)
                cursor.execute("SELECT * FROM PRODUCTS")
                dataNew = cursor.fetchall()
                win['Table'].update(dataNew)
            except IndexError:
                sg.popup( "Warning: No Product Selected",title = "WARNING", font=main_font_normal)
        elif event == 'Delete' :
            try:
                prod_clicked = value['Table'][0]
                prod_click_id = int(data_product[prod_clicked][0])
                cursor.execute(f"DELETE FROM PRODUCTS WHERE ID = {prod_click_id}")
                mycon.commit()
                cursor.execute("SELECT * FROM PRODUCTS")
                data_product = cursor.fetchall()
                win['Table'].update(data_product)
            except IndexError:
                sg.popup('NO PRODUCTS SELECTED', font=main_font_normal)
        if event == "sort_amt":
            query = """SELECT Name,Phone_Number,Email_ID,Total_Price FROM CUSTOMERS
            ORDER BY Total_Price DESC"""
            cursor.execute(query)
            data =  cursor.fetchall()
            win['cust_Table'].update(data)
            win['email'].update('')
            win['name'].update('')
            win['mob'].update('')
            win['show_det'].update('')
            win['show'].update(disabled=True)
        elif event=='sort_name':
            query="""SELECT Name,Phone_Number,Email_ID,Total_Price FROM CUSTOMERS
            ORDER BY Name"""
            cursor.execute(query)
            data=cursor.fetchall()
            win['cust_Table'].update(data)
            win['email'].update('')
            win['name'].update('')
            win['mob'].update('')
            win['show_det'].update('')
            win['show'].update(disabled=True)
        if event == 'show':
            show_details(data[value['cust_Table'][0]])

        if event=='name' and value:
            query = f"""Select Name,Phone_Number,Email_ID,Total_Price from customers
            where name like '{value['name']}%' and email_id like '{value['email']}%' and phone_number like '{value['mob']}%'
            """
            cursor.execute(query)
            data =  cursor.fetchall()
            win['cust_Table'].update(data)
            win['show_det'].update('')
            win['show'].update(disabled=True)
        elif event=='email':
            query = """Select Name,Phone_Number,Email_ID,Total_Price from customers
            where name like '{}%' and email_id like '{}%' and phone_number like '{}%'
            """.format(value['name'],value['email'],value['mob'])
            cursor.execute(query)
            data =  cursor.fetchall()
            win['cust_Table'].update(data)
            win['show_det'].update('')
            win['show'].update(disabled=True)
        elif event=='mob':
            query = """Select Name,Phone_Number,Email_ID,Total_Price from customers
            where name like '{}%' and email_id like '{}%' and phone_number like '{}%'
            """.format(value['name'],value['email'],value['mob'])
            cursor.execute(query)
            data =  cursor.fetchall()
            win['cust_Table'].update(data)
            win['show_det'].update('')
            win['show'].update(disabled=True)
        if event == 'cust_Table' and value['cust_Table']!=[]:
            em = data[value['cust_Table'][0]][2] #Basically extracting email
            win['show_det'].update(em)
            win['show'].update(disabled = False)
        if event=='Calendar_Date':
            win['Go1'].update(disabled=False)
        if event == 'Go1':
            win.hide()
            daily_profit(value['daily_profit'],value['Calendar_Date'])
            win.un_hide()

        elif event == 'Go2':
            year1 = value['y1m'][0]
            year2 = value['y2m'][0]
            win.hide()
            monthly(year1,year2)
            win.un_hide()
        if event == 'Cat_rev' and value['Cat_rev'] == 'Trend':
            win['year1'].update(disabled = True)
            win['year2'].update(disabled=False)
            win['Go3'].update(disabled = False)
        if event == 'Cat_rev' and value['Cat_rev'] == 'Comparision':
            win['year1'].update(disabled = False)
            win['year2'].update(disabled=False)
            win['Go3'].update(disabled = False)
        if event == 'Go3' and value['Cat_rev'] == 'Comparision':
            win.hide()
            categ_rev_comp(value['year1'][0],value['year2'][0])
            win.un_hide()
        if event == 'Go3' and value['Cat_rev'] == 'Trend':
            win.hide()
            categ_rev_trend(value['year2'][0])
            win.un_hide()
        if event == 'Brand_rev' and value['Brand_rev'] == 'Comparision':
            win['year1_b'].update(disabled = False)
            win['year2_b'].update(disabled=False)
            win['Go_b'].update(disabled = False)
            win['b1'].update(visible = False)
            win['b2'].update(visible =False)
            win['b3'].update(visible =False)
        elif event == 'Brand_rev' and value['Brand_rev'] == 'Trend':
            win['year1_b'].update(disabled = True)
            win['year2_b'].update(disabled=False)
            win['Go_b'].update(disabled = False)
            win['b1'].update(visible = True)
            win['b2'].update(visible =True)
            win['b3'].update(visible =True)
        if event == 'Go_b' and value['Brand_rev'] == 'Trend':
            b1 = value['b1']
            b2 = value['b2']
            b3 = value['b3']
            win.hide()
            brand_rev_trend(b1,b2,b3,value['year2_b'][0])
            win.un_hide()
        if event == 'Go_b' and value['Brand_rev'] == 'Comparision':
            win.hide()
            brand_rev_comp(value['year1_b'][0],value['year2_b'][0])
            win.un_hide()
def display_stock():
    """This displays the products"""
    cursor.execute("SELECT * FROM PRODUCTS")
    global data_product
    data_product = cursor.fetchall()
    heading = ['Prod ID','Name','Brand','Size','Quantity','Cost_Price','Selling_Price']
    layout1 = [[sg.Text('Product List', font=main_font_normal)],
    [sg.Table(data_product,headings = heading,key = 'Table',justification='left'
    ,auto_size_columns=True,expand_y = True, font=main_font_normal)],
    [sg.Button('Add',key = 'Add', font=main_font_normal),sg.Button('Update Stock',key = 'Update', font=main_font_normal),
        sg.Button('Delete',key = 'Delete', font=main_font_normal)]]
    return layout1
def add_stock():
    """This function enables the employee to add new products in stock"""
    msg = sg.Text('Enter appropriate data', font=main_font_normal)
    lay = [[msg],[sg.Text('Enter Product ID',size = (18,1), font=main_font_normal),
            sg.Input(key = 'id',enable_events=True, font=main_font_normal)],
    [sg.Text('Product Name',size = (18,1), font=main_font_normal),sg.Input(key = 'name',enable_events=True, font=main_font_normal)],
    [sg.Text('Product Brand',size = (18,1), font=main_font_normal),sg.Input(key = 'brand',enable_events=True, font=main_font_normal)],
    [sg.Text('Product Size',size = (18,1), font=main_font_normal),sg.Input(key = 'size',enable_events=True, font=main_font_normal)],
    [sg.Text('Product Quantity',size = (18,1), font=main_font_normal),sg.Input(key = 'quantity',enable_events=True, font=main_font_normal)],
    [sg.Text('Product Cost Price',size = (18,1), font=main_font_normal),sg.Input(key = 'cost_price',enable_events=True, font=main_font_normal)],
    [sg.Text('Product Sell Price',size=(18,1), font=main_font_normal),sg.Input(key ='selling_price',enable_events=True, font=main_font_normal)],
    [sg.Text('Product Category',size = (18,1), font=main_font_normal),sg.Input(key ='category',enable_events=True, font=main_font_normal)]]
    layout = [[sg.Frame("Add New Stock",lay, font=main_font_normal)],
    [sg.Button('Go Back', font=main_font_normal),sg.Button('Confirm',key = 'Confirm', font=main_font_normal)]
    ]
    window = sg.Window("New Product",layout=layout)
    while True:
        event,value = window.read()
        if event in (None, "Go Back"):
            window.close()
            break
        try:
            if event == 'Confirm':
                insert_prod = """INSERT INTO PRODUCTS
                (ID,Name,Brand,Size,Quantity,Cost_Price,Selling_Price, Category)
                Values(%s,%s,%s,%s,%s,%s,%s,%s)"""
                upd_value = [list(value.values())]
                cursor.executemany(insert_prod,upd_value)
                mycon.commit()
                sg.popup('Stock Added to Database', font=main_font_normal)
                window.close()
                break
        except mysql_errors.DatabaseError:
            msg.update("WRONG DATA ENTERED",text_color='Red')
def update_data(ID):
    """This function allows employee to modify the details of existing stock"""
    lay = [[sg.Text('Product ID',size = (18,1), font=main_font_normal),
        sg.Input(default_text = ID, key = 'ID',readonly=True,tooltip = "It's Read Only",
            disabled_readonly_background_color='Gray',disabled_readonly_text_color='Black', font=main_font_normal)],
    [sg.Text('Product Name',size = (18,1), font=main_font_normal),sg.Input(key = 'Name', font=main_font_normal)],
    [sg.Text('Product Brand',size = (18,1), font=main_font_normal),sg.Input(key = 'Brand', font=main_font_normal)],
    [sg.Text('Product Size',size = (18,1), font=main_font_normal),sg.Input(key = 'Size', font=main_font_normal)],
    [sg.Text('Quantity of Product',size = (18,1), font=main_font_normal),sg.Input(key = 'Quantity', font=main_font_normal)],
    [sg.Text('Cost Price of Product',size = (18,1), font=main_font_normal),sg.Input(key = 'Cost_Price', font=main_font_normal)],
    [sg.Text('Selling Price of Product',size = (18,1), font=main_font_normal),sg.Input(key ='Selling_Price', font=main_font_normal)]
    ]
    msg=sg.Text("Instructions: The data which is not to be updated shall be left blank", font=main_font_normal)
    layout=[[msg],
        [sg.Frame("Add New Stock",lay, font=main_font_normal)],
    [sg.Button('Go Back', font=main_font_normal),sg.Button('Confirm', font=main_font_normal)]
    ]
    win = sg.Window('Update Data',layout,finalize=True)
    while True:
        event,value=win.read()
        if event is None:
            break
        try:
            if event == 'Confirm':
                for i in value:
                    if value[i] != '' and i!= 'ID':
                        cursor.execute(f"""UPDATE PRODUCTS SET {i} = '{value[i]}'
                        WHERE ID = {int(ID)}""")
                sg.popup('Data Updated', font=main_font_normal)
                mycon.commit()
                win.close()
        except mysql_errors.DatabaseError:
            msg.update('Wrong data entered...')

def revenue_analysis():
    cursor.execute("select DISTINCT YEAR(Purchase_Date) from purchase order by year(purchase_date)")
    year = cursor.fetchall()
    cursor.execute("SELECT DISTINCT Product_Brand FROM PURCHASE")
    brand = cursor.fetchall()
    brand = [i[0] for i in brand]
    
    date_inp = sg.Input("Date", key="Calendar_Date",size=(10, None),
    readonly=True, disabled_readonly_background_color="Gray",
    disabled_readonly_text_color="Black",
    font=main_font_normal,
    enable_events=True)

    calender_btn = sg.CalendarButton('Choose Date',close_when_date_chosen=False,
    title='Choose Date',format='%Y-%m-%d', key='Calendar', enable_events=True)

    stats = [
        [sg.Text('Finance', font=main_font_normal)],
        [sg.Text('Daily Profit:',size = (15,1), font=main_font_normal),
        date_inp,calender_btn,
        sg.Combo(default_value = '7',values =[str(i) for i in range(7,31)],key = 'daily_profit',
        readonly = True,size=(7,1), font=main_font_normal,tooltip = 'Count of dates'),
        sg.Button('GO',k='Go1', font=main_font_normal, disabled=True)
        ],
        [sg.Text('Monthly Profit:',size = (15,1), font=main_font_normal),
        sg.Combo(default_value = year[-1],values = year,k = 'y1m',readonly = True,
                 font=main_font_normal,tooltip = 'Year 1'),
        sg.Combo(default_value = year[-2],values = year,key = 'y2m',readonly = True,
                 font=main_font_normal,tooltip = 'Year 2'),
        sg.Button('GO',k='Go2', font=main_font_normal)],
        [sg.Text('Revenue Generated per Category', font=main_font_normal)],
        [sg.Combo(default_value = '-',values = ['Trend','Comparision'],readonly = True,
        enable_events=True,key='Cat_rev', font=main_font_normal),
        sg.Combo(default_value = year[0],values = year,k = 'year1',
            readonly = True,disabled = True, font=main_font_normal,tooltip = 'Year 1'),
        sg.Combo(default_value = year[-2],values = year,k = 'year2',readonly = True,
            disabled = True, font=main_font_normal,tooltip = 'Year 2'),
        sg.Button('Go',key = 'Go3',disabled=True, font=main_font_normal)],
        [sg.Text('Revenue Generated by Brand', font=main_font_normal)],
        [sg.Combo(default_value = '-',values = ['Trend','Comparision'],readonly = True,
            enable_events=True,key='Brand_rev', font=main_font_normal),
        sg.Combo(default_value = year[-2],values = year,k = 'year1_b',readonly = True,
            disabled = True, font=main_font_normal,tooltip = 'Year 1'),
        sg.Combo(default_value = year[-2],values = year,k = 'year2_b',readonly = True,
            disabled = True, font=main_font_normal,tooltip = 'Year 2'),
        sg.Button('Go',key = 'Go_b',disabled=True, font=main_font_normal)],
        [sg.Col([[sg.Combo(values = brand,readonly = True,visible = False,key='b1',
             font=main_font_normal,tooltip = 'Brand 1')]]),
        sg.Col([[sg.Combo(values = brand,readonly = True,visible = False,key='b2',
             font=main_font_normal,tooltip = 'Brand 2')]]),
        sg.Col([[sg.Combo(values = brand,readonly = True,visible = False,key='b3',
             font=main_font_normal,tooltip = 'Brand 3')]])]
           ]
    return stats


cursor.execute('SELECT Name,Phone_Number,Email_ID,Total_Price FROM CUSTOMERS')
data = cursor.fetchall()
def cust_details():
    """This function shows the list of customers"""
    global data
    heading = ['Name','Phone_Number','Email_ID','Total_Purchase_Amt']
    table = sg.Table(data,headings=heading,key = 'cust_Table',enable_events=True, font=main_font_normal)
    layout = [[sg.Radio("Sort by Purchase Amount",group_id='sort',key = 'sort_amt',
        enable_events=True, font=main_font_normal),
        sg.Radio("Sort by Name",default=True,group_id='sort',key = 'sort_name',enable_events=True, font=main_font_normal)],
    [sg.Text('Search by Name',size = (15,1), font=main_font_normal),sg.Input(key = 'name',enable_events=True, font=main_font_normal)],
    [sg.Text('Search by Email ID',size = (15,1), font=main_font_normal),sg.Input(key = 'email',enable_events=True, font=main_font_normal)],
    [sg.Text('Search by Mobile',size = (15,1), font=main_font_normal),sg.Input(key = 'mob',enable_events=True, font=main_font_normal)],
    [table],
    [sg.Input(key = 'show_det', font=main_font_normal),sg.Button('Show Details', disabled=True,key = 'show', font=main_font_normal)],
    [sg.Button('Exit', font=main_font_normal)]
    ]
    return layout

def show_details(dat):#dat is a tuple containing name, mob, email, pur_amount
    """This function shows the details of the customer"""
    heading = ['Invoice Number',  'Purchase date','Total Cost']
    cursor.execute(f"""SELECT INVOICE_NUMBER, PURCHASE_DATE, SUM(PRODUCT_TOT_COST) FROM PURCHASE
    WHERE CUSTOMER_EMAIL = '{dat[2]}'
    GROUP BY INVOICE_NUMBER""")
    purchase_data = cursor.fetchall()
    if not purchase_data:
        sg.popup('NO DATA FOUND', font=main_font_normal)
    
    else:
        table = sg.Table(purchase_data,headings=heading,key='pur_table',enable_events=True, font=main_font_normal)
        layout = [
        [sg.Text(f'Name: {dat[0]}', font=main_font_normal)],
        [sg.Text(f'Mobile Number: {dat[1]}', font=main_font_normal)],
        [sg.Text(f'Email: {dat[2]}', font=main_font_normal)],
        [sg.Text(f'Total Amount Purchased: {round(dat[3],2)}', font=main_font_normal)],
        [table],
        [sg.Button('Exit',key = 'Exit', font=main_font_normal),sg.Button('Show More',disabled = True,key='show_more', font=main_font_normal)]
        ]
        win = sg.Window(f'{dat[2]}',layout)
        while True:
            event1,value = win.read()  #Extracting only event
            if event1  in ('Exit',None):
                win.close()
                break
            if event1 == 'pur_table' and value['pur_table'] != []:
                win['show_more'].update(disabled=False)
            if event1 == 'show_more' and value['pur_table'] != []:
                ind_select = value['pur_table'][0]
                inv_num = purchase_data[ind_select][0]
                date = purchase_data[ind_select][1]
                more_details(inv_num,date)
                
def more_details(invoice,date):
    cursor.execute(f"""SELECT Product_ID ,Product_Name ,Product_Brand ,Product_Size ,
            Product_Category ,Quantity_Purchased ,Product_tot_cost FROM PURCHASE
            WHERE Invoice_Number = '{invoice}'""")
    specific_info = cursor.fetchall()
    heading = ['Product_ID' ,'Product_Name' ,'Product_Brand' ,'Product_Size' ,
            'Product_Category' ,'Quantity_Purchased' ,'Product_tot_cost']
    table = sg.Table(headings=heading,values = specific_info, font=main_font_normal)
    layout = [[sg.Text(f'INVOICE NUMBER: {invoice}', font=main_font_normal)],[sg.Text(f'DATE OF PURCHASE: {date}', font=main_font_normal)],
    [table]]
    prod_win = sg.Window(title = 'More Information', layout=layout)
    while True:
        event,value = prod_win.read()
        if event is None:
            break
    
    
def daily_profit(days,date):
    """This function plots daily profit"""
    cursor.execute(f""" SELECT PURCHASE_DATE,SUM(PURCHASE_PROFIT) FROM PURCHASE
    WHERE PURCHASE_DATE BETWEEN DATE_SUB('{date}', INTERVAL {str(int(days)-1)} DAY) AND '{date}'
    GROUP BY PURCHASE_DATE""")
    prof_day = cursor.fetchall()
    if prof_day:
        dates = [prof_day[i][0] for i in range(len(prof_day))] #Extracting dates from sql db
        amt = [prof_day[i][1] for i in range(len(prof_day))] #Extracting daily profit from sql db
        plt.plot_date(dates,amt,linestyle='--',marker = '8')
        plt.gcf().autofmt_xdate()
        date_format = mpl_dates.DateFormatter('%b, %d %Y')
        plt.gca().xaxis.set_major_formatter(date_format)
        plt.title(f'Daily Profit (Last {days} days)')
        plt.ylabel('Profit in rupees')
        plt.xlabel('Date')
        plt.grid(True)
        figManager = plt.get_current_fig_manager()
        figManager.window.state('zoomed') #For opening window in maximised screen
        plt.show()
    else:
        sg.popup('NO DATA FOUND', font=main_font_normal)

def monthly(year1,year2):
    """This function plots monthly sale"""
    cursor.execute(f"""select DATE_FORMAT(purchase_date ,'%M'), sum(PURCHASE_PROFIT)
     FROM PURCHASE WHERE YEAR(PURCHASE_DATE) = {year1}
     GROUP BY YEAR(PURCHASE_DATE), MONTH(PURCHASE_DATE);""")
    year_1data = cursor.fetchall()
    x_axis = np.arange(12)
    prof1 = {'January':0,'February':0,'March':0,'April':0,'May':0,
            'June':0,'July':0,'August':0,'September':0,'October':0,
            'November':0,'December':0}
    months = list(prof1)
    prof2 = prof1.copy()
    prof1.update(year_1data)
    profit_1 = []
    for key in prof1:
        profit_1.append(prof1[key])
    width = 0.4
    plt.bar(x_axis,profit_1,width=width,label = year1)
    
    cursor.execute(f"""select DATE_FORMAT(purchase_date ,'%M'), sum(PURCHASE_PROFIT)
     FROM PURCHASE WHERE YEAR(PURCHASE_DATE) = {year2}
     GROUP BY YEAR(PURCHASE_DATE), MONTH(PURCHASE_DATE);""")
    year_2data = cursor.fetchall()
    prof2.update(year_2data)
    profit2 = []
    for key in prof2:
        profit2.append(prof2[key])
    plt.bar(x_axis+width,profit2,width=width,label = year2)
    plt.legend()
    plt.xticks(ticks = x_axis,labels=months,rotation = 45)
    plt.xlabel("Month")
    plt.ylabel("Profit")
    plt.grid(True)
    figManager = plt.get_current_fig_manager()
    figManager.window.state('zoomed') #For opening window in maximised screen
    
    plt.show()

def categ_rev_comp(year1,year2):
    y1 = min(year1,year2)
    y2 = max(year1,year2)
    cursor.execute(f"""select sum(PURCHASE_PROFIT), product_category from purchase
        where year(purchase_date) between {y1} and {y2}
        group by product_category;""")
    cat_data = cursor.fetchall()
    
    sale_data = [cat_data[i][0] for i in range(len(cat_data))]
    label = [cat_data[i][1] for i in range(len(cat_data))]
    plt.pie(sale_data,labels = label,shadow=True, autopct = '%1.1f%%',
        wedgeprops={'edgecolor':'black'})
    figManager = plt.get_current_fig_manager()
    figManager.window.state('zoomed') #For opening window in maximised screen
    plt.show()
def categ_rev_trend(year):
    cursor.execute(f"""select sum(PURCHASE_PROFIT) from purchase
    where year(purchase_date) = {year} and product_category = 'Men' 
    group by monthname(purchase_date)""")
    men = cursor.fetchall()
    men = men+[[0]]*(12-len(men))
    cursor.execute(f"""select sum(PURCHASE_PROFIT) from purchase 
    where year(purchase_date) = {year} and product_category = 'Women' 
    group by monthname(purchase_date)""")
    women = cursor.fetchall()
    women = women+[[0]]*(12-len(women))
    cursor.execute(f"""select sum(PURCHASE_PROFIT) from purchase 
    where year(purchase_date) = {year} and product_category = 'Kids' 
    group by monthname(purchase_date)""")
    kid = cursor.fetchall()
    kid = kid+[[0]]*(12-len(kid))
    x_axis = ['January','February','March','April','May','June','July','August','September','October','November','December']
    men_y = []
    women_y = []
    kid_y = []
    for i in range(12):
        men_y.append(men[i][0])
        women_y.append(women[i][0])
        kid_y.append(kid[i][0])
    plt.plot(x_axis,men_y,label = 'Men',color = 'k',linestyle = '-',marker = '.')
    plt.plot(x_axis,women_y,label ='Women',color = 'b',linestyle = '-.',marker = '.')
    plt.plot(x_axis,kid_y,label = 'Kids',color = 'm',linestyle = ':',marker = '.')
    figManager = plt.get_current_fig_manager()
    figManager.window.state('zoomed') #For opening window in maximised screen
    plt.legend()
    plt.title('Profit each Month')
    plt.xlabel('Months')
    plt.ylabel('Profit')
    plt.tight_layout()
    plt.show()

def brand_rev_comp(year1,year2):
    y1 = min(year1,year2)
    y2 = max(year1,year2)
    cursor.execute(f""" SELECT SUM(PRODUCT_TOT_COST), product_brand FROM PURCHASE
    where year(purchase_date) between {y1} and {y2}
    group by product_brand;""")
    data = cursor.fetchall()
    brand_names = [i[1] for i in data]
    sum = [i[0] for i in data]
    fig,ax = plt.subplots()
    ax.barh(brand_names,sum)
    figManager = plt.get_current_fig_manager()
    figManager.window.state('zoomed') #For opening window in maximised screen
    ax.set_xlabel('Profit in lakhs')
    ax.set_ylabel('Brand Name')
    scale = round(max(sum))//5
    plt.xticks(range(0,round(max(sum)),scale))
    cur = mplcursors.cursor(hover=mplcursors.HoverMode.Transient)
    @cur.connect("add")
    def on_add(sel):
        x, y, width, height = sel.artist[sel.target.index].get_bbox().bounds
        sel.annotation.set(text=f"{brand_names[sel.target.index]}: {width}",
                           position=(10, 0), anncoords="offset points")
        sel.annotation.xy = (x + width / 2, y + height / 2)
        sel.annotation.get_bbox_patch().set(alpha=0.8)
    #Credits to stackoverflow @JohnC for the above piece of code
    
    plt.show()
def brand_rev_trend(brand1,brand2,brand3,year):
    """This function plots brand popularity trend"""

    cursor.execute(f"""select sum(product_tot_cost) from purchase 
    where product_brand = '{brand1}' and year(purchase_date) = {year} 
    group by month(purchase_date);""")
    b1_data = cursor.fetchall()
    for i in range(len(b1_data)):
        b1_data[i] = float(b1_data[i][0])
    b1_data = b1_data+[0.0]*(12-len(b1_data))    
    cursor.execute(f"""select sum(product_tot_cost) from purchase 
    where product_brand = '{brand2}' and year(purchase_date) = {year} 
    group by month(purchase_date);""")
    b2_data = cursor.fetchall()
    for i in range(len(b2_data)):
        b2_data[i] = float(b2_data[i][0])
    b2_data = b2_data+[0.0]*(12-len(b2_data))
    cursor.execute(f"""select sum(product_tot_cost) from purchase 
    where product_brand = '{brand3}' and year(purchase_date) = {year} 
    group by month(purchase_date);""")
    b3_data = cursor.fetchall()
    
    for i in range(len(b3_data)):
        b3_data[i] = float(b3_data[i][0])
    b3_data = b3_data+[0.0]*(12-len(b3_data))

    month = ['January','February','March','April','May','June','July','August','September','October','November','December']
    plt.plot(month,b1_data,label = brand1,color = 'k',linestyle = '-',marker = '.')
    plt.plot(month,b2_data,label = brand2,color = 'r',linestyle = '-.',marker = '8')
    plt.plot(month,b3_data,label = brand3,color = 'c',linestyle = '--',marker = '.')
    plt.legend()
    plt.title('Trend of Brands')
    plt.xlabel('Months')
    plt.ylabel('Profit')
    figManager = plt.get_current_fig_manager()
    figManager.window.state('zoomed') #For opening window in maximised screen
    plt.tight_layout()
    plt.show()
    

if __name__=='__main__':
    main()
mycon.commit()
