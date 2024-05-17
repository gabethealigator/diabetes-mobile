import matplotlib.pyplot as plt
import mysql.connector
from kivy.app import App
import pandas as pd
from kivy.core.window import Window
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.event import EventDispatcher
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.button import MDIconButton, MDRoundFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, TwoLineListItem
from kivymd.uix.textfield import MDTextField

Window.size = (338, 630)

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'diabetes'

class DatabaseManager:
    def execute_sql_file(filename, connection):
        try:
            with open(filename, 'r') as file:
                sql_commands = file.read().split(';')

                cursor = connection.cursor()

                for command in sql_commands:
                    if command.strip():
                        cursor.execute(command)

                connection.commit()

                print("Arquivo SQL executado com sucesso")

        except mysql.connector.Error as error:
            print("Falha ao ler o arquivo SQL", error)

    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
        )

        execute_sql_file('diabetes.sql', connection)

        print("Conectado ao banco de dados MYSQL")

    except mysql.connector.Error as error:
        print("Falha ao se conectar ao MYSQL", error)

    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("Conexão MYSQL fechada")

    @staticmethod
    def get_data_from_database():
        data = []
        try:
            connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )

            cursor = connection.cursor()

            cursor.execute("SELECT id_pc, nome_pc, idade, altura, peso, sexo FROM paciente")

            data = cursor.fetchall()

        except mysql.connector.Error as error:
            print("Falha ao obter dados do banco de dados", error)

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

        return data

    @staticmethod
    def get_all_patients():
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

        cursor = connection.cursor()
        cursor.execute("SELECT id_pc, nome_pc FROM paciente")
        patients = cursor.fetchall()
        connection.close()

        return patients

class CardPaciente(MDCard, EventDispatcher):
    delete_patient_event = None

    def edit_paciente(self, *kwargs):
        app = MDApp.get_running_app()
        app.root.get_screen('editpaciente').id_paciente = self.id_pc
        app.sm.current = 'editpaciente'
            
    def __init__(self, dados, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_delete_patient')
        self.orientation = "vertical"
        self.spacing = "8dp"
        self.size_hint_y = None
        self.height = "138dp"
        self.padding = [18, 0, 0, 0]
        self.md_bg_color = (51, 53, 53, 0.07)

        id_pc, nome, idade, altura, peso, sexo = dados
        self.nome = nome
        self.id_pc = id_pc

        info_text = f"Idade: {idade}\nAltura: {altura} cm\nPeso: {peso} kg\nSexo: {sexo} \nID: {id_pc}"

        box_layout = BoxLayout(orientation='horizontal', spacing=dp(8))

        text_label = MDLabel(text=f"Nome: {nome}\n{info_text}", size_hint_y=None, height=self.height)
        box_layout.add_widget(text_label)

        button_layout = BoxLayout(orientation='horizontal', size_hint_x=.5)

        delete_button = MDIconButton(icon="delete", on_release=self.delete_paciente, size_hint_y=None, height=dp(46))
        edit_button = MDIconButton(icon="pencil", on_release=self.edit_paciente, size_hint_y=None, height=dp(46))
        
        button_layout.add_widget(delete_button)
        button_layout.add_widget(edit_button)

        box_layout.add_widget(button_layout)

        self.add_widget(box_layout)

    def delete_paciente(self, *args):
        try:
            connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            cursor = connection.cursor()

            cursor.execute(f"DELETE FROM medicamento WHERE paciente_ID_PC = '{self.id_pc}'")
            connection.commit()

            cursor.execute(f"DELETE FROM paciente WHERE id_pc = '{self.id_pc}'")
            connection.commit()

            toast('Paciente deletado', duration=1) 

            self.dispatch('on_delete_patient')

        except mysql.connector.Error as error:
            print(error)
            toast("Falha ao deletar paciente", duration=1)

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def on_delete_patient(self):
        pass

class HealthScreen(Screen):
    def on_enter(self):
        layout = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=[10])

        data = DatabaseManager.get_data_from_database()

        self.ids.container.clear_widgets()

        for dados in data:
            card = CardPaciente(dados=dados)
            card.bind(on_delete_patient=self.refresh_screen)
            self.ids.container.add_widget(card)

        scroll_view = ScrollView()
        scroll_view.add_widget(layout)

    def refresh_screen(self, *args):
        data = DatabaseManager.get_data_from_database()

        self.ids.container.clear_widgets()

        for dados in data:
            card = CardPaciente(dados=dados)
            card.bind(on_delete_patient=self.refresh_screen)
            self.ids.container.add_widget(card)

class ControlScreen(Screen):
    pass

