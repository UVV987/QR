from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import Clock
from requests import get, post


Window.size = (360, 480)
Window.clearcolor = (0, .17, .55, 1)


notice_list = []
try:
    with open('f.txt', 'r') as f:
        file = f.readlines()
        department = file[0].replace('\n', '')
        otk = file[1].replace('\n', '')
except:
    department = None
    otk = None

buttons = """
        Button:
            id: back
            text: 'ВОЗВРАЩЕНИЕ ЗАКАЗА НА ДОРАБОТКУ'
            background_color: 0, .12, .52, 1
            on_press: root.server('back', False)
""" if otk == "otk" or otk == None else ''

Builder.load_string(f"""
<MenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 5, 5
        spacing: 5

        Button:
            text: 'УВЕДОМЛЕНИЯ'
            background_color: 0, .12, .52, 1
            on_press: root.clear()
            Image:
                source: 'bell-ring.png'
                id: bell
                opacity: 0
                size_hint: None, None
                size: 30, 30
                center_x: 330
                center_y: 450
        Button:
            text: 'ЗАКАЗЫ В РАБОТЕ'
            background_color: 0, .12, .52, 1
            on_press: root.manager.current = 'foto'
        Button:
            text: 'СКАНИРОВАНИЕ QR'
            background_color: 0, .12, .52, 1
            on_press: root.manager.current = 'scan'

<AllScreen>:
    BoxLayout:
        orientation: 'vertical'
        Button:
            text: 'KM'
            background_color: 0, .12, .52, 1
            on_press: root.save('km')
        Button:
            text: 'KMД'
            background_color: 0, .12, .52, 1
            on_press: root.save('kmd')
        Button:
            text: 'ТМЦ'
            background_color: 0, .12, .52, 1
            on_press: root.save('tmc')
        Button:
            text: 'ЗАГОТОВКА'
            background_color: 0, .12, .52, 1
            on_press: root.save('zagatovka')
        Button:
            text: 'СБОРКА'
            background_color: 0, .12, .52, 1
            on_press: root.save('sborka')
        Button:
            text: 'СВАРКА'
            background_color: 0, .12, .52, 1
            on_press: root.save('svarka')
        Button:
            text: 'УПАКОВКА'
            background_color: 0, .12, .52, 1
            on_press: root.save('upakovka')

<All2Screen>:
    BoxLayout:
        orientation: 'vertical'
        Button:
            text: 'Производство'
            background_color: 0, .12, .52, 1
            on_press: root.save('not_otk')
        Button:
            text: 'ОТК'
            background_color: 0, .12, .52, 1
            on_press: root.save('otk')

<FotoScreen>:
    BoxLayout:
        orientation: 'vertical'
        Button:
            background_color: (0, .17, .55, 1)
            on_press: root.manager.current = 'menu'
            Image:
                source: 'demo_01.png'
                size: self.parent.size

<ScanScreen>:
    BoxLayout:
    #:import ZBarCam kivy_garden.zbarcam.ZBarCam
        id: box
        orientation: 'vertical'
        padding: 5, 5
        spacing: 5
        ZBarCam:
            id: qrcodecam
        Label:
            size_hint: None, None
            size: self.texture_size[0], 50
            id: qr_text
            text: ' '

        Button:
            text: 'РАБОТА НАЧАТА'
            background_color: 0, .12, .52, 1
            on_press: root.server('start', True)
        Button:
            text: 'РАБОТА ПРИОСТАНОВЛЕНА/ВОЗОБНОВЛЕНА'
            background_color: 0, .12, .52, 1
            on_press: root.server('stop', True)
        Button:
            text: 'ОБРАТНО В МЕНЮ'
            background_color: 0, .12, .52, 1
            on_press: root.manager.current = 'menu'
        Button:
            text: 'ОТСКАНИРОВАТЬ'
            background_color: 0, .12, .52, 1
            on_press: root.get_qr()
        Button:
            text: 'РАБОТА ЗАКОНЧЕНА'
            background_color: 0, .12, .52, 1
            on_press: root.server('end', True)
""" + buttons)


class MenuScreen(Screen):
    def clear(self):
        global notice_list
        notice_list.clear()


class AllScreen(Screen):
    def save(self, select):
        global department
        department = select

        with open('f.txt', 'w') as f:
            f.write(f'{department}\n')

        App.get_running_app().root.current = 'select_otk'

class All2Screen(Screen):
    def save(self, select):
        global otk
        otk = select

        with open('f.txt', 'a') as f:
            f.write(f'{otk}\n')

        if otk != 'otk':
            scan_screen = App.get_running_app().root.get_screen('scan')

            scan_screen.ids['box'].remove_widget(scan_screen.ids['back'])

        App.get_running_app().root.current = 'menu'

class FotoScreen(Screen):
    pass

class ScanScreen(Screen):
    def server(self, command, check_otk):
        r = get(f'http://127.0.0.1:8000/api/give_csrf')
        csrf = r.text.split('=')[-1][1:-2]
        cookies = r.cookies.get_dict()

        add = ''
        if check_otk and otk == 'otk':
            add = '_otk'

        post(f'http://127.0.0.1:8000/api/{command}{add}/{department}',
             data = {'id': self.ids['qr_text'].text.split('\n')[0], 'csrfmiddlewaretoken': csrf},
             cookies = cookies)

        self.ids['qr_text'].text = ''

    def get_qr(self):
        qr = ''.join([symbol.data.decode('utf-8') for symbol in self.ids['qrcodecam'].symbols])

        self.ids['qr_text'].text = qr


def get_notice(_):
    for i in get(f'http://127.0.0.1:8000/api/notice/{department}').text.split(','):
        if i != '':
            notice_list.append(i)

    if len(notice_list) > 0:
        App.get_running_app().root.get_screen('menu').ids['bell'].opacity = 1
    else:
        App.get_running_app().root.get_screen('menu').ids['bell'].opacity = 0


class MainApp(App):
    def build(self):
        sm = ScreenManager()

        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(ScanScreen(name='scan'))
        sm.add_widget(FotoScreen(name='foto'))
        sm.add_widget(AllScreen(name='all'))
        sm.add_widget(All2Screen(name='select_otk'))

        if department == None or department == 'None' or otk == None or otk == 'None':
            sm.current = 'all'
        else:
            sm.current = 'menu'

        return sm


if __name__=='__main__':
    Clock.schedule_interval(get_notice, 3)

    MainApp().run()
