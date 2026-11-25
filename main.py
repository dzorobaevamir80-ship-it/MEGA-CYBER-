from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Ellipse, Line, Triangle
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.metrics import dp
import random, math

GREEN=(0,1,.35,1); DARK=(0,.16,.07,1); RED=(1,.15,.2,1)
BLUE=(0,.55,1,1); PURPLE=(.75,0,1,1); WHITE=(1,1,1,1); YELLOW=(1,.85,0,1)

class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mode="NORMAL"
        self.settings={"EASY":(180,55),"NORMAL":(300,35),"HARD":(480,20)}
        self.state="menu"
        self.score=0; self.hp=100; self.boss=None; self.boss_hp=150
        self.enemies=[]; self.bullets=[]; self.ebullets=[]
        self.spawn=0; self.fire=0; self.boss_fire=0; self.next_boss=100
        self.joy=(0,0); self.joy_active=False; self.last_dt=1/60
        self.bind(size=self.redraw, pos=self.redraw)
        Clock.schedule_interval(self.update, 1/60)

    def reset(self):
        self.score=0; self.hp=100; self.boss=None; self.boss_hp=150
        self.enemies=[]; self.bullets=[]; self.ebullets=[]
        self.spawn=0; self.fire=0; self.boss_fire=0; self.next_boss=100
        self.joy=(0,0); self.joy_active=False; self.state="playing"
        self.redraw()

    def on_touch_down(self,t):
        if self.state=="menu":
            y=t.y/self.height
            button_h=dp(54)/max(1,self.height)
            if .53 <= y <= .53+button_h: self.mode="EASY"
            elif .41 <= y <= .41+button_h: self.mode="NORMAL"
            elif .29 <= y <= .29+button_h: self.mode="HARD"
            elif .14 <= y <= .14+button_h: self.reset()
            self.redraw(); return True
        if self.state=="gameover":
            self.state="menu"; self.redraw(); return True
        if self.state=="playing" and t.x < self.width*.75 and t.y < self.height*.48:
            self.joy_active=True; self.move_joy(t); return True
        return True

    def on_touch_move(self,t):
        if self.joy_active: self.move_joy(t); return True
        return super().on_touch_move(t)

    def on_touch_up(self,t):
        if self.joy_active:
            self.joy_active=False; self.joy=(0,0); return True
        return super().on_touch_up(t)

    def move_joy(self,t):
        cx=self.width/2; cy=dp(105); dx=t.x-cx; dy=t.y-cy
        d=math.hypot(dx,dy); r=dp(75)
        if d>r: dx*=r/d; dy*=r/d
        self.joy=(dx/r,dy/r)

    def update(self,dt):
        if self.state!="playing": return
        self.last_dt=dt; w=self.width; h=self.height
        self.fire+=dt; self.spawn+=dt*60
        dx,dy=self.joy
        self.px=max(dp(22),min(w-dp(22),getattr(self,"px",w/2)+dx*dp(5)))
        self.py=max(dp(22),min(h-dp(22),getattr(self,"py",h*.55)+dy*dp(5)))
        if self.fire>.22:
            self.fire=0
            for a in (-.22,0,.22):
                self.bullets.append([self.px,self.py+dp(20),math.sin(a)*dp(12),math.cos(a)*dp(12)])
        speed, interval=self.settings[self.mode]
        if self.spawn>interval:
            self.spawn=0; self.enemies.append([random.uniform(dp(18),w-dp(18)),h+dp(20)])
        for b in self.bullets[:]:
            b[0]+=b[2]; b[1]+=b[3]
            if b[1]>h+dp(20): self.bullets.remove(b); continue
            hit=False
            for e in self.enemies[:]:
                if abs(b[0]-e[0])<dp(22) and abs(b[1]-e[1])<dp(22):
                    self.enemies.remove(e); self.score+=10; hit=True; break
            if hit:
                if b in self.bullets:self.bullets.remove(b)
            elif self.boss and abs(b[0]-self.boss[0])<dp(85) and abs(b[1]-self.boss[1])<dp(38):
                self.boss_hp-=2
                if b in self.bullets:self.bullets.remove(b)
                if self.boss_hp<=0:
                    self.boss=None; self.score+=150; self.hp=min(100,self.hp+20); self.next_boss+=150
        for e in self.enemies[:]:
            e[1]-=speed*dt
            if e[1]<-dp(25): self.enemies.remove(e); self.hp-=5
            elif abs(e[0]-self.px)<dp(28) and abs(e[1]-self.py)<dp(28):
                self.enemies.remove(e); self.hp-=15
        if self.score>=self.next_boss and self.boss is None:
            self.boss=[w/2,h-dp(100)]
            self.boss_hp=150
        if self.boss:
            self.boss[0]=w/2+math.sin(Clock.get_time()/300)*w*.22
            self.boss_fire+=dt
            if self.boss_fire>1.2:
                self.ebullets.append([self.boss[0],self.boss[1]-dp(35)])
                self.boss_fire=0
        for b in self.ebullets[:]:
            b[1]-=dp(7)*60*dt
            if abs(b[0]-self.px)<dp(25) and abs(b[1]-self.py)<dp(25):
                self.hp-=10; self.ebullets.remove(b)
            elif b[1]<0:self.ebullets.remove(b)
        if self.hp<=0:self.hp=0; self.state="gameover"
        self.redraw()

    def text(self, s, x, y, size=22, color=GREEN, center=False):
        lab=Label(text=s, font_size=dp(size), color=color, size_hint=(None,None),
                  size=(self.width,dp(size*1.7)), pos=(0,y))
        if center: lab.center_x=self.width/2
        else: lab.x=x
        self.add_widget(lab)

    def redraw(self,*args):
        self.canvas.clear()
        self.clear_widgets()
        w,h=self.width,self.height
        with self.canvas:
            Color(0,0,0,1); Rectangle(pos=self.pos,size=self.size)
            if self.state=="menu":
                self.text("MEGA CYBER",0,h*.78,38,GREEN,True)
                self.text("MOBILE ANDROID",0,h*.72,22,BLUE,True)
                labels=[("EASY",.53),("NORMAL",.41),("HARD",.29),("START GAME",.14)]
                for name,yy in labels:
                    selected=(name==self.mode)
                    Color(*(GREEN if selected else BLUE) if name=="START GAME" else (YELLOW if name=="NORMAL" else RED if name=="HARD" else GREEN))
                    Rectangle(pos=(w*.18,h*yy),size=(w*.64,dp(54)))
                    Color(0,0,0,1); Rectangle(pos=(w*.18+dp(3),h*yy+dp(3)),size=(w*.64-dp(6),dp(48)))
                    self.text(("▶ " if selected else "")+name,0,h*yy+dp(10),22,WHITE,True)
                self.text("TAP TO SELECT",0,h*.06,17,WHITE,True)
            elif self.state=="playing":
                for b in self.bullets:
                    Color(*GREEN); Rectangle(pos=(b[0]-dp(4),b[1]),size=(dp(8),dp(17)))
                for e in self.enemies:
                    Color(*RED); Ellipse(pos=(e[0]-dp(15),e[1]-dp(15)),size=(dp(30),dp(30)))
                for b in self.ebullets:
                    Color(*PURPLE); Ellipse(pos=(b[0]-dp(7),b[1]-dp(7)),size=(dp(14),dp(14)))
                if self.boss:
                    Color(*PURPLE); Rectangle(pos=(self.boss[0]-dp(85),self.boss[1]-dp(30)),size=(dp(170),dp(60)))
                    Color(*RED); Rectangle(pos=(w/2-dp(90),h-dp(42)),size=(dp(180),dp(8)))
                    Color(*GREEN); Rectangle(pos=(w/2-dp(90),h-dp(42)),size=(dp(180)*max(0,self.boss_hp)/150,dp(8)))
                px=getattr(self,"px",w/2); py=getattr(self,"py",h*.55)
                Color(*GREEN); Triangle(points=[px,py+dp(24),px-dp(22),py-dp(20),px,py-dp(10),px+dp(22),py-dp(20)])
                # joystick
                Color(0,.18,.08,.9); Ellipse(pos=(w/2-dp(75),dp(30)),size=(dp(150),dp(150)))
                Color(*GREEN); Line(circle=(w/2,dp(105),dp(75)),width=dp(2))
                Color(*GREEN); Ellipse(pos=(w/2+self.joy[0]*dp(55)-dp(22),dp(105)+self.joy[1]*dp(55)-dp(22)),size=(dp(44),dp(44)))
                # HUD
                Color(*RED); Rectangle(pos=(dp(70),h-dp(45)),size=(dp(180),dp(15)))
                Color(*GREEN); Rectangle(pos=(dp(70),h-dp(45)),size=(dp(180)*self.hp/100,dp(15)))
                self.text(f"SCORE: {self.score}",dp(10),h-dp(32),18,GREEN)
                self.text(f"HP: {self.hp}/100",dp(10),h-dp(65),16,WHITE)
                self.text(self.mode, w-dp(110),h-dp(35),17,BLUE)
            else:
                self.text("GAME OVER",0,h*.55,38,RED,True)
                self.text(f"SCORE: {self.score}",0,h*.46,24,GREEN,True)
                self.text("TAP TO MENU",0,h*.34,20,WHITE,True)

class CyberApp(App):
    def build(self):
        Window.clearcolor=(0,0,0,1)
        return GameWidget()

if __name__=="__main__":
    CyberApp().run()