class EditPaciente(Screen):
    def on_enter(self):
        if self.id_paciente is not None:
            try:
                connection = mysql.connector.connect(
                    host=DB_HOST,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    database=DB_NAME
                )

                cursor = connection.cursor()

                cursor.execute(f"SELECT * FROM paciente WHERE id_pc = '{self.id_paciente}'")

                data = cursor.fetchone()
                connection.close()

                if data is not None:
                    self.ids.nome.text = data[1]
                    self.ids.idade.text = str(data[2])
                    self.ids.peso.text = str(data[3])
                    self.ids.altura.text = str(data[4])
                    self.ids.sexo.text = data[5]
                else:
                    toast("Paciente não encontrado", duration=1)
                    self.manager.current = "health"

            except mysql.connector.Error as error:
                print(f"Error: {error}")

    def editar_paciente(self):
        try:
            connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            cursor = connection.cursor()

            cursor.execute(f"""
                UPDATE paciente 
                SET NOME_PC = '{self.ids.nome.text}', 
                    IDADE = '{self.ids.idade.text}', 
                    PESO = '{self.ids.peso.text}', 
                    ALTURA = '{self.ids.altura.text}', 
                    SEXO = '{self.ids.sexo.text}'
                WHERE id_pc = '{self.id_paciente}'
            """)

            self.manager.current = "health"

            toast('Edições salvas', duration=1) 

            connection.commit()

        except mysql.connector.Error as error:
            toast("Falha ao editar paciente", duration=1)

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

class DiabetesGraphCard(MDCard):
    def __init__(self, treated_data, **kwargs):
        super().__init__(**kwargs)
        if isinstance(treated_data, list):
            treated_data = pd.DataFrame(treated_data, columns=['date', 'glicose'])

        self.df = treated_data

        if not self.df.empty:
            fig = plt.figure(facecolor='None')

            plt.rcParams['text.color'] = 'white'
            plt.rcParams['axes.labelcolor'] = 'white'
            plt.rcParams['xtick.color'] = 'white'
            plt.rcParams['ytick.color'] = 'white'
            plt.rcParams['axes.edgecolor'] = 'white'

            ax = fig.add_subplot(111)
            ax.set_facecolor('None')

            plt.title('Glicose x Data')
            plt.xlabel('Data')
            plt.ylabel('Glicose')

            self.df.set_index('date')['glicose'].plot(
                kind='bar', 
                color='red', 
                figsize=(10, 5), 
                rot=45, 
                fontsize=8, 
                width=0.5, 
                edgecolor='white',
                linewidth=0.5,
                ax=ax
            )
            App.get_running_app().root.get_screen('diabetes').ids.container.add_widget(FigureCanvasKivyAgg(fig))

class DiabetesScreen(Screen):
    def open_patient_dialog(self):
        self.dialog = MDDialog(
            title="Selecione um paciente",
            type="custom",
            content_cls=MDList(),
            buttons=[
                MDRoundFlatButton(
                    text="CANCELAR",
                    on_release=self.close_patient_dialog,
                )
            ],
        )

        for id_pc, nome_pc in DatabaseManager.get_all_patients():
            list_item = TwoLineListItem(
                text=nome_pc,
                secondary_text=f"ID: {id_pc}",
                on_release=self.on_patient_select
            )
            list_item.id_pc = id_pc
            self.dialog.content_cls.add_widget(list_item)

        self.dialog.open()

    def close_patient_dialog(self, *args):
        if self.dialog:
            self.dialog.dismiss()

    def on_patient_select(self, instance):
        self.ids.top_bar_diabetes.title = instance.text
        self.selected_patient_id = instance.id_pc
        self.create_card()
        self.dialog.dismiss()

    def get_data_for_plot(self):
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

        cursor = connection.cursor()
        cursor.execute(f"SELECT glicose, date FROM controle_dt WHERE paciente_id_pc = {self.selected_patient_id}")
        data = cursor.fetchall()
        connection.close()

        if data:
            df = pd.DataFrame(data, columns=['glicose', 'date'])
        else:
            df = pd.DataFrame(columns=['glicose', 'date'])

        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])

        return df

    def create_card(self):
        self.ids.container.clear_widgets()
        data = self.get_data_for_plot()

        if not data.empty:
            data['date'] = pd.to_datetime(data['date'])

        treated_data = [(item[1].strftime('%m-%d'), item[0]) for item in data.itertuples(index=False, name=None) if item[0] is not None and item[1] is not None]
        card = DiabetesGraphCard(treated_data)

