from random import randrange, choice # generate and place new tile
from  kivy.properties import ListProperty
chars = list('WASDRQwasdrq')
actions = ["Left", "Right", "Up", "Down"]
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout

def transpose(field):
    return [list(row) for row in zip(*field)]

def invert(field):
    return [row[::-1] for row in field]

class GameField(FloatLayout):
    def __init__(self,**kwargs):
        super(GameField,self).__init__(**kwargs)
        self.score = 0
        self.highscore = 0
        self.fieldLabels = [[None for i in range(4)] for j in range(4)]
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.instruction_label = Label(text = "Use 'WASD' to play the game.\nAnd use 'R' to reset", size_hint=(.3, .1),pos_hint={'x':0, 'y':.9})
        self.score_label = Label(text = """
        Highest Score: 0
        Current Score: 0
        """, size_hint=(.3, .1),pos_hint={'x':.66, 'y':.9})
        self.text_label = Label(text = "Enjoy the game", size_hint=(.3, .1),pos_hint={'x':.33, 'y':.9})
        self.add_widget(self.instruction_label)
        self.add_widget(self.score_label)
        self.add_widget(self.text_label)
        for i in range(4):
            for j in range(4):
                self.fieldLabels[i][j] = Button(text = "", markup=True ,font_size='30sp',background_color=[0, 1, 0, 1], size_hint=(.235, .21),pos_hint={'x':j*0.255, 'y':(3-i)*0.23})
                self.add_widget(self.fieldLabels[i][j])
        self.reset()
        self.draw()

    def reset(self):
        if self.score > self.highscore:
            self.highscore = self.score
        self.text_label.text = "Enjoy the game"
        self.score = 0
        self.field = [[0 for i in range(4)] for j in range(4)]
        self.spawn()
        self.spawn()

    def spawn(self):
        new_element = 4 if randrange(100) > 89 else 2
        (i,j) = choice([(i,j) for i in range(4) for j in range(4) if self.field[i][j] == 0])
        self.field[i][j] = new_element

    def _keyboard_closed(self):
        print('The keyboard have been closed!')
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        ch = keycode[1]
        if ch not in chars:
            return False
        ch=ch.upper()
        if ch == 'A':
            self.move('Left')
        if ch == 'W':
            self.move('Up')
        if ch == 'S':
            self.move('Down')
        if ch == 'D':
            self.move('Right')
        if ch == 'R':
            self.reset()
        if self.is_gameover():
            self.text_label.text = "Game Over! Enter 'R' to reset."
        if self.is_win():
            self.text_label.text = "Congrats! You win! Enter 'R' to reset."
        self.draw()
        return True


    def draw(self):
        for i in range(4):
            for j in range(4):
                self.fieldLabels[i][j].text = str(self.field[i][j]) if self.field[i][j] != 0 else " "
        scoreString = "Highest Score: " + str(self.highscore) +"\n"+ "Current Score:" +  str(self.score)
        self.score_label.text = scoreString

    def move(self, direction):
        def move_row_left(row):
            def tighten(row):  # squeese non-zero elements together
                new_row = [i for i in row if i != 0]
                new_row += [0 for i in range(len(row) - len(new_row))]
                return new_row

            def merge(row):
                pair = False
                new_row = []
                for i in range(len(row)):
                    if pair:
                        new_row.append(2 * row[i])
                        self.score += 2 * row[i]
                        pair = False
                    else:
                        if i + 1 < len(row) and row[i] == row[i + 1]:
                            pair = True
                            new_row.append(0)
                        else:
                            new_row.append(row[i])
                assert len(new_row) == len(row)
                return new_row

            return tighten(merge(tighten(row)))
        if self.is_win() or self.is_gameover():
            return False
        moves = {}
        moves['Left'] = lambda field: [move_row_left(row) for row in field]
        moves['Right'] = lambda field: invert(moves['Left'](invert(field)))
        moves['Up'] = lambda field: transpose(moves['Left'](transpose(field)))
        moves['Down'] = lambda field: transpose(moves['Right'](transpose(field)))

        if direction in moves:
            if self.move_is_possible(direction):
                self.field = moves[direction](self.field)
                self.spawn()
                if self.score > self.highscore:
                    self.highscore = self.score
                return True
            else:
                return False


    def is_win(self):
        return any(any(i >= 2048 for i in row) for row in self.field)


    def is_gameover(self):
        return not any(self.move_is_possible(move) for move in actions)

    def move_is_possible(self, direction):
        def row_is_left_movable(row):
            def change(i): # true if there'll be change in i-th tile
                if row[i] == 0 and row[i + 1] != 0: # Move
                    return True
                if row[i] != 0 and row[i + 1] == row[i]: # Merge
                    return True
                return False
            return any(change(i) for i in range(len(row) - 1))

        self.check = {}
        self.check['Left']  = lambda field:   any(row_is_left_movable(row) for row in field)

        self.check['Right'] = lambda field:  self.check['Left'](invert(field))

        self.check['Up']    = lambda field:  self.check['Left'](transpose(field))

        self.check['Down']  = lambda field:  self.check['Right'](transpose(field))

        if direction in self.check:
            return self.check[direction](self.field)
        else:
            return False


class app_2048(App):
    def build(self):
        return GameField()
if __name__=="__main__":
     app_2048().run()
