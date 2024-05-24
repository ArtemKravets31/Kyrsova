import os
import csv
import re

from kivy.app import App
from kivy.graphics import RoundedRectangle, Color, Rectangle
from kivy.properties import ListProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

FILE = "contacts.csv"

sm = ScreenManager()


def save_contacts(contacts):
    with open(FILE, mode='w', newline='') as file:
        fieldnames = ['Full Name', 'Address', 'Email', 'Mobile Phone', 'Home Phone']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for contact in contacts:
            writer.writerow(contact)


def load_contacts():
    contacts = []
    if os.path.exists(FILE):
        with open(FILE, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                contacts.append(row)
    return contacts


class CustomButton(Button):
    def __init__(self, **kwargs):
        super(CustomButton, self).__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        with self.canvas.before:
            Color(0.4, 0.6, 0.8, 1)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[20])

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super(BaseScreen, self).__init__(**kwargs)
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos


class RoundedBoxLayout(BoxLayout):
    background_color = ListProperty([1, 1, 1, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*self.background_color)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[20])
            self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class MainManu(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.contacts = load_contacts()
        anchor_lyout = AnchorLayout(anchor_x='center', anchor_y='top', padding='20dp')
        main_layout = BoxLayout(orientation='vertical', spacing='5dp')

        button_add_contact = CustomButton(text="Додати контакт", on_press=self.add_contact)
        button_edit_contact = CustomButton(text="Змінити контакт", on_press=self.switch_to_edit_contact)
        button_view_contacts = CustomButton(text="Продивитися контакти", on_press=self.switch_to_view_contacts)
        button_delete_contact = CustomButton(text="Видалити контакт", on_press=self.switch_to_delete_contact)
        button_search_contacts = CustomButton(text="Пошук контактів", on_press=self.switch_to_search_contacts)

        main_layout.add_widget(button_add_contact)
        main_layout.add_widget(button_edit_contact)
        main_layout.add_widget(button_view_contacts)
        main_layout.add_widget(button_delete_contact)
        main_layout.add_widget(button_search_contacts)
        anchor_lyout.add_widget(main_layout)
        self.add_widget(anchor_lyout)

    def add_contact(self, instance):
        self.fullname = TextInput(hint_text="Введіть своє ім'я", size_hint=(1, .2))
        self.adress = TextInput(hint_text="Введіть свою адресу", size_hint=(1, .2))
        self.email = TextInput(hint_text="Введіть свою пошту", size_hint=(1, .2))
        self.phone = TextInput(hint_text="Введіть свій номер телефону", size_hint=(1, .2))
        self.home_phone = TextInput(hint_text="Введіть свій номер телефону", size_hint=(1, .2))

        self.modal_box_layout = RoundedBoxLayout(orientation='vertical')
        self.view = ModalView(size_hint=(None, None), size=(600, 500))
        submit_btn = CustomButton(text='Відправити', size_hint=(.5, .2), on_press=self.submit_button)

        self.modal_box_layout.add_widget(self.fullname)
        self.modal_box_layout.add_widget(self.adress)
        self.modal_box_layout.add_widget(self.email)
        self.modal_box_layout.add_widget(self.phone)
        self.modal_box_layout.add_widget(self.home_phone)

        self.modal_box_layout.add_widget(submit_btn)
        self.view.add_widget(self.modal_box_layout)
        self.view.open()

    def validate_fullname(self, fullname):
        return len(fullname) > 0

    def validate_address(self, address):
        return len(address) > 0

    def validate_email(self, email):
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(email_regex, email) is not None

    def validate_phone(self, phone):
        # Ukrainian phone number regex
        phone_regex = r'^\+380\d{9}$'
        return re.match(phone_regex, phone) is not None

    def submit_button(self, instance):
        fullname = self.fullname.text
        address = self.adress.text
        email = self.email.text
        phone = self.phone.text
        home_phone = self.home_phone.text
        errors = []
        if not self.validate_fullname(fullname):
            errors.append("Некоректне ім'я")
        if not self.validate_address(address):
            errors.append("Некоректна адреса")
        if not self.validate_email(email):
            errors.append("Некоректна пошта")
        if not self.validate_phone(phone):
            errors.append("Некоректний мобільний телефон")
        if not self.validate_phone(home_phone):
            errors.append("Некоректний домашній телефон")

        if errors:
            self.modal_box_layout.clear_widgets()
            for error in errors:
                self.modal_box_layout.add_widget(Label(text=error, size_hint=(1, .2)))
            self.modal_box_layout.add_widget(self.fullname)
            self.modal_box_layout.add_widget(self.adress)
            self.modal_box_layout.add_widget(self.email)
            self.modal_box_layout.add_widget(self.phone)
            self.modal_box_layout.add_widget(self.home_phone)
            submit_btn = CustomButton(text='Відправити', size_hint=(.5, .3), on_press=self.submit_button)
            self.modal_box_layout.add_widget(submit_btn)
        else:
            contact = {
                'Full Name': fullname,
                'Address': address,
                'Email': email,
                'Mobile Phone': phone,
                'Home Phone': home_phone
            }
            self.contacts.append(contact)
            save_contacts(self.contacts)
            self.view.dismiss()

    def switch_to_view_contacts(self, instance):
        view_contacts_screen = sm.get_screen('view_contacts')
        view_contacts_screen.update_data()
        App.get_running_app().root.current = 'view_contacts'

    def switch_to_search_contacts(self, instance):
        search_contacts = sm.get_screen('search_contacts')
        search_contacts.update_data()
        App.get_running_app().root.current = 'search_contacts'

    def switch_to_delete_contact(self, instance):
        delete_contact = sm.get_screen('delete_contact')
        delete_contact.update_data()
        App.get_running_app().root.current = 'delete_contact'

    def switch_to_edit_contact(self, instance):
        edit_contact = sm.get_screen('edit_contact')
        edit_contact.update_data()
        App.get_running_app().root.current = 'edit_contact'


class ViewContacts(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        scroll = ScrollView(size_hint=(1, 1))

        main_layout = BoxLayout(orientation='vertical', padding='10dp', size_hint_y=None)
        main_layout.bind(minimum_height=main_layout.setter('height'))

        switch_btn_menu = CustomButton(text='Повернутися назад', on_press=self.switch_to_menu, size_hint=(.2, .1))

        contacts = MainManu().contacts
        sorted_contacts = sorted(contacts, key=lambda x: x['Full Name'])
        for contact in sorted_contacts:
            contacts_box = RoundedBoxLayout(orientation='vertical',
                                            padding='5dp', size_hint=(.8, None),
                                            height=200, background_color=[0.2, 0.2, 0.2, 1])

            name_label = Label(text=f"ПІБ: {contact['Full Name']}", size_hint_y=None, height=30)
            address_label = Label(text=f"Адреса: {contact['Address']}", size_hint_y=None, height=30)
            email_label = Label(text=f"Пошта: {contact['Email']}", size_hint_y=None, height=30)
            phone_label = Label(text=f"Номер телефону: {contact['Mobile Phone']}", size_hint_y=None, height=30)
            home_phone_label = Label(text=f"Домашній телефон: {contact['Home Phone']}", size_hint_y=None, height=30)

            contacts_box.add_widget(name_label)
            contacts_box.add_widget(address_label)
            contacts_box.add_widget(email_label)
            contacts_box.add_widget(phone_label)
            contacts_box.add_widget(home_phone_label)

            main_layout.add_widget(contacts_box)
        scroll.add_widget(main_layout)
        self.add_widget(scroll)
        self.add_widget(switch_btn_menu)

    def update_data(self):
        self.clear_widgets()
        self.__init__()

    def switch_to_menu(self, instance):
        App.get_running_app().root.current = 'menu'


class SearchContacts(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.contacts = load_contacts()

        main_layout = BoxLayout(orientation='vertical')
        btn_box = BoxLayout(spacing='5dp', padding='5dp')
        self.search_input = TextInput(hint_text="Введіть ім'я або номер телефону для пошуку", size_hint=(1, .2))
        search_button = CustomButton(text="Пошук", size_hint=(1, .2), on_press=self.search_contacts)
        self.results_layout = BoxLayout(orientation='vertical', padding='5dp')
        switch_btn_menu = CustomButton(text='Повернутися назад', on_press=self.switch_to_menu, size_hint=(1, .2))

        main_layout.add_widget(self.search_input)
        main_layout.add_widget(self.results_layout)
        btn_box.add_widget(switch_btn_menu)
        btn_box.add_widget(search_button)
        main_layout.add_widget(btn_box)
        self.add_widget(main_layout)

    def search_contacts(self, instance):
        query = self.search_input.text
        results = []
        for contact in self.contacts:
            if query in contact['Full Name'] or query in contact['Mobile Phone'] or query in contact['Home Phone']:
                results.append(contact)

        self.results_layout.clear_widgets()
        if results:
            for contact in results:
                contacts_box = RoundedBoxLayout(orientation='vertical', padding='5dp', size_hint=(.8, .5),
                                                background_color=[0.2, 0.2, 0.2, 1])

                name_label = Label(text=f"ПІБ: {contact['Full Name']}")
                address_label = Label(text=f"Адреса: {contact['Address']}")
                email_label = Label(text=f"Пошта: {contact['Email']}")
                phone_label = Label(text=f"Номер телефону: {contact['Mobile Phone']}")
                home_phone_label = Label(text=f"Домашній телефон: {contact['Home Phone']}")
                contacts_box.add_widget(name_label)
                contacts_box.add_widget(address_label)
                contacts_box.add_widget(email_label)
                contacts_box.add_widget(phone_label)
                contacts_box.add_widget(home_phone_label)

                self.results_layout.add_widget(contacts_box)
        else:
            self.results_layout.add_widget(Label(text="Контактів не знайдено", color=(0, 0, 0, 1)))

    def switch_to_menu(self, instance):
        App.get_running_app().root.current = 'menu'

    def update_data(self):
        self.clear_widgets()
        self.__init__()


class DeleteContact(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.contacts = load_contacts()

        main_layout = BoxLayout(orientation='vertical')
        btn_layout = BoxLayout(spacing='5dp', padding='5dp')
        self.delete_input = TextInput(hint_text="Введіть ПІБ контакту для видалення", size_hint=(1, .2))
        delete_button = CustomButton(text="Видалити", size_hint=(1, .2), on_press=self.delete_contact)
        self.results_label = Label(text='', size_hint=(1, .2), color=(0, 0, 0, 1))
        switch_btn_menu = CustomButton(text='Повернутися назад', on_press=self.switch_to_menu, size_hint=(1, .2))

        main_layout.add_widget(self.delete_input)
        main_layout.add_widget(self.results_label)
        btn_layout.add_widget(switch_btn_menu)
        btn_layout.add_widget(delete_button)
        main_layout.add_widget(btn_layout)
        self.add_widget(main_layout)

    def delete_contact(self, instance):
        name = self.delete_input.text
        found = False
        for contact in self.contacts:
            if contact['Full Name'] == name:
                self.contacts.remove(contact)
                save_contacts(self.contacts)
                self.results_label.text = "Контакт успішно видалено!"
                found = True
                break
        if not found:
            self.results_label.text = "Контакт не знайдено!"

    def switch_to_menu(self, instance):
        App.get_running_app().root.current = 'menu'

    def update_data(self):
        self.clear_widgets()
        self.__init__()


class EditContact(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.contacts = load_contacts()
        main_layout = BoxLayout(orientation='vertical')
        self.edit_input = TextInput(hint_text="Введіть ПІБ контакту для редагування", size_hint=(1, .2))
        edit_button = CustomButton(text="Редагувати", size_hint=(1, .2), on_press=self.edit_contact)
        self.results_label = Label(text='', size_hint=(1, .2), color=(0, 0, 0, 1))
        btn_layout = BoxLayout(spacing='5dp', padding='5dp')
        switch_btn_menu = CustomButton(text='Повернутися назад', on_press=self.switch_to_menu, size_hint=(1, .2))

        main_layout.add_widget(self.edit_input)
        main_layout.add_widget(self.results_label)

        btn_layout.add_widget(switch_btn_menu)
        btn_layout.add_widget(edit_button)
        main_layout.add_widget(btn_layout)
        self.add_widget(main_layout)

    def edit_contact(self, instance):
        name = self.edit_input.text
        found = False
        for contact in self.contacts:
            if contact['Full Name'] == name:
                self.results_label.text = "Контакт знайдено. Введіть нові дані."
                self.show_edit_fields(contact)
                found = True
                break
        if not found:
            self.results_label.text = "Контакт не знайдено!"

    def show_edit_fields(self, contact):
        self.clear_widgets()
        main_layout = BoxLayout(orientation='vertical')

        self.address_input = TextInput(hint_text=f"Адреса ({contact['Address']})", size_hint=(1, .2))
        self.email_input = TextInput(hint_text=f"Пошта ({contact['Email']})", size_hint=(1, .2))
        self.phone_input = TextInput(hint_text=f"Мобільний телефон ({contact['Mobile Phone']})", size_hint=(1, .2))
        self.home_phone_input = TextInput(hint_text=f"Домашній телефон ({contact['Home Phone']})", size_hint=(1, .2))

        save_button = CustomButton(text="Зберегти", size_hint=(1, .2), on_press=lambda x: self.save_edits(contact))
        switch_btn_menu = CustomButton(text='Повернутися назад', on_press=self.switch_to_menu, size_hint=(.2, .1))

        main_layout.add_widget(self.address_input)
        main_layout.add_widget(self.email_input)
        main_layout.add_widget(self.phone_input)
        main_layout.add_widget(self.home_phone_input)
        main_layout.add_widget(save_button)
        main_layout.add_widget(switch_btn_menu)
        self.add_widget(main_layout)

    def save_edits(self, contact):
        contact['Address'] = self.address_input.text if self.address_input.text else contact['Address']
        contact['Email'] = self.email_input.text if self.email_input.text else contact['Email']
        contact['Mobile Phone'] = self.phone_input.text if self.phone_input.text else contact['Mobile Phone']
        contact['Home Phone'] = self.home_phone_input.text if self.home_phone_input.text else contact['Home Phone']
        save_contacts(self.contacts)
        self.results_label.text = "Контакт успішно редаговано!"
        self.switch_to_menu(None)

    def switch_to_menu(self, instance):
        App.get_running_app().root.current = 'menu'

    def update_data(self):
        self.clear_widgets()
        self.__init__()


class MainApp(App):
    def build(self):
        sm.add_widget(MainManu(name='menu'))
        sm.add_widget(ViewContacts(name='view_contacts'))
        sm.add_widget(SearchContacts(name='search_contacts'))
        sm.add_widget(DeleteContact(name='delete_contact'))
        sm.add_widget(EditContact(name='edit_contact'))
        return sm


if __name__ == '__main__':
    MainApp().run()
