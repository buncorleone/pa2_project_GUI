import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import messagebox
import requests
import json

URL = "http://localhost:8000/"


class GUI:
    # Capture the user's authentication token and username. Username is used to display only the logged in user's posts.
    token = None
    user = ""

    # Borrowed close_window function to confirm exit.
    def close_window(self):
        if messagebox.askokcancel("Exit", "Do you really want to exit?"):
            self.parent.destroy()

    # Login window GUI
    def login_pop_up(self):
        def login(usr, pwd):
            username = usr
            password = pwd
            data = {"username": username, "password": password}
            response = requests.post(URL + "login/", data)
            self.token = response.json().get("access")
            if response.status_code == 200:
                messagebox.showinfo(title='Login success',
                                    message='Login successful.')
                self.user = usr
                login_window.destroy()
            elif response.status_code >= 400:
                messagebox.showinfo(title='Login failed',
                                    message='Login failed, please try again.')

        login_window = tk.Tk()
        login_window.title('Login')
        login_frame = ttk.Frame(login_window, padding=10)
        login_frame.grid(row=0, column=0, sticky=W + E)

        # User del_user_text and del_pass_text to remove the default text in the username and password fields.
        # Removed the need to include labels for them.
        def del_user_text(event):
            login_user.delete(0, "end")
            return None

        login_user = Entry(login_frame)
        login_user.insert(END, "Username")
        login_user.grid(row=1, column=3, sticky=E, padx=5)
        login_user.bind("<Button-1>", del_user_text)

        def del_pass_text(event):
            login_pass.delete(0, "end")
            return None

        login_pass = Entry(login_frame)
        login_pass.insert(END, "Password")
        login_pass.grid(row=1, column=4, sticky=E, padx=5, columnspan=2)
        login_pass.bind("<Button-1>", del_pass_text)

        login_button = Button(login_frame, text="Login", command=lambda: login(login_user.get(), login_pass.get()))
        login_button.grid(row=1, column=6, sticky=W + E, padx=5)

    # Logout function which closes the app and relaunches it once the user is successfully logged out.
    # This was done to ensure protected data (posts) were not visible after the user logs out.
    def logout(self):
        if self.token is None:
            messagebox.showinfo(title='Not logged in',
                                message='You are not currently logged in.')
        else:
            self.token = None
            messagebox.showinfo(title='Logout successful',
                                message='You are now logged out.')
            self.parent.destroy()
            main()

    # Function to populate the posts into body_text. Visible to any user, whether logged in or not.
    def load_posts(self):
        self.top_label.configure(text="Posts")
        self.body_text.configure(state="normal")
        self.body_text.delete('1.0', END)
        p = requests.get(f"{URL}posts/")
        p_dict = p.json()
        for i in p_dict['posts']:
            for k, v in i.items():
                self.body_text.insert(tk.INSERT, f"{k}: {v}\n")
            self.body_text.insert(tk.INSERT, f"{'-' * 80}\n")
        self.body_text.configure(state="disabled")

    # Same as above but shows only posts created by the currently logged in user.
    def load_my_posts(self, user):
        if self.token is None:
            messagebox.showinfo(title='Login required', message='Please login to show your posts.')
        else:
            self.top_label.configure(text="My Posts")
            self.body_text.configure(state="normal")
            self.body_text.delete('1.0', END)
            headers = {'Authorization': f'Bearer {self.token}'}
            p = requests.get(f"{URL}posts/", headers=headers)
            p_dict = p.json()
            for i in p_dict['posts']:
                if i['author'] == self.user:
                    for k, v in i.items():
                        self.body_text.insert(tk.INSERT, f"{k}: {v}\n")
                    self.body_text.insert(tk.INSERT, f"{'-' * 80}\n")
            self.body_text.configure(state="disabled")

    # Function to capture a new post and send a post request to save it to the DB.
    def capture_post(self):
        if self.token is None:
            messagebox.showinfo(title='Login required', message='Please login to create a post.')
        else:
            post_title = self.new_title.get()
            post_category = self.selected_cat.get()
            post_text = self.post_box.get('1.0', 'end')
            post_dict = {"title": post_title, "category": post_category, "body": post_text[0:-1]}
            headers = {'Authorization': f'Bearer {self.token}'}
            requests.post(f"{URL}posts/", post_dict, headers=headers)
            self.load_posts()

    # Function to populate the Category drop down for creating a new post.
    # Pulls the list of categories from the DB to be placed into an option box/dropdown.
    def list_categories(self):
        cat_list = []
        cl = requests.get(f"{URL}categories/")
        c_dict = cl.json()
        for j in c_dict['categories']:
            cat_list.append(j['name'])
        return cat_list

    # Loads the current category details into body_text.
    def load_categories(self):
        self.top_label.configure(text="Categories")
        self.body_text.configure(state='normal')
        self.body_text.delete('1.0', END)
        c = requests.get(f"{URL}categories/")
        c_dict = c.json()
        for j in c_dict['categories']:
            for k, v in j.items():
                self.body_text.insert(tk.INSERT, f"{k}: {v}\n")
            self.body_text.insert(tk.INSERT, f"{'-' * 80}\n")
        self.body_text.configure(state="disabled")

    # Main GUI starts here. Split into frames to allow easy separation of elements.
    def __init__(self, parent):
        self.parent = parent
        self.parent.title('Blogger')
        self.parent.protocol("WM_DELETE_WINDOW", self.close_window)

        # Top_frame starts here. Contains title and navigation buttons.
        self.top_frame = ttk.Frame(parent, padding=10)
        self.top_frame.grid(row=0, column=0, sticky=W + E)
        self.top_frame.columnconfigure(0, weight=1)

        self.top_label = Label(self.top_frame, text="Welcome to Blogger", font="bold, 18")
        self.top_label.grid(row=0, sticky=W)

        # Navigation buttons here, each connected to their respective functions defined above.
        self.login_nav_btn = Button(self.top_frame, text="Login", command=lambda: self.login_pop_up())
        self.login_nav_btn.grid(row=0, column=3, sticky=W + E)
        self.logout_nav_btn = Button(self.top_frame, text="Logout", command=lambda: self.logout())
        self.logout_nav_btn.grid(row=0, column=4, sticky=W + E, padx=5)
        self.post_nav_btn = Button(self.top_frame, text="Posts", command=lambda: self.load_posts())
        self.post_nav_btn.grid(row=0, column=5, sticky=W + E)
        self.categories_nav_btn = Button(self.top_frame, text="Categories", command=lambda: self.load_categories())
        self.categories_nav_btn.grid(row=0, column=6, sticky=W + E)
        self.profile_button = Button(self.top_frame, text="My Posts", command=lambda: self.load_my_posts(self.user))
        self.profile_button.grid(row=0, column=7, sticky=W + E)

        # Main body_frame starts here. Includes main text box.
        self.body_frame = ttk.Frame(parent, padding=10)
        self.body_frame.grid(row=2, column=0)
        self.body_text = tk.scrolledtext.ScrolledText(self.body_frame, width=80, height=20, wrap=WORD)
        self.body_text.configure(state="disabled")
        self.body_text.grid(row=2, column=0, sticky=W + E, columnspan=6)

        # Bottom_frame starts here. Contains all fields for creating a new post.
        self.bottom_frame = ttk.Frame(parent, padding=10)
        self.bottom_frame.grid(row=3, column=0, sticky=W + E)
        self.bottom_label = Label(self.bottom_frame, text="Create new post", font="bold, 12")
        self.bottom_label.grid(row=3, column=0, columnspan=4, sticky=N + S + E + W)

        # New post objects start here.
        self.new_title_label = Label(self.bottom_frame, text="Title:")
        self.new_title_label.grid(row=4, column=0, sticky=W)
        self.new_title = Entry(self.bottom_frame)
        self.new_title.grid(row=4, column=1, sticky=W + E)
        self.selected_cat = StringVar()
        self.selected_cat.set("Choose a category")
        self.new_category = OptionMenu(self.bottom_frame, self.selected_cat, *self.list_categories())
        self.new_category.grid(row=4, column=3, sticky=W + E, padx=5, pady=2)
        self.new_post_label = Label(self.bottom_frame, text="Post title:")
        self.new_post_label.grid(row=4, column=0, columnspan=2, sticky=W)
        self.post_box = scrolledtext.ScrolledText(self.bottom_frame, height=4, width=60)
        self.post_box.grid(row=6, column=0, columnspan=4, sticky=W)
        self.post_button = Button(self.bottom_frame, padx=5, pady=5, text="Post", font="bold, 14", bg="green",
                                  fg="white", width=14, height=5, command=lambda: self.capture_post())
        self.post_button.grid(row=3, column=6, sticky=E, rowspan=4)


def main():
    root = tk.Tk()
    GUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