class CardMed(MDCard, EventDispatcher):
    def __init__(self, dados, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = "8dp"
        self.size_hint_y = None
        self.height = "70dp"
        self.padding = [18, 0, 0, 0]
        self.md_bg_color = (51, 53, 53, 0.07)

        id_med, medicamento, dose_med = dados
        self.id_med = id_med

        info_text = f"Medicamento: {medicamento}\nDose: {dose_med} Mg"

        box_layout = BoxLayout(orientation='horizontal', spacing=dp(8))

        text_label = MDLabel(text=f"{info_text}", size_hint_y=None, height=self.height)
        box_layout.add_widget(text_label)

        delete_button = MDIconButton(icon="delete", on_release=self.delete_med, size_hint_y=None, height=dp(46))
        delete_button.pos_hint = {'center_y': 0.5}

        box_layout.add_widget(delete_button)

        self.add_widget(box_layout)

    def delete_med(self, instance):
        try:
            connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            cursor = connection.cursor()

            DatabaseManager.get_all_patients()

            cursor.execute(f"DELETE FROM medicamento WHERE id_med = {self.id_med}")

            toast('Medicamento deletado!', duration=1)

            connection.commit()

            self.parent.remove_widget(self)

        except mysql.connector.Error as error:
            toast("Falha ao deletar medicamento", duration=1)

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

class MedScreen(Screen):
    def get_data_from_meds(self):
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

        cursor = connection.cursor()
        cursor.execute(f"SELECT id_med, medicamento, dose_med FROM medicamento WHERE paciente_id_pc = '{self.selected_patient_id}'")
        meds = cursor.fetchall()
        connection.close()

        self.create_card(meds)

        return meds

    def create_card(self, meds):
        self.ids.container.clear_widgets()

        for dados in meds:
            card = CardMed(dados=dados)
            self.ids.container.add_widget(card)

    def open_patient_dialog(self):
        self.dialog = MDDialog(
            title="Selecione um paciente",
            type="custom",
            content_cls=MDList(),
            buttons=[
                MDRoundFlatButton(
                    text="CANCELAR",
                    on_release=self.close_patient_dialog,
                )
            ],
        )

        for id_pc, nome_pc in DatabaseManager.get_all_patients():
            list_item = TwoLineListItem(
                text=nome_pc,
                secondary_text=f"ID: {id_pc}",
                on_release=self.on_patient_select
            )
            list_item.id_pc = id_pc
            self.dialog.content_cls.add_widget(list_item)

        self.dialog.open()

    def close_patient_dialog(self, *args):
        if self.dialog:
            self.dialog.dismiss()

    def on_patient_select(self, instance):
        self.ids.top_bar_meds.title = instance.text
        self.selected_patient_id = instance.id_pc
        self.get_data_from_meds()
        self.dialog.dismiss()
    
    def close_add_med_dialog(self, *args):
        if self.dialog:
            self.dialog.dismiss()

    def add_med(self, *args):
        try:
            connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            cursor = connection.cursor()

            if self.med_name.text == "" or self.med_dose.text == "":
                toast('Preencha todos os campos', duration=1)
                return
            else:
                cursor.execute(f"""
                    INSERT INTO medicamento (medicamento, dose_med, paciente_id_pc) 
                    VALUES ('{self.med_name.text}', '{self.med_dose.text}', '{self.selected_patient_id}')
                """)

                toast('Medicamento Adicionado!', duration=1) 

                self.dialog.dismiss()

                self.get_data_from_meds()

                connection.commit()

        except mysql.connector.Error as error:
            print("Falha ao inserir dados no mysql", error)

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def open_add_med_dialog(self):
        self.dialog = MDDialog(
            title="Adicionar Medicamento",
            type="custom",
            content_cls=MDList(),
            buttons=[
                MDRoundFlatButton(
                    text="CANCELAR",
                    on_release=self.close_add_med_dialog,
                ),
                MDRoundFlatButton(
                    text="ADICIONAR",
                    on_release=self.add_med,
                )
            ],
        )

        self.med_name = MDTextField(hint_text="Nome do Medicamento",font_size=14)
        self.med_dose = MDTextField(hint_text="Dose do Medicamento")

        self.dialog.content_cls.add_widget(self.med_name)
        self.dialog.content_cls.add_widget(self.med_dose)

        self.dialog.open()

class AddPaciente(Screen):
    def on_pre_enter(self):
        self.ids.nome.text = ""
        self.ids.idade.text = ""
        self.ids.altura.text = ""
        self.ids.peso.text = ""
        self.ids.sexo.text = ""

class Main(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"

        self.sm = ScreenManager()

        self.sm.add_widget(ControlScreen(name='control'))
        self.sm.add_widget(AddPaciente(name='addpaciente'))
        self.sm.add_widget(HealthScreen(name='health'))
        self.sm.add_widget(DiabetesScreen(name='diabetes'))
        self.sm.add_widget(EditPaciente(name='editpaciente'))
        self.sm.add_widget(MedScreen(name='medication'))

        return self.sm

    def change_screen(self, screen_name, direction='forward'):
        if direction == 'forward':
            self.sm.transition = SlideTransition(direction='left')
        elif direction == 'backward':
            self.sm.transition = SlideTransition(direction='right')
        self.sm.current = screen_name 

    def adicionar_paciente(self, id_pc, nome, idade, sexo, controle_dt):
        try:
            connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            cursor = connection.cursor()

            cursor.execute(f"INSERT INTO controle_dt (ID_DT) VALUES ('{controle_dt}')")
            connection.commit()

            id_dt = cursor.lastrowid

            cursor.execute(f"INSERT INTO paciente (id_pc, nome_pc, idade, sexo, controle_dt_ID_DT) VALUES ('{id_pc}', '{nome}', '{idade}', '{sexo}', '{id_dt}')")
            connection.commit()

            toast('Paciente adicionado', duration=1) 
            self.change_screen('health')  

        except mysql.connector.Error as error:
            print(error)
            toast("Falha ao adicionar paciente", duration=1)

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

Main().run()