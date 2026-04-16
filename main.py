from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import tkinter
import random
from openpyxl import Workbook
from tkinter import filedialog
from datetime import datetime
import numpy as np
import sqlite3


# Connect to SQLite database 
conn = sqlite3.connect("inventory.db")
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    item_id TEXT PRIMARY KEY,
    name TEXT,
    price REAL,
    quantity INTEGER,
    category TEXT,
    date TEXT
)
""")

conn.commit()

#Window
window=tkinter.Tk()
window.title("Inventory Management System")
window.geometry("720x640")
my_tree=ttk.Treeview(window,show='headings',height=20)
style=ttk.Style()

placeholderArray=['','','','','']



def refreshTable():
    for data in my_tree.get_children():
        my_tree.delete(data)

    cursor.execute("SELECT * FROM inventory")
    rows = cursor.fetchall()

    for row in rows:
        my_tree.insert('', 'end', values=row, tags=('orow',))

    my_tree.tag_configure('orow', background="#EEEEEE")

def saveData():
    if (itemIdEntry.get() == "" or nameEntry.get() == "" or
        priceEntry.get() == "" or qntEntry.get() == "" or
        categoryCombo.get() == ""):
        messagebox.showwarning("Warning", "All fields are required!")
        return

    try:
        cursor.execute("""
        INSERT INTO inventory VALUES (?, ?, ?, ?, ?, ?)
        """, (
            itemIdEntry.get(),
            nameEntry.get(),
            float(priceEntry.get()),
            int(qntEntry.get()),
            categoryCombo.get(),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        conn.commit()
        refreshTable()
        clearFields()

    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Item ID already exists!")

def clearFields():
    itemIdEntry.delete(0, END)
    nameEntry.delete(0, END)
    priceEntry.delete(0, END)
    qntEntry.delete(0, END)
    categoryCombo.set("")

def deleteData():
    selected = my_tree.focus()
    if not selected:
        return

    values = my_tree.item(selected, 'values')
    item_id = values[0]

    cursor.execute("DELETE FROM inventory WHERE item_id = ?", (item_id,))
    conn.commit()

    refreshTable()

def searchData():
    keyword = searchVar.get()

    if keyword == "":
        messagebox.showwarning("Warning", "Enter something to search!")
        return

    for data in my_tree.get_children():
        my_tree.delete(data)

    cursor.execute("""
        SELECT * FROM inventory
        WHERE item_id LIKE ?
        OR name LIKE ?
        OR category LIKE ?
    """, (
        f"%{keyword}%",
        f"%{keyword}%",
        f"%{keyword}%"
    ))

    rows = cursor.fetchall()

    if not rows:
        messagebox.showinfo("Result", "No matching records found!")
        return

    for row in rows:
        my_tree.insert('', 'end', values=row, tags=('orow',))

    my_tree.tag_configure('orow', background="#EEEEEE")

def resetTable():
    searchVar.set("")
    refreshTable()

def updateData():
    selected = my_tree.focus()
    if not selected:
        messagebox.showwarning("Warning", "No item selected!")
        return

    # ✅ Check empty fields
    if (nameEntry.get() == "" or priceEntry.get() == "" or
        qntEntry.get() == "" or categoryCombo.get() == ""):
        messagebox.showwarning("Warning", "Please fill all fields!")
        return

    try:
        price = float(priceEntry.get())
        quantity = int(qntEntry.get())
    except ValueError:
        messagebox.showerror("Error", "Price must be a number and Quantity must be an integer!")
        return

    old_values = my_tree.item(selected, 'values')
    old_id = old_values[0]

    cursor.execute("""
    UPDATE inventory SET
        name=?,
        price=?,
        quantity=?,
        category=?
    WHERE item_id=?
    """, (
        nameEntry.get(),
        price,
        quantity,
        categoryCombo.get(),
        old_id
    ))

    conn.commit()
    refreshTable() 

def selectData():
    selected = my_tree.focus()
    if not selected:
        messagebox.showwarning("Warning", "No item selected!")
        return

    values = my_tree.item(selected, 'values')

    # values = (item_id, name, price, quantity, category, date)

    itemIdEntry.delete(0, END)
    itemIdEntry.insert(0, values[0])

    nameEntry.delete(0, END)
    nameEntry.insert(0, values[1])

    priceEntry.delete(0, END)
    priceEntry.insert(0, values[2])

    qntEntry.delete(0, END)
    qntEntry.insert(0, values[3])

    categoryCombo.set(values[4])

def exportToExcel():
    cursor.execute("SELECT * FROM inventory")
    rows = cursor.fetchall()

    if not rows:
        messagebox.showwarning("Warning", "No data to export!")
        return

    wb = Workbook()
    ws = wb.active
    ws.title = "Inventory"

    # Headers
    headers = ["Item ID", "Name", "Price", "Quantity", "Category", "Date"]
    ws.append(headers)

    # Data rows
    for row in rows:
        ws.append(row)

    # Auto filename with timestamp
    file = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")]
    )

    if not file:
        return  # user canceled

    wb.save(file)

    messagebox.showinfo("Success", "Data exported successfully!")

def generateID():
    itemIdEntry.delete(0, END)
    itemIdEntry.insert(0, str(random.randint(1000, 9999)))

def only_numbers(char):
    return char.isdigit() or char == ""

def only_float(char):
    return char.isdigit() or char == "." or char == ""


def openPOS():
    posWindow = Toplevel(window)
    posWindow.title("Point of Sale")
    posWindow.geometry("350x200")
    posWindow.resizable(False,False)

    # Variables
    selectedItem = StringVar()
    quantityVar = StringVar()

    posframe=tkinter.Frame(posWindow, bg="#02577A")
    posframe.pack()

    manageFrame=tkinter.LabelFrame(posframe, text="Point of Sales", borderwidth=5)
    manageFrame.grid(row=0, column=0, sticky="nsew", padx=[10,200], pady=20, ipadx=[6])
    # Dropdown for items
    cursor.execute("SELECT item_id, name FROM inventory")
    items = cursor.fetchall()

    itemList = [f"{i[0]} - {i[1]}" for i in items]

    productLabel=Label(manageFrame,text="PRODUCT",anchor="e",width=10)
    productLabel.grid(row=0,column=0,padx=5,pady=5)
    itemCombo = ttk.Combobox(manageFrame, values=itemList, width=32)
    itemCombo.grid(row=0, column=1, padx=3, pady=10)

    qntLabel=Label(manageFrame,text="QUANTITY",anchor="e",width=10)
    qntLabel.grid(row=1,column=0,padx=5,pady=5)
    qtyEntry = Entry(manageFrame, width=35, textvariable=quantityVar)
    qtyEntry.grid(row=1, column=1,padx=5,pady=5)

    # Buttons
    sellBtn = Button(manageFrame, text="SELL", bg="red", fg="white",
                     command=lambda: sellItem(itemCombo.get(), quantityVar.get()))
    sellBtn.grid(row=2, column=1, pady=10)

def sellItem(item, qty):
    if item == "" or qty == "":
        messagebox.showwarning("Warning", "Fill all fields!")
        return

    try:
        qty = int(qty)
    except:
        messagebox.showerror("Error", "Quantity must be a number!")
        return

    item_id = item.split(" - ")[0]

    cursor.execute("SELECT quantity FROM inventory WHERE item_id=?", (item_id,))
    result = cursor.fetchone()

    if result is None:
        return

    current_qty = result[0]

    if qty > current_qty:
        messagebox.showerror("Error", "Not enough stock!")
        return

    new_qty = current_qty - qty

    cursor.execute("UPDATE inventory SET quantity=? WHERE item_id=?",
                   (new_qty, item_id))
    conn.commit()

    messagebox.showinfo("Success", "Item sold!")
    refreshTable()

vcmd_int = (window.register(only_numbers), '%P')
vcmd_float = (window.register(only_float), '%P')



frame=tkinter.Frame(window, bg="#02577A")
frame.pack()

btnColor="#196E78"

searchFrame = tkinter.LabelFrame(frame, text="Search", borderwidth=5)
searchFrame.grid(row=2, column=0, sticky="w", padx=[10,200], pady=10, ipadx=[6])
searchVar = tkinter.StringVar()

searchEntry = Entry(searchFrame, width=40, textvariable=searchVar)
searchEntry.grid(row=0, column=0, padx=5, pady=5)

searchBtn = Button(
    searchFrame,
    text="SEARCH",
    width=10,
    bg=btnColor,
    fg="white"
)
resetBtn = Button(
    searchFrame,
    text="RESET",
    width=10,
    bg=btnColor,
    fg="white",
    command=resetTable
)
searchBtn.grid(row=0, column=1, padx=5, pady=5)
resetBtn.grid(row=0, column=2, padx=5, pady=5)

manageFrame=tkinter.LabelFrame(frame, text="Manage", borderwidth=5)
manageFrame.grid(row=0, column=0, sticky="w", padx=[10,200], pady=20, ipadx=[6])

saveBtn=Button(
    manageFrame, 
    text="SAVE",
    width=10,
    borderwidth=3,
    bg=btnColor,
    fg='white'
)

updateBtn=Button(
    manageFrame, 
    text="UPDATE",
    width=10,
    borderwidth=3,
    bg=btnColor,
    fg='white'
)

deleteBtn=Button(
    manageFrame, 
    text="DELETE",
    width=10,
    borderwidth=3,
    bg=btnColor,
    fg='white'
)

selectBtn=Button(
    manageFrame, 
    text="SELECT",
    width=10,
    borderwidth=3,
    bg=btnColor,
    fg='white'
)

clearBtn=Button(
    manageFrame, 
    text="CLEAR",
    width=10,
    borderwidth=3,
    bg=btnColor,
    fg='white'
)

exportBtn=Button(
    manageFrame, 
    text="EXPORT EXCEL",
    width=15,
    borderwidth=3,
    bg=btnColor,
    fg='white'
)

posBtn = Button(
    manageFrame,
    text="OPEN POS",
    width=12,
    borderwidth=3,
    bg="orange",
    fg="white",
    command=openPOS
)


#Button grid
saveBtn.grid(row=0,column=0,padx=5,pady=5)
updateBtn.grid(row=0,column=1,padx=5,pady=5)
deleteBtn.grid(row=0,column=2,padx=5,pady=5)
selectBtn.grid(row=0,column=3,padx=5,pady=5)
clearBtn.grid(row=0,column=5,padx=5,pady=5)
exportBtn.grid(row=0,column=6,padx=5,pady=5)
posBtn.grid(row=0, column=7, pady=10)

#Button connection/config
saveBtn.config(command=saveData)
updateBtn.config(command=updateData)
deleteBtn.config(command=deleteData)
selectBtn.config(command=selectData)
clearBtn.config(command=clearFields)
exportBtn.config(command=exportToExcel)
searchBtn.config(command=searchData)

#The Entry Frame/Table
entriesFrame=tkinter.LabelFrame(frame, text="Form", borderwidth=5)
entriesFrame.grid(row=1, column=0, sticky="w", padx=[10,200], pady=[0,20], ipadx=[6])

#Item Labels
itemIdLabel=Label(entriesFrame,text="ITEM ID",anchor="e",width=10)
nameLabel=Label(entriesFrame,text="NAME",anchor="e",width=10)
priceLabel=Label(entriesFrame,text="PRICE",anchor="e",width=10)
qntLabel=Label(entriesFrame,text="QNT",anchor="e",width=10)
categoryLabel=Label(entriesFrame,text="CATEGORY",anchor="e",width=10)

#Label grids
itemIdLabel.grid(row=0,column=0,padx=10)
nameLabel.grid(row=1,column=0,padx=10)
priceLabel.grid(row=2,column=0,padx=10)
qntLabel.grid(row=3,column=0,padx=10)
categoryLabel.grid(row=4,column=0,padx=10)

categoryArray=['Chips','Fruits','Vegetable','Canned Goods', ]

#Entry Fields
itemIdEntry=Entry(entriesFrame,width=50,textvariable=placeholderArray[0])
nameEntry=Entry(entriesFrame,width=50,textvariable=placeholderArray[1])
priceEntry=Entry(entriesFrame,width=50,textvariable=placeholderArray[2])
qntEntry=Entry(entriesFrame,width=50,textvariable=placeholderArray[3])
categoryCombo=ttk.Combobox(entriesFrame,width=47,textvariable=placeholderArray[4],values=categoryArray)

#Entry grids
itemIdEntry.grid(row=0,column=2,padx=5,pady=5)
nameEntry.grid(row=1,column=2,padx=5,pady=5)
priceEntry.grid(row=2,column=2,padx=5,pady=5)
qntEntry.grid(row=3,column=2,padx=5,pady=5)
categoryCombo.grid(row=4,column=2,padx=5,pady=5)

#Quantity and Price validation
qntEntry.config(validate="key", validatecommand=vcmd_int)
priceEntry.config(validate="key", validatecommand=vcmd_float)

#Random Id generator
generateIdBtn=Button(entriesFrame,text="GENERATE ID",borderwidth=3,bg=btnColor,fg='white')
generateIdBtn.grid(row=0,column=3,padx=5,pady=5)
generateIdBtn.config(command=generateID)

style.configure(window)

my_tree['columns']=("Item Id","Name","Price","Quantity","Category","Date")
my_tree.column("#0",width=0,stretch=NO)
my_tree.column("Item Id",anchor=W,width=70)
my_tree.column("Name",anchor=W,width=125)
my_tree.column("Price",anchor=W,width=125)
my_tree.column("Quantity",anchor=W,width=100)
my_tree.column("Category",anchor=W,width=150)
my_tree.column("Date",anchor=W,width=150)
my_tree.heading("Item Id",text="Item Id", anchor=W)
my_tree.heading("Name",text="Name", anchor=W)
my_tree.heading("Price",text="Price", anchor=W)
my_tree.heading("Quantity",text="Quantity", anchor=W)
my_tree.heading("Category",text="Category", anchor=W)
my_tree.heading("Date",text="Date", anchor=W)
my_tree.tag_configure('orow',background="#EEEEEE")
my_tree.pack()

refreshTable()

window.resizable(False,False)
window.mainloop()

