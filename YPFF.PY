import pyglet
from pyglet.gl import *
from pyglet.window import key
from pyglet.window import mouse
from math import cos, sin, acos, floor
import random
import time
import os
from loadObj1 import *
from matrix import *
import ctypes
from _thread import *
from queue import Queue
from multiprocessing import Process
# pyglet.lib.load_library('avbin')
# pyglet.have_avbin=True

w = 1280 #width and height of window,
h = 720

#data
class ProfKosbie(object): pass
data = ProfKosbie()

#openGL env
config = Config(sample_buffers = 1, samples = 4,
 depth_size = 24 , double_buffer = True)
window = pyglet.window.Window(fullscreen=False,vsync=False,resizable = False, config=config,width=w,height=h)

def init():
    data.mode = Loading()
    data.view = 40000
    data.astMod = loadModel('mod/astroid','ast.obj',False)
    data.mode = Splash()
    data.frameRate = 240
    data.dome = pyglet.image.load('res/space6.png')
    data.keys = dict()
    data.mapSize = data.view*0.9/4
    data.mapSize = 10000
    data.tgtModel = loadModel("mod/bst","2.obj")
    data.score = 0
def setup():
    glColor3f(255, 255, 255)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glDepthMask(GL_TRUE)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glFrontFace(GL_CW)
    pyglet.options['audio'] = ('openal', 'silent')
class Anime(object):
    def on_mouse_motion(self,x, y, dx, dy):
        pass
    def on_mouse_press(self,x, y, button, modifiers):
        pass
    def on_mouse_scroll(self,x, y, scroll_x, scroll_y):
        pass
    def on_mouse_drag(self,s,y,dx,dy,buttons,modifiers):
        pass
    def on_close(self):
        window.close()
    def on_key_press(self,symbol,modifier):
        pass
    def update(self,dt):
        pass
class Main(Anime):
    def __init__(self):
            #splash - subdivision loading main 'jsut use data as current' 
        self.mode = Loading()
        # Process(target = Loading().on_draw,args = ()).start()
        self.speed= 500
        self.counter = 0
        self.hitboundry = False
        self.shells = []
        self.fireTime = [0,0]
        self.fireTimeLimit = [0.3,5]
        self.astList = []
        self.zoomed = False
        self.shellTrace = False
        self.monstshellList = []
        self.lostTimer = False
        self.launchMissile = False
        self.score = 0
        self.wave = 0
        self.waveMon = [1,1,2,3,5]
        self.finished = False
        #bgm
        self.bgm = [
        pyglet.media.load('res/Megatrax - Bump and Run.mp3'),
        pyglet.media.load('res/Megatrax - We are invincible.mp3'),
        pyglet.media.load('res/Close To A Holy Place.mp3')]
        self.play(self.bgm[0])
        #soundeffect
        self.launchShellsound = pyglet.media.load('res/WOWS_GS.007.ogg',streaming = False)
        self.launchMissilesound = [pyglet.media.load('res/WOWS_GS.706.ogg',streaming = False),
        pyglet.media.load('res/WOWS_GS.074.ogg',streaming = False)]
        self.explosionSound = [
        [pyglet.media.load('res/WOWS_GS.252.ogg',streaming = False),
        pyglet.media.load('res/WOWS_GS.234.ogg',streaming = False),
        pyglet.media.load('res/WOWS_GS.730.ogg',streaming = False)],
        pyglet.media.load('res/WOWS_GS.719.ogg',streaming = False),
        pyglet.media.load('res/WOWS_GS.015.ogg',streaming = False),
        pyglet.media.load('res/WOWS_PM.037.ogg',streaming = False),
        pyglet.media.load('res/WOWS_PM.062.ogg',streaming = False),
        pyglet.media.load('res/WOWS_PM.106.ogg',streaming = False),
        pyglet.media.load('res/WOWS_PM.106.ogg',streaming = False)]
        #textures
        self.player = Player(0,500,0)
        self.shellMod = loadModel("mod/shell","shell.obj",False)
        self.mslModel = loadModel('mod/msl','msl.obj',False)
        explosion = [pyglet.image.load('res/explosion6.png'),
        pyglet.image.load('res/explosion13.png'),
        pyglet.image.load('res/explosion14.png')]
        explosion_s = [pyglet.image.ImageGrid(p, 8,8) for p in explosion]
        self.explosionSeq = []
        for l in explosion_s:
            tp = []
            for j in l:
                tp.append(j.get_texture())
            self.explosionSeq.append(tp)
        self.missileStatusText = [pyglet.image.load('res/READY.png').get_texture(),
        pyglet.image.load('res/LOADING.png').get_texture()]
        self.turnBk = pyglet.image.load('res/TURN BACK.png').get_texture()
        self.lostTex = pyglet.image.load('res/YOU LOST.png').get_texture()
        self.winTex = pyglet.image.load('res/YOU WIN.jpg').get_texture()
        self.batchList = []
        #shell model rotate
        nv = []
        for vect in self.shellMod[0]:
            nv.append(matProd(inverse([[1,0,0],[0,0,-1],[0,1,0]]),vect))
        self.shellMod = [nv] + self.shellMod[1:]
        nv = []
        for vect in self.mslModel[0]:
            nv.append(matProd(inverse([[0,0,-1],[0,1,0],[1,0,0]]),vect))
        self.mslModel = listTobatch(nv, *self.mslModel[1:])

        self.astMod = loadModel('mod/astroid','ast.obj',False)
        self.aimText = pyglet.image.load('res/aim.png').get_texture()
        self.weaponText = [#pyglet.image.load('res/lsr.jpg').get_texture(),
                        pyglet.image.load('res/shellT.jpg').get_texture(),
                        pyglet.image.load('res/missileT.jpg').get_texture()]
        self.bg = BgCube(0,0,0)
        self.boundry = Boundry()
        self.astGen()
        window.set_exclusive_mouse(True)
        self.mode = False

        self.win = False
        self.target = []
        self.targetGen(self.waveMon[self.wave])

        self.mouseExclusive = True
        self.quit = False
        self.butList=[Button(w/2-180,h/2,130,60,"MAIN MENU"),Button(w/2,h/2,130,60,"RESUME"),
                        Button(w/2+180,h/2,130,60,"QUIT"),Button(w/2,h/2+90,130,60,"RESTART")]
        self.explosionList = []
    def play(self,abstractMus):
        self.bgmplayer = pyglet.media.Player()
        self.bgmplayer.queue(abstractMus)
        self.bgmplayer.eos_action = 'loop'
        self.bgmplayer.play()
    def targetGen(self,x):
        for i in range(x):
            self.target.append(Target(
                random.randint(-data.mapSize,data.mapSize),
                random.randint(-data.mapSize,data.mapSize),
                random.randint(-data.mapSize,data.mapSize)))
    def astGen(self):
        for i in range(30):
            x,y,z,scale,angle = (random.randint(-data.mapSize,data.mapSize),
                random.randint(-data.mapSize,data.mapSize),
                random.randint(-data.mapSize,data.mapSize),
                random.randint(10,600)/10,
                [random.randint(1,360),random.randint(1,360),random.randint(1,360)])
            while (self.chkCollapse(x,y,z)):
                x,y,z = (random.randint(-data.mapSize,data.mapSize),
                random.randint(-data.mapSize,data.mapSize),
                random.randint(-data.mapSize,data.mapSize))
            self.astList.append(Astroid(x,y,z,scale,angle))
    def chkCollapse(self,x,y,z):
        for ast in self.astList:
            if ast.inside(x,y,z):
                return True
        return False
    def update(self,dt): 
    #the main function update and draw functions are long 
    #but I will comment them into clear parts

    #game status checks
        if self.quit: #if quit raised, stop update, function as pause
            return
        if self.mode:   #dispatcher left for loading screen, 
                        #not showing without multithreading,
            self.mode.update(dt)
        if not self.lostTimer: #if not in lost animetion time, do all calculations
            self.player.move(dt)
            self.player.accelerate(dt)
            if (self.launchMissile and self.fireTime[1] - self.launchMissile >= 0.2
            and self.player.target != None and self.player.target.locked):
                #launch 4 missile if missile launch switched on
                #check lockon
                self.launchMissile = self.fireTime[1]
                self.shells.append(Missile(self.player,self.player.target))
                random.choice(self.launchMissilesound).play()
                self.launchCount += 1
                if self.launchCount >= 4:
                    self.launchCount = 0
                    self.launchMissile = False
            elif self.launchMissile and self.player.target == None:#lost track
                self.launchMissile = False
        if len(self.target) == 0: #wave cleared
            self.wave += 1
            if self.wave == 3:
                self.bgmplayer.pause()
                self.play(self.bgm[1])
            elif self.wave == len(self.waveMon):
                self.bgmplayer.pause()
                self.play(self.bgm[2])
            if self.wave >= len(self.waveMon) and not self.finished :#win
            #first time
                if self.win == False:
                    self.quitSwitch()
                    self.finished = True
                    bBatch = pyglet.graphics.Batch()
                    bBatch.add(4,GL_QUADS,None,
                    ('v2f',(w/2-w/4,h/4-h/8,w/2-w/4,h/4+h/8,
                        w/2+w/4,h/4+h/8,w/2+w/4,h/4-h/8)),
                    ('t2f',(0,1,0,0,1,0,1,1)))
                    self.batchList.append(bBatch)
                self.win = True
                data.score = max(self.score,data.score)
            elif not self.finished:
                self.targetGen(self.waveMon[self.wave])

    #handle keyboard events (for keys not released)
        if data.keys[key.S]:#pitch
            self.player.sry = rad(50*dt)
        elif data.keys[key.W]:#pirch
            self.player.sry = -rad(50*dt)
        else:#don pitch
            self.player.sry = 0
        if data.keys[key.D]:#roll
            self.player.srx = rad(-80*dt)
        elif data.keys[key.A]:
            self.player.srx = rad(80*dt)
        else:
            self.player.srx = 0
        if data.keys[key.Q]:#turn
            self.player.srz = rad((-1)**(self.player.speed<-50)*30*dt)
        elif data.keys[key.E]:
            self.player.srz = rad((-1)**(self.player.speed<-50)*-30*dt)
        else:
            self.player.srz = 0

    #explosion animation update and removal
        for obji in range(len(self.explosionList)):
            self.explosionList[obji].time += dt
            if self.explosionList[obji].time >= 1.94:
                self.explosionList.pop(obji)
                return 

    #player shell and objects collision
        lengthOshell = len(self.shells)
        for obji in range(lengthOshell):#all shells
            if ( (self.shells[obji].time >= self.shells[obji].timeLimit) #time out
            or #missile target destroyed
            (type(self.shells[obji]) == Missile 
                and self.shells[obji].target not in self.target) ):
                #if last shell
                if lengthOshell == 1 or self.shells[obji] is self.shells[-1]:
                    self.shellTrace = False #turn off shell trace camera

                if type(self.shells[obji]) == Missile:#missiles explodes
                    self.explosionList.append(Explosion(self.shells[obji].dx,
                        self.shells[obji].dy,self.shells[obji].dz,150))

                self.shells.pop(obji)
                return
            else: #shells hit something
                for obj in self.astList + self.target:#all hittable objects
                    if obj.inside(self.shells[obji].dx,self.shells[obji].dy,
                        self.shells[obji].dz):
                        obj.doDamage(self.shells[obji].damage)
                        if lengthOshell == 1 or self.shells[obji] is self.shells[-1]:
                            self.shellTrace = False
                        if type(self.shells[obji]) == Missile:
                            self.explosionList.append(Explosion(self.shells[obji].dx,self.shells[obji].dy,self.shells[obji].dz,100))
                        shell = self.shells.pop(obji)
                        if type(obj) == Target:
                            self.score += sum(shell.damage)/10
                            data.score = max(self.score,data.score)
                            self.explosionSound[0][random.randint(0,2)].play()
                            return
                        else:
                            self.explosionSound[0][2].play() #play hit sounds
                            return
                self.shells[obji].turn()            
                self.shells[obji].move(dt)
                self.shells[obji].time+=dt #shell time update

    #astroid hp checks, if died, pop and explode 
        for obji in range(len(self.astList)):
            if self.astList[obji].hp[2] <= 0:
                self.explosionList.append(Explosion(self.astList[obji].dx,self.astList[obji].dy,self.astList[obji].dz,self.astList[obji].scale*63.8))
                self.astList.pop(obji)
                self.explosionSound[1].play()
                return

    #handle enemies
        for obji in range(len(self.target)):
            #shot and time
            self.target[obji].fireTime += dt
            if self.target[obji].fireTime >= 2.5:
                self.target[obji].fireTime = 0
                self.target[obji].attack()
            #die and explode
            if self.target[obji].hp[2] <= 0:
                self.explosionList.append(Explosion(self.target[obji].dx,self.target[obji].dy,self.target[obji].dz,450))
                self.score += 1000
                data.score = max(data.score,self.score)
                self.target.pop(obji)
                self.explosionSound[2].play()
                return

    #handle enemies shells
        for obji in range(len(self.monstshellList)):
            if self.monstshellList[obji].time >= 2.5:
                self.monstshellList.pop(obji)
                return 
            else:
                for obj in self.astList + [self.player]:
                    if obj.inside(self.monstshellList[obji].dx,
                        self.monstshellList[obji].dy,
                        self.monstshellList[obji].dz):
                        obj.doDamage(self.monstshellList[obji].damage)
                        if type(obj) == Player:
                            self.explosionSound[random.randint(3,6)].play()
                        self.monstshellList.pop(obji)
                        return

    #check player death
        if self.player.hp[2] <= 0: #player died
            if self.lostTimer:#finissh the animetion
                self.lostTimer += dt
            else:#first time
                self.explosionList.append(Explosion(self.player.dx,self.player.dy,self.player.dz,size = 800))
                self.lostTimer = 0.1
                self.zoomed = False
            if self.lostTimer >= 2:#animation done, display
                self.butList.pop(1)
                bBatch = pyglet.graphics.Batch()
                bBatch.add(4,GL_QUADS,None,
                ('v2f',(w/2-w/4,h/4-h/8,w/2-w/4,h/4+h/8,
                    w/2+w/4,h/4+h/8,w/2+w/4,h/4-h/8)),
                ('t2f',(0,1,0,0,1,0,1,1)))
                self.batchList.append(bBatch)
                # self.butList.append(BillBoard(w/2,h/4,w/2,h/4,'YOU LOST',color = [[255,255,255],[180,180,180]]))#same color as quit background
                # 
                self.quitSwitch()

    #update weapon CD (loading time)
        self.fireTime = [x+dt for x in self.fireTime]
        for obj in self.monstshellList:
            obj.move(dt)
            obj.time+=dt

    #handle missile locking event
        locked = False
        for obj in self.target:#iterate
            obj.smartMove() 
            obj.move(dt)
            if (locked or 
                (self.player.target != None and obj is not self.player.target)
                or self.player.weaponMode != 1): #only lock in missile mode:
                                            # or already have one target
                obj.lockOnTimer = False
                obj.locked = False
            else:
                #player sight target angle
                camePo = [self.player.dx,self.player.dy,self.player.dz]
                cameDi = self.player.cameraDire()
                cameCord = cameDi[:2]+[constProd(-1,cameDi[2])]
                tgtPo = [obj.dx,obj.dy,obj.dz]
                tgtVe = vAdd(tgtPo,camePo,False)
                dtprd = dotProd(cameCord[2],tgtVe)
                angle = acos(dtprd / leng(cameCord[2])/leng(tgtVe) )
                if rad(-18) <= angle <= rad(18): #winthin angle range
                    self.player.target = obj
                    obj.lockOnTimer += dt
                    locked = True
                    if obj.lockOnTimer >= 3:
                        obj.locked = True
                        locked = True #only lock one
                else: #not locked, set zero
                    obj.lockOnTimer = False
                    obj.locked = False
        if not locked: #iterated through all target, refreash player target
            self.player.target = None
    def on_draw(self):
        if self.mode:
            self.mode.draw()
            return

        # this line will return everything to polygons without textures, fun to try
        # glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        #zoom in , change projection matrix
        if self.zoomed:
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            gluPerspective(15., w / float(h), .01, float(data.view))
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()

        #draw player at the center of the screen
        if not self.zoomed and not (self.shellTrace) and not self.lostTimer:
            #player
            self.player.draw()
            glLoadIdentity()

        #rotate the bg box according to player direction
        self.player.rotateCord()

        #draw astroids
        glFrontFace(GL_CCW)
        for ast in self.astList:
            ast.draw()
        glFrontFace(GL_CW)

        #draw shells:
        for obj in self.shells  + self.monstshellList:
            obj.draw()

        #draw enemies
        for obj in self.target:
            obj.draw() #also cal screen coord

        #draw background box
        self.bg.draw()
        # if self.hitboundry:
        #     self.boundry.draw()

        #draw explosions
        for obj in self.explosionList:
            obj.draw()

        #restore matrix for UI plotting
        if self.zoomed:
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
        
        #3D UI
        glLoadIdentity()
        #angle meter
        self.player.drawMeter()

        #2d ui
        uiBatch = pyglet.graphics.Batch()
        glDisable(GL_CULL_FACE)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, w,h, 0, 0, -1.0) #plane projection
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity() #center

        #turn on transparent
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        #handle quit screen quit
        if self.quit:
            if not self.win and not self.finished:
                glEnable(self.lostTex.target)
                glBindTexture(self.lostTex.target,self.lostTex.id)
            else:
                glEnable(self.winTex.target)
                glBindTexture(self.winTex.target,self.winTex.id)
            for obj in self.batchList:
                obj.draw()
            glBindTexture(self.lostTex.target,0)
            glBindTexture(self.winTex.target,0)
            for obj in self.butList:
                obj.draw()
            glPushMatrix()
            glRotatef(180,1,0,0)
            glTranslatef(0,-h,0)
            # glBlendFunc(GL_ONE,GL_ONE)
            pyglet.text.Label("High Score: %d \n Current Score: %d"%(data.score,self.score),
                font_size = 10, x = 40, y =h-40).draw()
            # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glPopMatrix()
            pyglet.graphics.draw(4,GL_QUADS,
                    ('v2f',(0,0,0,h,w,h,w,0)),
                    ('c4B',[0,128,255,40]*4))
        if not self.zoomed:
        #central sight
            pyglet.graphics.draw_indexed(8,GL_LINES,[0,1,2,3,4,5,6,7],
                ('v2f',(w/2-10,h/2,w/2-5,h/2,w/2+5,h/2,w/2+10,h/2,w/2,h/2-5,w/2,h/2-10,w/2,h/2+5,w/2,h/2+10)))

        #tgtLabels
        for obj in self.target:
            obj.drawLabel()

        #aim
        if self.zoomed:
            glEnable(self.aimText.target)
            glBindTexture(self.aimText.target,self.aimText.id)
            pyglet.graphics.draw(4,GL_QUADS,('v2f',(0,h,w,h,w,0,0,0)),
                ('t3f',(0,0,255,1,0,255,1,1,255,0,1,255)))

        #missile Stat
        if self.fireTime[1] <= self.fireTimeLimit[1]:
            i = 1
        else:
            i = 0
        # glBlendFunc(GL_ONE, GL_ONE)
        glEnable(self.missileStatusText[i].target)
        glBindTexture(self.missileStatusText[i].target,self.missileStatusText[i].id)
        pyglet.graphics.draw(4,GL_QUADS,
            ('v2f',(w/4*3+40,h-30-46.8,w/4*3+40,h-30,
                w/4*3+40+150,h-30,w/4*3+40+150,h-30-46.8)),
            ('t2f',(0,1,0,0,1,0,1,1)))
        glBindTexture(self.missileStatusText[i].target,0)
        
        #handle hit bound
        if self.hitboundry:
            i=1
            glEnable(self.turnBk.target)
            glBindTexture(self.turnBk.target,self.turnBk.id)
            pyglet.graphics.draw(4,GL_QUADS,
                ('v2f',(w/2-256/2*i,h/2-80*i/2+150,w/2-256/2*i,h/2+80*i/2+150,
                    w/2+256/2*i,h/2+80*i/2+150,w/2+256/2*i,h/2-80*i/2+150)),
                ('t2f',(0,1,0,0,1,0,1,1)))
            glBindTexture(self.turnBk.target,0)


        # circle gen
        x = 140;y = h-75
        size = 85
        vt = []
        for i in range(30):
            vt += [x+size*sin(rad(360/30*-i)),y+size*cos(rad(360/30*-i))]
        #draw meter circle
        pyglet.graphics.draw(30,GL_POLYGON,('v2f',vt),('c4B',[128,255,255,40]*30))

        #hp bar
            #shield
        pyglet.graphics.draw(4,GL_POLYGON,
            ('v2f',(w+min(-250+230/3000*(3000-self.player.hp[0]),-20),
                50+1,w-20,50+1,w-20,50+50/3-1,
                w+min(-250+23.3+230/3000*(3000-self.player.hp[0]),-20),50+50/3-1)),
            ("c4B",(0,128,255,150,0,128,255,150,0,128,255,150,0,128,255,150)))
            #armor
        pyglet.graphics.draw(4,GL_POLYGON,
            ('v2f',(w+min(-250+23.3+206.7/3000*(3000-self.player.hp[1]),-20),
                50+50/3+1,w-20,50+50/3+1,w-20,50+50/3*2-1,
                w+min(-250+23.3*2+206.7/3000*(3000-self.player.hp[1]),-20),50+50/3*2-1)),
            ("c4B",[255,255,128,150]*4))    
            #structure
        pyglet.graphics.draw(4,GL_POLYGON,
            ('v2f',(w+min(-250+23.3*2+183.4/3000*(3000-self.player.hp[2]),-20),
                50+50/3*2+1,w-20,50+50/3*2+1,w-20,100-1,
                w+min(-250+23.3*3+183.4/3000*(3000-self.player.hp[2]),-20),100-1)),
            ("c4B",(255,128,255,180,255,128,255,180,255,128,255,180,255,128,255,180)))

        #rounded polygon gen
        def rpg(x,y,w,h):
            vt = [x-w/2+5,y-h/2,x-w/2,y-h/2+5,x-w/2,y+h/2-5,x-w/2+5,y+h/2,x+w/2-5,y+h/2,
            x+w/2,y+h/2-5,x+w/2,y-h/2+5,x+w/2-5,y-h/2]
            return vt

        #speed gear
        for arg in [[w-100,h-200,60,10],[w-100,h-180,40,10],
            [w-100,h-160,20,10],[w-100,h-140,40,10],[w-100,h-120,60,10]] :
            vt = rpg(*arg)
            pyglet.graphics.draw(len(vt)//2,GL_POLYGON,('v2f',vt),('c4B',[128,128,255,150]*(len(vt)//2)))
        vt = rpg(w-100,h-160-20*self.player.gear,100,15)
        pyglet.graphics.draw(len(vt)//2,GL_POLYGON,('v2f',vt),('c4B',[128,0,255,150]*(len(vt)//2)))   

        # speed meter
        pyglet.graphics.draw(4,GL_QUADS,('v2f',(w-20,h-315*(self.player.speed+600)/1800,w-40,h-min(300,315*(self.player.speed+600)/1800),
            w-40,h-300,w-20,h-315)),
            ('c4B',(255,0,0,40,255,0,0,40,255,255,128,0,255,255,128,0)))
        pyglet.graphics.draw(4,GL_QUADS,('v2f',(w-20,h-20,w-40,h-20,
            w-40,h-300,w-20,h-315)),
            ('c3B',(128,255,255,128,255,255,255,255,128,255,255,128)))
        
        if not self.zoomed:
            #weapon bar
            glBlendFunc(GL_ONE, GL_ONE)
            for i in range(2):
                glEnable(self.weaponText[i].target)
                glBindTexture(self.weaponText[i].target,self.weaponText[i].id)
                pyglet.graphics.draw(4,GL_QUADS,
                    ('v2f',(w/4-20-40+60*i,h-70,w/4-20-40+60*i,h-30,w/4-20+60*i,h-30,w/4-20+60*i,h-70)),
                    ('t2f',(0,1,0,0,1,0,1,1)))
                glBindTexture(self.weaponText[i].target,0)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            #weapn chosen
            i = self.player.weaponMode
            pyglet.graphics.draw(4,GL_QUADS,
                    ('v2f',(w/4-20-40+60*i-3,h-70-3,w/4-20-40+60*i-3,h-30+3,w/4-20+60*i+3,h-30+3,w/4-20+60*i+3,h-70-3)),
                    ('c4B',(255,255,0,180,255,255,0,180,255,255,0,180,255,255,0,180)))

        #strings (why they are upside down?)
        glPushMatrix()
        glRotatef(180,1,0,0)
        glTranslatef(0,-h,0)
        #fps
        pyglet.text.Label("FPS = %d"%(pyglet.clock.get_fps()),
            font_size = 10, x = 20, y =h-20).draw()
        glPopMatrix()
        
        #restore 3D projection
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        #setup
        glDisable(GL_BLEND)
        glEnable(GL_CULL_FACE)
    def quitSwitch(self):
        self.quit = not self.quit
        self.mouseExclusive = not self.mouseExclusive 
        window.set_exclusive_mouse(self.mouseExclusive)
    def on_key_press(self,symbol,modifier):
        if symbol == key.DOWN:
            if self.player.gear >= -1:
                self.player.gear -= 1
        if symbol == key.UP:
            if self.player.gear <= 1:
                self.player.gear += 1
        if modifier & key.MOD_SHIFT and not self.shellTrace and not self.quit:
            self.zoomed = not self.zoomed
        if symbol == key._1:
            self.player.weaponMode = 0
        if symbol == key._2:
            self.player.weaponMode = 1
        if symbol == key.Z and not self.quit and len(self.shells) > 0:
            self.shellTrace = not self.shellTrace
            self.zoomed = False
        if symbol == pyglet.window.key.ESCAPE:
            self.quitSwitch()
            return pyglet.event.EVENT_HANDLED
        pass
    def on_mouse_motion(self,x,y,dx,dy):
        if self.quit:
            for obj in self.butList:
                if obj.inside(x,h-y):
                    obj.hoverOn = True
                else:
                    obj.hoverOn = False
            return
        if self.zoomed:
            dx /= 4
            dy /= 4
        self.player.rx += rad(dx/10)
        if  -3/ 2 <= self.player.ry + rad(dy/10) <= 3/2:
            self.player.ry += rad(dy/10)
    def on_mouse_scroll(self,x, y, scroll_x, scroll_y):
        if self.quit:
            return
        if self.player.cameraDist + 10*scroll_y >= 20:
            self.player.cameraDist += 10*scroll_y
    def on_mouse_press(self,x,y,button,modifiers):
        if self.quit:
            for obj in self.butList: #handle colicks in buttons
                if obj.inside(x,h-y):
                    if obj.capital == 'START':
                        data.mode = Main()
                    elif obj.capital == 'RESUME':
                        if self.win: self.win =False
                        self.quitSwitch()
                    elif obj.capital == 'MAIN MENU':
                        data.score = max(self.score,data.score)
                        self.quitSwitch()
                        self.bgmplayer.pause()
                        data.mode=Splash()
                        window.set_fullscreen(False)
                        window.set_exclusive_mouse(False)
                    elif obj.capital =='RESTART':
                        self.bgmplayer.pause()
                        data.score = max(self.score,data.score)
                        data.mode = Main()
                    elif obj.capital =='QUIT':
                        self.bgmplayer.pause()
                        window.close()
            return    
        if not self.shellTrace and not self.lostTimer:
            if self.player.weaponMode == 0 and self.fireTime[0] >= self.fireTimeLimit[0]: #shell
                self.shells.append(Shell(self.player))
                self.launchShellsound.play()
                self.fireTime[0] = 0
            elif (self.player.weaponMode == 1 and self.fireTime[1] >= self.fireTimeLimit[1]
                and self.player.target != None and self.player.target.locked): #missile
                self.launchMissile = 0.01
                self.launchCount = 0
                self.fireTime[1] = 0
    def on_mouse_drag(self,s,y,dx,dy,buttons,modifiers):
        if self.quit:
            return
        if self.zoomed:
            dx /= 4
            dy /= 4
        self.player.rx += rad(dx/10)
        sry = self.player.sry % (2*3.1415926)
        if  -3/ 2 <= self.player.ry + rad(dy/10) <= 3/2:
            self.player.ry += rad(dy/10)
        if not self.shellTrace and not self.lostTimer:
            if self.player.weaponMode == 0 and self.fireTime[0] >= self.fireTimeLimit[0]: #shell
                self.shells.append(Shell(self.player))
                self.launchShellsound.play()
                self.fireTime[0] = 0
            elif (self.player.weaponMode == 1 and self.fireTime[1] >= self.fireTimeLimit[1] and
            self.player.target != None and self.player.target.locked): #missile
                self.launchMissile = 0.01
                self.launchCount = 0
                self.fireTime[1] = 0
    def on_close(self):
        
        pass
        # window.set_fullscreen(False)
        # window.close()
        # return pyglet.event.EVENT_HANDLED
class Splash(Anime):
    def __init__(self):
        self.background = pyglet.image.load('res/space6.png').get_texture()
        self.c = 0
        self.astList = []
        self.astGen()
        self.butList = [Button(w/2-180,h/2+90,130,60,"CREDIT"),
        Button(w/2,h/2,130,60,"START"),
        Button(w/2,h/2+90,130,60,"INSTRUCT"), 
        Button(w/2+180,h/2+90,130,60,"QUIT")]
        self.bgm = pyglet.media.load('res/All Which Was Lost Has Now been Regained.mp3')
        self.bgmplayer = pyglet.media.Player()
        self.bgmplayer.queue(self.bgm)
        self.bgmplayer.eos_action = 'loop'
        self.bgmplayer.play()
        self.initBut = self.butList
        self.instructList = [BillBoard(w/2,h/2-20,w-391,h-230,'instructCont1', 
                                color =[ [255,255,255],[255,255,255] ]),
                            BillBoard(w/2,h/2-20,w-391,h-230,'instructCont2',
                                color = [ [255,255,255],[255,255,255] ]),
                            BillBoard(w/2,h/2-20,w-391,h-230,'instructCont3',
                                color = [ [255,255,255],[255,255,255] ]),
                            BillBoard(w/2,h/2-20,w-391,h-230,'instructCont4',
                                color = [ [255,255,255],[255,255,255] ])]
        self.instructInd = 0
    def astGen(self):
        for i in range(50):
            x,y,z,scale,angle = (random.choice([random.randint(-100,-10),random.randint(10,100)]),
                random.choice([random.randint(-100,-10),random.randint(10,100)]),
                random.randint(-1500,200),
                random.randint(1,10)/10,
                [random.randint(1,360),random.randint(1,360),random.randint(1,360)])
            self.astList.append(Astroid(x,y,z,scale,angle))
    def on_draw(self):
        glDisable(GL_CULL_FACE)
        #plain
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, w,h, 0, 0, -1.0)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        #bg
        glDisable(GL_DEPTH_TEST)
        glEnable(self.background.target)
        glBindTexture(self.background.target,self.background.id)
        pyglet.graphics.draw(4,GL_QUADS,
            ('v2f',(0,0,0,h,w,h,w,0)),
            ('t2f',[.25,.5,.25,.25,.75,.25,.75,.5]),
            )
        glBindTexture(self.background.target,0)
        glEnable(GL_DEPTH_TEST)

        #top bottom bar
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        t = 100 #transparency
        pyglet.graphics.draw(4,GL_QUADS,
            ('v2f',(5,605,0,610,w,610,w-5,605)),
            ('c4B',[27,217,206,t,27,148,217,150,27,148,217,150,27,217,206,t]),
            )

        t = 150 #transparency
        pyglet.graphics.draw(4,GL_QUADS,
            ('v2f',(0,610,0,h,w,h,w,610)),
            ('c4B',[27,217,206,t,27,148,217,t,27,148,217,t,27,217,206,t]),
            )

        pyglet.graphics.draw(4,GL_POLYGON,
            ('v2f',(w/2+40,0,w/2+40,80,w,80,w,0)),
            ('c4B',[27,148,217,t,27,217,206,t,27,217,206,t,27,148,217,t])
            )
        pyglet.graphics.draw(4,GL_POLYGON,
            ('v2f',(0,0,0,80,w/2-40,80,w/2-40,0)),
            ('c4B',[27,148,217,t,27,217,206,t,27,217,206,t,27,148,217,t])
            )
        pyglet.graphics.draw(6,GL_POLYGON,
            ('v2f',(w/2-40,0,w/2-40,80,w/2-40+8,90,w/2+40-8,90,w/2+40,80,w/2+40,0)),
            ('c4B',[27,148,217,t,27,217,206,t,
                27,217,206,t,27,217,206,t,27,217,206,t,27,148,217,t])
            )

        #draw buttons
        for obj in self.butList:
            obj.draw()

        glDisable(GL_BLEND)
        #restore 3d
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        #end of plain

        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)

        #draw astroids
        for obj in self.astList:
            obj.draw()

    def chkCollapse(self,x,y,z):
        for ast in self.astList:
            if ast.inside(x,y,z):
                return True
        return False

    def update(self,dt):
        for obj in self.astList:
            obj.dz += 10*dt
            if obj.dz >= 30:
                obj.dz = -1500
            obj.angles[0] += random.random()/4
            obj.angles[1] += random.random()/3
            obj.angles[2] += random.random()/5
        pass
    def on_mouse_motion(self,x, y, dx, dy):
        for obj in self.butList:
            if obj.inside(x,h-y):
                obj.hoverOn = True
            else:
                obj.hoverOn = False
    def on_mouse_press(self,x, y, button, modifiers):
        for obj in self.butList:
            if obj.inside(x,h-y):
                if obj.capital == 'START':
                    self.bgmplayer.pause()
                    data.mode = Main()

                    # window.set_fullscreen(True)
                elif obj.capital == 'QUIT':
                    self.bgmplayer.pause()
                    window.close()
                elif obj.capital == 'MAIN MENU':
                    self.butList = self.initBut
                    self.on_mouse_press(x, y, button, modifiers)#reset highlight
                elif obj.capital == 'CREDIT':
                    self.butList = [Button(80,h/2+120,120,50,"MAIN MENU"),
                    BillBoard(w/2,h/2-20,w-391,h-230,'creditCont')]
                elif obj.capital == 'INSTRUCT':
                    self.butList = [Button(80,h/2-60,120,50,"NEXT"),
                    Button(80,h/2+30,120,50,"PREV"),
                    Button(80,h/2+120,120,50,"MAIN MENU"),
                    self.instructList[self.instructInd]]
                elif obj.capital == 'NEXT':
                    self.instructInd += 1
                    self.instructInd %= 4
                    self.butList = [Button(80,h/2-60,120,50,"NEXT"),
                    Button(80,h/2+30,120,50,"PREV"),
                    Button(80,h/2+120,120,50,"MAIN MENU"),
                    self.instructList[self.instructInd]]
                elif obj.capital == 'PREV':
                    self.instructInd -= 1
                    self.instructInd %= 4
                    self.butList = [Button(80,h/2-60,120,50,"NEXT"),
                    Button(80,h/2+30,120,50,"PREV"),
                    Button(80,h/2+120,120,50,"MAIN MENU"),
                    self.instructList[self.instructInd]]
            else:
                obj.hoverOn = False
    def on_close(self):
        self.bgmplayer.pause()
        window.close()
        return pyglet.event.EVENT_HANDLED
class Loading(Anime):
    def __init__(self):
        self.background = pyglet.image.load('res/ld.jpg').get_texture()
        self.time = 0
    def on_draw(self):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, w,h, 0, 0, -1.0)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        #bg
        glDisable(GL_DEPTH_TEST)
        glEnable(self.background.target)
        glBindTexture(self.background.target,self.background.id)
        pyglet.graphics.draw(4,GL_QUADS,
            ('v2f',(0,0,0,h,w,h,w,0)),
            ('t2f',[0,1,0,0,1,0,1,1]),
            )
        glBindTexture(self.background.target,0)
        glEnable(GL_DEPTH_TEST)

        # hud{
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        x = w/2;y = h/2
        size = 85
        vt = []
        for i in range(30):
            vt += [x+size*sin(rad(360/30*-i)),y+size*cos(rad(360/30*-i))]
        pyglet.graphics.draw(30,GL_POLYGON,('v2f',vt),('c4B',list(map(int,[255*sin(self.time),200,255,180]*30))))
        glDisable(GL_BLEND)

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        #end of plain
    def update(self,dt):
        self.time += dt/3
        # self.time /= 225
        pass
class Moveable(object):
    def move(self,dt):
        hit = False
        nvz = self.direction[2]
        homz = constProd(-self.speed*dt,nvz)
        if type(self) == Player:
            coeff = 1
        else: coeff = 1.5
        upb = data.mapSize*coeff
        lob = -data.mapSize*coeff
        popUp = data.mapSize*coeff*0.8
        if lob< self.dx + dotProd(homz,[1,0,0]) <upb:
            self.dx += dotProd(homz,[1,0,0])
        else:
            if type(self) == Player and -popUp< self.dx + dotProd(homz,[1,0,0]) < popUp:
                hit =True
        if lob< self.dy + dotProd(homz,[0,1,0]) < upb:
            self.dy += dotProd(homz,[0,1,0])
        else:
            if type(self) == Player and -popUp< self.dx + dotProd(homz,[1,0,0]) < popUp:
                hit =True
        if lob< self.dz + dotProd(homz,[0,0,1]) < upb:
            self.dz += dotProd(homz,[0,0,1])
        else:
            if type(self) == Player and -popUp< self.dx + dotProd(homz,[1,0,0]) < popUp:
                hit =True
        data.mode.hitboundry = hit
class Hurtable(object):
    def doDamage(self,damage):
        damageBuffer = 0
        for i in range(3):
            if self.hp[i] < (damage[i] + damageBuffer):
                if i == 2: self.hp[2] = 0
                else:
                    damageBuffer += (damage[i] + damageBuffer - self.hp[i])*0.8
                    self.hp[i] = 0
            else:
                self.hp[i] -= (damage[i]+damageBuffer)
                damageBuffer = 0
class BgCube(object):
    def __init__(self,dx,dy,dz):
        self.x = dx
        self.y = dy
        self.z = dz
        self.image = data.dome
        self.batch = self.batchGen()
        self.textureGen()
    def batchGen(self):
        vertex = ((-data.view/2,data.view/2,data.view/2),
        (-data.view/2,-data.view/2,data.view/2),
        (data.view/2,-data.view/2,data.view/2),
        (data.view/2,-data.view/2,-data.view/2),
        (data.view/2,data.view/2,-data.view/2),
        (-data.view/2,data.view/2,-data.view/2),
        (data.view/2,data.view/2,data.view/2),
        (-data.view/2,-data.view/2,-data.view/2))
        bgBatch = pyglet.graphics.Batch()
        indices = [1,2,3,7,
        1,0,6,2,
        5,0,1,7,
        4,5,7,3,
        2,6,4,3,
        0,5,4,6]
        for l in range(len(indices)//4):
            vertlist = []
            if l == 0:
                textCord = [.25,.25,
                .25,0,
                .5,0,
                .5,.25]
            elif l ==1:
                textCord = [.25,.25,
                .25,.5,
                0,.5, 
                .0,.25]
            elif l ==2:
                textCord = [.5,.5,
                .25,.5,
                .25,.25,
                .5,.25]
            elif l == 3:
                textCord =[.75,.5,
                .5,.5,
                .5,.25,
                .75,.25]
            elif l ==4:
                textCord = [1,.25,
                1,.5,
                .75,.5,
                .75,.25]
            elif l==5:
                textCord = [.25,.5,
                .5,.5,
                .5,.75,
                .25,.75]
            indlist = indices[l*4:l*4+4]
            for i in indlist:
                vertlist += vertex[i]
            bgBatch.add(4,GL_QUADS,None,
                ("v3f",vertlist),
                ("t2f",textCord))
        return bgBatch
    def draw(self):
        if data.mode.shellTrace:
            try:
                dx,dy,dz = data.mode.shells[-1].dx,data.mode.shells[-1].dy,data.mode.shells[-1].dz
            except:
                dx,dy,dz = data.mode.player.dx, data.mode.player.dy, data.mode.player.dz
        else:
            dx,dy,dz = data.mode.player.dx, data.mode.player.dy, data.mode.player.dz
        glPushMatrix()
        glTranslatef(dx,dy,dz)
        glDepthMask(GL_FALSE)
        glDisable(GL_CULL_FACE)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(self.dome_tex_seq.target)
        glBindTexture(self.dome_tex_seq.target,self.dome_tex_seq.id)
        self.batch.draw()
        glBindTexture(self.dome_tex_seq.target,0)
        glEnable(GL_CULL_FACE)
        glDepthMask(GL_TRUE)
        glPopMatrix()
        glDisable(GL_BLEND)
    def textureGen(self):
        self.dome_seq = pyglet.image.ImageGrid(self.image,3,4)
        self.dome_tex_seq = self.dome_seq.get_texture()
        glEnable(self.dome_tex_seq.target)
        glBindTexture(self.dome_tex_seq.target,self.dome_tex_seq.id)
        glTexParameterf(self.dome_tex_seq.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(self.dome_tex_seq.target, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(self.dome_tex_seq.target, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(self.dome_tex_seq.target, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
class Boundry(object):
    def __init__(self):
        self.batch = self.batchGen()
    def batchGen(self):
        vertex = (-data.mapSize*2.2,data.mapSize*2.2,data.mapSize*2.2,
        -data.mapSize*2.2,-data.mapSize*2.2,data.mapSize*2.2,
        data.mapSize*2.2,-data.mapSize*2.2,data.mapSize*2.2,
        data.mapSize*2.2,-data.mapSize*2.2,-data.mapSize*2.2,
        data.mapSize*2.2,data.mapSize*2.2,-data.mapSize*2.2,
        -data.mapSize*2.2,data.mapSize*2.2,-data.mapSize*2.2,
        data.mapSize*2.2,data.mapSize*2.2,data.mapSize*2.2,
        -data.mapSize*2.2,-data.mapSize*2.2,-data.mapSize*2.2)
        bdBatch = pyglet.graphics.Batch()
        indices = [1,2,3,7,
        1,0,6,2,
        5,0,1,7,
        4,5,7,3,
        2,6,4,3,
        0,5,4,6]
        bdBatch.add_indexed(len(vertex)//3,GL_QUADS,None,indices,
                ("v3f",vertex),
                ("c4B",[128,255,255,50]*(len(vertex)//3)))
        return bdBatch
    def draw(self):
        glDisable(GL_CULL_FACE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.batch.draw()
        glDisable(GL_BLEND)
        glEnable(GL_CULL_FACE)
class Player(Moveable,Hurtable):
    def __init__(self,x,y,z):
        self.dx = x
        self.dy = y
        self.dz = z
        self.speed = 500
        self.rx = self.ry = self.rz = 0
        self.sry = self.srx = self.srz= 0
        self.cameraDist = 450
        #load player
        time1 = time.time()
        # data.player = loadModel("mod/starcruiser military","Starcruiser military.obj")
        # self.batch = loadModel("mod/starcruiser military","test3.obj")
        self.batch = loadModel("mod/bst","2.obj")
        # self.batch = loadModel("mod/strf","1.obj")
        # self.batch = loadModel('mod/Battleship Yamato','test.obj')
        # data.player = loadModel("mod/sof",'sof_.obj')
        print ('Model loaded in %d seconds' %(time.time()-time1))
        self.astCol = False
        self.astDist = 0
        self.hp = [3000,3000,3000] 
        self.direction = [[1,0,0],[0,1,0],[0,0,1]] #x,y,z
        self.gear = 0
        self.weaponMode = 0
        self.collision = False
        self.cameraPos = [0,0,0]
        self.target = None
    def inside(self,x,y,z,sphereR = 0):
        if (self.dx-x)**2+(self.dy-y)**2+(self.dz-z)**2 <= (65)**2 : return True
        else: return False
    def accelerate(self,dt):
        #800 400 0 -200 -400
        if not self.collision:
            if self.gear == 2:
                if self.speed <= 1200:
                    self.speed += 100*(1200-self.speed)/400*dt
            elif self.gear == 1:
                if self.speed >= 400:
                    self.speed -= 40*abs(400-self.speed)/200*dt
                elif self.speed <= 400:
                    self.speed += 40*abs(800-self.speed)/200*dt
            elif self.gear == 0:
                if self.speed >= 0:
                    self.speed -= 20*abs(0-self.speed)/100*dt
                elif self.speed <= 0:
                    self.speed += 20*abs(0-self.speed)/100*dt
            elif self.gear == -1:
                if self.speed >= -300:
                    self.speed -= 40*abs(-300-self.speed)/150*dt
                elif self.speed <= -300:
                    self.speed += 40*abs(-300-self.speed)/150*dt
            elif self.gear == -2:
                if self.speed >= -600:
                    self.speed -= 80*abs(-600-self.speed)/300*dt
                elif self.speed <= -600:
                    self.speed += 120*abs(-600-self.speed)/-300*dt
    def set_state(self):
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glCullFace(GL_FRONT)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
    def unset_state(self):
        glCullFace(GL_BACK)
        glDisable(GL_LIGHTING)
        glDisable(GL_LIGHT0)
    def draw(self):
        self.set_state()
        dy = self.cameraDist*sin(self.ry)
        dx = self.cameraDist*sin(self.rx)*cos(self.ry)
        dz = (self.cameraDist*cos (self.rx))*cos(self.ry)
        gluLookAt(0+dx,30-dy,0-dz,0,30,0,0.0,1.0,0.0)
        #commented for falcon
        # glPushMatrix()
        # glRotatef(180,0,1,0)
        # glScalef(30,30,30)
        self.batch.draw()
        # glPopMatrix()

        self.unset_state()
    def rotateCord(self):#return current coordinate system #== player.move()
        if data.mode.shellTrace and len(data.mode.shells)>0:
            shell = data.mode.shells[-1]
            direction = shell.direction
            pos = [shell.dx,shell.dy,shell.dz]
            up = constProd(30,direction[1])
            strt = vAdd(vAdd(pos,constProd(80,direction[2])),up)
            to = vAdd(vAdd(pos,direction[2],False),up)
            gluLookAt(*(strt+to+direction[1]))
        else:                
            sry = self.sry #pitch
            srx = self.srx #roll
            srz = self.srz #yaw
            for ast in data.mode.astList:
                if ast.inside(self.dx,self.dy,self.dz,400): #collision distance
                    if abs(self.speed) >= 30: #decelerate
                        self.speed += (-1)**(self.speed>0)*3
                    if ast.inside(self.dx,self.dy,self.dz,130): 
                        self.collision = True
                    #too close, bounce back
                        if self.speed >= -5000:
                            self.speed -= 1000000*(((
                            self.dx-ast.dx)**2+(self.dy-ast.dy)**2+(
                            self.dz-ast.dz)**2)/500)**(-1)
                        self.hp[1] -= 10
                        self.hp[0] -= 10
                        self.hp[2] -= 3
                else:
                    self.collision = False

            xcomp = sin(self.rx)*cos(self.ry)
            ycomp = sin(self.ry)
            zcomp = -cos(self.rx)*cos(self.ry)

            #MATRIX rotation (ask me math LOL)
            (vx,vy,vz) = self.direction
            nvx = mod(Ru(srx,vz,*Ru(srz,vy,*Ru(sry,vx,*vx))))
            nvy = mod(Ru(srx,vz,*Ru(srz,vy,*Ru(sry,vx,*vy))))
            nvz = mod(Ru(srx,vz,*Ru(srz,vy,*Ru(sry,vx,*vz))))
            self.direction = [nvx,nvy,nvz]
            drrx,drry,drrz = 0,0,0
            homx = constProd(xcomp,nvx)
            homy = constProd(ycomp,nvy)
            homz = constProd(zcomp,nvz)
            for vect in [homx,homy,homz]:
                drrx += dotProd(vect,[1,0,0])
                drry += dotProd(vect,[0,1,0])
                drrz += dotProd(vect,[0,0,1])
            if data.keys[key.P] : print('speed',self.speed,'hp',data.mode.player.hp)
            gluLookAt(self.dx-self.cameraDist*drrx,
            self.dy-self.cameraDist*drry,
            self.dz-self.cameraDist*drrz,
            self.dx,self.dy,self.dz,*nvy)
            self.cameraPos = [self.dx-self.cameraDist*drrx,
            self.dy-self.cameraDist*drry,
            self.dz-self.cameraDist*drrz]
            return (nvx,nvy,nvz,drrx,drry,drrz)
    def drawMeter(self):
        if data.mode.quit:
            return
        glTranslatef(-11.5,-6.5,-20)
        tv =[]
        for i in self.direction:
            for j in i:
                tv += [1.5*j]
            for j in i:
                tv += [-1.5*j]
        tv = [0,0,0] + tv + [0,-1,0]
        pyglet.graphics.draw_indexed(8,GL_LINES,[0,1,0,2,0,3,0,4,0,5,0,6,0,7],
            ('v3f',tv),
            ('c3B',[255,255,255,255,0,0,255,0,0,0,255,0,0,255,0,0,0,255,0,0,255,255,255,0]))

        # glPushMatrix()
        # glTranslatef(-8,-6.8,-20)
        # glTranslatef(1,1,-2)

        # glScalef(.03,.03,.03)
        # # glRotatef(self.srx*180/3.1415926,*self.direction[2])
        # # glRotatef(self.sry*180/3.1415926,*self.direction[0])
        # # glRotatef(self.srz*180/3.1415926,*self.direction[1])
        # rrz = acos(dotProd(self.direction[2],[0,0,1]))*180/3.1415926
        # rry = acos(dotProd(self.direction[1],[0,1,0]))*180/3.1415926
        # rrx = acos(dotProd(self.direction[0],[1,0,0]))*180/3.1415926
        # glRotatef(rrz,0,0,1)
        # glRotatef(rrx,1,0,0)
        # glRotatef(rry,0,1,0)
        # self.batch.draw()
        # pyglet.graphics.draw_indexed(6,GL_LINES,[0,1,2,3,4,5],
        #     ('v3f',[-50,0,0,50,0,0,0,-50,0,0,50,0,0,0,-50,0,0,50]),
        #     ('c3B',[255,0,0,255,0,0,0,255,0,0,255,0,0,0,255,0,0,255]))
        # glPopMatrix()
    def cameraDire(self):#return looking direction of camera1
        def rt(arg):
            return  mod(Ru(-self.rx,self.direction[1],*Ru(self.ry,self.direction[0],*arg)))
        return list(map(rt,self.direction))
class Shell(Moveable):
    def __init__(self,player):
        x,y,z,direction = player.dx,player.dy,player.dz,player.direction
        self.dx = x - 30*direction[1][0]
        self.dy = y - 30*direction[1][1]
        self.dz = z - 30*direction[1][2]
        self.speed = 8000 #3400
        self.model = data.mode.shellMod
        nv = []
        for vect in data.mode.shellMod[0]:
            nv.append(matProd(inverse(player.cameraDire()),vect))
        self.batch = listTobatch(nv,*data.mode.shellMod[1:])
        self.time = 0
        self.xspeed = self.speed*-player.cameraDire()[2][0]
        self.yspeed = self.speed*-player.cameraDire()[2][1]
        self.zspeed = self.speed*-player.cameraDire()[2][2]
        self.damage = [60,120,250]
        self.direction = player.cameraDire()
        self.gravity = 5
        self.timeLimit = 5
    def draw(self):
        # nvertexList = []
        # for vert in self.model[0]:
        #     x,y,z = self.dx,self.dy,self.dz
        #     nvertexList.append([vert[0]+self.dx,vert[1]+self.dy,vert[2]+self.dz])
        # listTobatchReduced(nvertexList,self.model[-2],(255,255,0)).draw()
        glDisable(GL_CULL_FACE)
        glPushMatrix()
        glTranslatef(self.dx,self.dy,self.dz)
        glScalef(30,30,30)
        self.batch.draw()
        glPopMatrix()
        glEnable(GL_CULL_FACE)
    def move(self,dt):
        self.dx += self.xspeed*dt
        self.dy += self.yspeed*dt
        self.dz += self.zspeed*dt
        self.yspeed -= 9.8*self.gravity*dt #gravity
        pass
    def turn(self):
        pass
class Missile(Moveable,Hurtable):
    def __init__(self,player,target):
        x,y,z,direction = player.dx,player.dy,player.dz,player.direction
        self.dx = x - 30*direction[1][0]
        self.dy = y - 30*direction[1][1]
        self.dz = z - 30*direction[1][2]
        self.speed = 1300
        self.model = data.mode.shellMod
        # nv = []
        # for vect in data.mode.shellMod[0]:
        #     nv.append(matProd(inverse(player.cameraDire()),vect))
        # self.batch = listTobatch(nv,*data.mode.shellMod[1:])
        # self.batch = loadModel("mod/shell","shell.obj")
        self.batch = data.mode.mslModel
        self.time = 0
        self.xspeed = self.speed*-player.cameraDire()[2][0]
        self.yspeed = self.speed*-player.cameraDire()[2][1]
        self.zspeed = self.speed*-player.cameraDire()[2][2]
        self.damage = [120,120,10]
        self.direction = player.cameraDire()
        self.target = target
        self.timeLimit = 15
    def turn(self):
        tgtPo = [self.target.dx,self.target.dy,self.target.dz]
        myPo = [self.dx,self.dy,self.dz]
        # T = r'/|r'|
        look = mod(vAdd(tgtPo,myPo,False))# view z, local -z
        self.direction[2] = constProd(-1,look) # local z
        self.direction[0] = right = crossProd([0,1,0],look) # view x, local x
        self.direction[1]= up = crossProd(right,look)#local y, view y
    def draw(self):
        glDisable(GL_CULL_FACE)
        glPushMatrix()
        # glTranslatef(self.dx,self.dy,self.dz)

        x,y,z = self.direction[0],[0,1,0],self.direction[2]
        # x,y,z = [0,1,0],[0,0,1],[1,0,0]
        myPo = self.dx,self.dy,self.dz
        #[[x],[y],[z]]
        #and opengl matrix written in inverse order
        #and append [displacement] on the right
        mx = [x[0],x[1],x[2],0,
                y[0],y[1],y[2],0,
                z[0],z[1],z[2],0,
                myPo[0],myPo[1],myPo[2], 1]
        # mx = [x[0],y[0],z[0],0,
        # x[1],y[1],z[1],0,
        # x[2],y[2],z[2],0,
        # myPo[0],myPo[1],myPo[2], 1]
        matrix = (GLfloat * 16) (*mx)
        # glTranslatef(myPo[0],myPo[1],myPo[2])
        glMultMatrixf(matrix)
        glPushMatrix()
        glScalef(.08,.08,0.08)
        self.batch.draw()
        glPopMatrix()
        glPopMatrix()
        glEnable(GL_CULL_FACE)
class MonstShell(Shell):
    def __init__(self,x,y,z,direction):
        self.dx = x
        self.dy = y
        self.dz = z
        self.speed = 6500 #3400
        self.model = data.mode.shellMod
        nv = []
        for vect in data.mode.shellMod[0]:
            nv.append(matProd(inverse(direction[:2]+[constProd(-1,direction[2])]),vect))
        self.batch = listTobatch(nv,*data.mode.shellMod[1:])
        self.time = 0
        self.xspeed = self.speed*direction[2][0]
        self.yspeed = self.speed*direction[2][1]
        self.zspeed = self.speed*direction[2][2]
        self.damage = [80,60,30]
        self.direction = direction
        self.friendly = True
        self.gravity = 3
class Astroid(Hurtable):
    def __init__(self,x,y,z,scale,angles): #zoom size and rotation angles
        self.scale = scale
        self.batch = listTobatch(*data.astMod)
        self.dx = x
        self.dy = y
        self.dz = z
        self.angles = angles
        self.hp=[0,0,12000/60*self.scale]
    def draw(self):
        glPushMatrix()
        glTranslatef(self.dx,self.dy,self.dz)
        glScalef(self.scale,self.scale,self.scale)
        glRotatef(self.angles[0],1,0,0)
        glRotatef(self.angles[1],0,1,0)
        glRotatef(self.angles[2],0,0,1)
        self.batch.draw()
        glPopMatrix()
    def inside(self,x,y,z,sphereR = 0):
        if (self.dx-x)**2+(self.dy-y)**2+(self.dz-z)**2 <= (self.scale*23+sphereR)**2 : return True
        else: return False
    def sprCollision(self,stx,stry,strz,vec):#return False or dist
        pass
class Button(object):
    def __init__(self,x,y,width,height,capital):
        self.x = x
        self.y = y 
        self.width = width
        self.height = height
        self.capital = capital
        self.hoverOn = False
        self.strText = pyglet.image.load('res/%s.jpg' % (capital)).get_texture()
        self.color = [ [27,148,217],[27,217,206] ]
        self.transph = 200
        self.transp = 130
    @staticmethod
    def set_state(self):
        #plain
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, w,h, 0, 0, -1.0)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
    @staticmethod
    def unset_state(self):
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        #end of plain
    def draw(self):
        if self.hoverOn:
            t = self.transph
        else:t = self.transp
        x,y = self.x,self.y
        # if self.capital == 'START':
        clr = self.color[0]+[t]+(self.color[1]+[t])*2+self.color[0]+[t]
        glEnable(self.strText.target)
        glBindTexture(self.strText.target,self.strText.id)
        pyglet.graphics.draw(4,GL_POLYGON,
        ('v2f',(x-self.width/2,y-self.height/2,
            x-self.width/2,y+self.height/2,
            x+self.width/2,y+self.height/2,
            x+self.width/2,y-self.height/2)),
        ('c4B',clr),
        ('t2f',[0,1,0,0,1,0,1,1])
        )
        glBindTexture(self.strText.target,0)
        pass
    def inside(self,x,y):
        if self.x-self.width/2 <= x <= self.x + self.width/2 and self.y-self.height/2 <= y <= self.y+self.height/2:
            return True
        return False
        pass
class BillBoard(Button):
    def __init__(self,x,y,width,height,capital,color=[ [100,100,180],[230,230,206] ]):
        super().__init__(x,y,width,height,capital)
        self.color = color
        self.transph = 220
    def draw(self):
        self.hoverOn = True
        super().draw()
class Explosion(object):
    def __init__(self,x,y,z,size = False):
        if size:
            self.quads = [ExpQuads(x,y,z,random.randrange(0,500)/1000,size) for i in range(1)]
        else:
            self.quads = [ExpQuads(x,y,z,random.randrange(0,500)/1000) for i in range(1)]#(x,y,z,startTime)
        self.time = 0 #update, +dt
    def draw(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        for obj in self.quads:
            obj.draw(self.time)
        glDisable(GL_BLEND)
class ExpQuads(object):
        def __init__(self,x,y,z,startTime,size = random.randrange(200,400)):
            self.dx,self.dy,self.dz = x,y,z
            self.startTime = startTime
            self.batch = pyglet.graphics.Batch()
            self.batch.add(4,GL_QUADS,None,
                ("v3f",[-size/2,+size/2,0,-size/2,-size/2,0,
                    +size/2,-size/2,0,+size/2,+size/2,0]),
                ("t2f",[0,0,0,1,1,1,1,0]))
            self.explosionSeq = random.choice(data.mode.explosionSeq)
        def draw(self,t):
            player = data.mode.player
            playerPo = player.cameraPos
            myPo = [self.dx,self.dy,self.dz]
            look = mod(vAdd(playerPo,myPo,False))
            up = [0,1,0]
            right = crossProd(up,look)
            mx = [  right[0], right[1],right[2],0,
                    up[0] ,up[1],up[2],0,
                    look[0], look[1],look[2],0, 
                    myPo[0],myPo[1],myPo[2], 1]
            matrix = (GLfloat * 16) (*mx)
            glPushMatrix()
            glMultMatrixf(matrix)
            glEnable(self.explosionSeq[int(t/0.03)%64].target)
            glBindTexture(self.explosionSeq[int(t/0.03)%64].target,
                self.explosionSeq[int(t/0.03)%64].id)
            glDisable(GL_CULL_FACE)
            self.batch.draw()
            glBindTexture(self.explosionSeq[int(t/0.03)%64].target,0)
            glPopMatrix()
            glEnable(GL_CULL_FACE)
class Target(Player,Hurtable):
    def __init__(self,x,y,z):
        self.dx = x
        self.dy = y
        self.dz = z
        self.speed = random.random()*300+300
        self.sry = self.srx = self.srz= 0
        self.size = 100
        self.batch = data.tgtModel
        self.hp = [3000,3000,3000] 
        self.direction = [[1,0,0],[0,1,0],
        mod([random.choice([-5,-4,-3,-2,-1,1,2,3,4,5]),
        random.choice([-5,-4,-3,-2,-1,1,2,3,4,5]),
        random.choice([-5,-4,-3,-2,-1,1,2,3,4,5])])] #x,y,z
        self.gear = 1
        self.weaponMode = 2
        self.collision = False
        self.labelDisp = False
        self.fireTime = 0
        self.time = time.time()
        self.nv = False
        self.locked = False
        self.lockOnTimer = False
    def smartMove(self):
        player = data.mode.player
        playerPo = [player.dx,player.dy,player.dz]
        myPo = [self.dx,self.dy,self.dz]
        dist = leng(vAdd(myPo,playerPo,False))
        if dist <= 900:
            self.nv = constProd(9/(901-dist),mod(vAdd(playerPo,myPo,False)))
            pass
        elif dist >= 4500:
            self.nv = constProd((dist-4499)/100,mod(vAdd(myPo,playerPo,False)))
            pass
        else:
            self.nv = [0,0,0]
        if data.keys[key.P] : print(self.direction[2])
    def move(self,dt):
        nvz = vAdd(self.direction[2],self.nv)
        homz = constProd(-self.speed*dt,nvz)
        if -data.mapSize*1.5< self.dx + dotProd(homz,[1,0,0]) < data.mapSize*1.5:
            self.dx += dotProd(homz,[1,0,0])
        if -data.mapSize*1.5< self.dy + dotProd(homz,[0,1,0]) < data.mapSize*1.5:
            self.dy += dotProd(homz,[0,1,0])
        if -data.mapSize*1.5< self.dz + dotProd(homz,[0,0,1]) < data.mapSize*1.5:
            self.dz += dotProd(homz,[0,0,1])

    def terminate(self):
        self.thread.exit()
    def inside(self,x,y,z,sphereR = 0):
        if (self.dx-x)**2+(self.dy-y)**2+(self.dz-z)**2 <= (75)**2 : return True
        else: return False
    def set_state(self):
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glCullFace(GL_FRONT)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
    def unset_state(self):
        glCullFace(GL_BACK)
        glDisable(GL_LIGHTING)
        glDisable(GL_LIGHT0)
    def draw(self):
        self.set_state()
        glPushMatrix()
        #calculate view angle to see if in the back
        #in which case target label does not need to be drawn
        glTranslatef(self.dx,self.dy,self.dz)
        if data.mode.shellTrace and len(data.mode.shells)>=1: 
        #during shell trace
        #target shall be drawn at he right position
            shell = data.mode.shells[-1]
            camePo = [shell.dx,shell.dy,shell.dz]
            cameDi = shell.direction
        else:
            player = data.mode.player
            camePo = [player.dx,player.dy,player.dz]
            cameDi = player.cameraDire()
        cameCord = cameDi[:2]+[constProd(-1,cameDi[2])]
        tgtPo = [self.dx,self.dy,self.dz]
        tgtVe = vAdd(tgtPo,camePo,False)
        dtprd = dotProd(cameCord[2],tgtVe)
        if dtprd > 0:
            self.labelDisp = True
        #Bewteen two line of hash tag Adapted from 
        #https://code.google.com/p/geoffrey/source/browse/trunk/selection.py?r=1&spec=svn6
        #################################################################
            pj = (GLdouble * 16)()
            mv = (GLdouble * 16)()
            vw = (GLint * 4)()
            X = ctypes.c_double()
            Y = ctypes.c_double()
            Z = ctypes.c_double()
            glGetDoublev(GL_PROJECTION_MATRIX,pj)
            glGetDoublev(GL_MODELVIEW_MATRIX,mv)
            glGetIntegerv(GL_VIEWPORT,vw)
            gluProject(ctypes.c_double(0),ctypes.c_double(0),ctypes.c_double(0),
            mv,pj,vw,
            ctypes.byref(X), ctypes.byref(Y), ctypes.byref(Z))
            self.labelCord = X.value , h - Y.value
        ##################################################################
        #obtain screen coordinate of targets from openGl, using c-arrays (OpenGL is C)
        else:
            self.labelDisp = False 
        self.batch.draw()
        glPopMatrix()
        self.unset_state()
    def drawLabel(self):
        if self.labelDisp:
            x,y = self.labelCord
            size = 30
            vt = []
            for i in range(30):
                vt += [x+size*sin(rad(360/30*-i)),y+size*cos(rad(360/30*-i))]
            pyglet.graphics.draw(30,GL_LINES,('v2f',vt),('c4B',[255,255,255,255]*30))
            pyglet.graphics.draw(30,GL_LINES,('v2f',vt[2:]+vt[:2]),('c4B',[255,255,255,255]*30))
            pyglet.graphics.draw(8,GL_LINES,('v2f',[x,y-size,x,y-size+10,x,y+size,
                            x,y+size-10,x+size,y,x+size-10,y,x-size,y,x-size+10,y]),
                            ('c4B',[128,255,255,255]*8))
            
            #hp bar
            dist = -87
            vt = [x-35,y+dist,x+35,y+dist,x-35,y+dist+13,x+35,y+dist+13,
            x-35,y+dist+26,x+35,y+dist+26,x-35,y+dist+39,x+35,y+dist+39]
            pyglet.graphics.draw_indexed(8,GL_LINES,[0,1,2,3,4,5,6,7,0,6,1,7],('v2f',vt),('c4B',[255,255,255,255]*8))
            color = [[0,128,255,150],[255,255,128,150],[255,128,255,150]]
            for i in range(3):
            #shield         #armor        #structure
                pyglet.graphics.draw(4,GL_QUADS,('v2f',[x-35,y+dist+13*i,
                    x-35+70/3000*self.hp[i],y+dist+13*i,
                    x-35+70/3000*self.hp[i],y+dist+13*(i+1),
                    x-35,y+dist+13*(i+1)]),('c4B',color[i]*4))
            #lock
            if self.lockOnTimer:
                if not self.locked:
                    if int(self.lockOnTimer*10) % 2 == 0: #let it flash
                        pyglet.graphics.draw(8,GL_LINES,('v2f',[x,y-size,x+size,y,
                            x+size,y,x,y+size,
                            x,y+size,x-size,y,
                        x-size,y,x,y-size]),
                        ('c4B',[255,120,0,255]*8))
                else:
                    pyglet.graphics.draw(8,GL_LINES,('v2f',[
                        x-size/1.414,y-size/1.414,x-size/1.414,y+size/1.414,
                        x-size/1.414,y+size/1.414,x+size/1.414,y+size/1.414,
                        x+size/1.414,y+size/1.414,x+size/1.414,y-size/1.414,
                        x+size/1.414,y-size/1.414,x-size/1.414,y-size/1.414]),
                        ('c4B',[0,255,0,255]*8))
                    #1.414 sqrt(2) circle inscribed squre
            if data.keys[key.P]:
                print()
    def attack(self):
        player = data.mode.player
        playerPo = [player.dx,player.dy,player.dz]
        playerDir = player.direction
        myPo = [self.dx,self.dy,self.dz]
        # tgtVe = vAdd(tgtPo,camePo,False)
        # dtprd = dotProd(cameCord[2],tgtVe)
        estTime = leng(vAdd(myPo,playerPo,False)) / 6500
        estPo = vAdd(playerPo,constProd(-random.random()*1.6*estTime*player.speed,playerDir[2]))
        shellDireZ = mod(vAdd(estPo,myPo,False))
        shellDireX = mod(crossProd(constProd(1,self.direction[2]),shellDireZ))
        shellDireY = mod(crossProd(shellDireZ,shellDireX))
        shellDirection = [ shellDireX,shellDireY,shellDireZ ]
        data.mode.monstshellList.append(MonstShell(self.dx,self.dy,self.dz,shellDirection))
def rad(deg):
        return deg/180*3.14159265359

############################# event framework #############################
def update(dt):
    data.mode.update(dt)
    pass
#Bewteen two line of hash tag Adapted from
#https://pypi.python.org/packages/source/p/pyglet/pyglet-1.2.4.zip
#pyglet-1.2.4/examples/graphics.py
#################################################################
@window.event
def on_resize(w, h):
    # Override the default on_resize handler to create a 3D projection
    glViewport(0,0,w,h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45., w / float(h), .01, float(data.view))
    glMatrixMode(GL_MODELVIEW)
    return pyglet.event.EVENT_HANDLED
##################################################################
@window.event
def on_draw(): #splash main draw
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    data.mode.on_draw()
@window.event
def on_key_press(symbol,modifier):
    data.mode.on_key_press(symbol,modifier)
@window.event
def on_mouse_motion(x, y, dx, dy):
    data.mode.on_mouse_motion(x, y, dx, dy)
@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    data.mode.on_mouse_scroll(x, y, scroll_x, scroll_y)
@window.event
def on_mouse_press(x,y,button,modifiers):    
    data.mode.on_mouse_press(x,y,button,modifiers)
@window.event
def on_mouse_drag(s,y,dx,dy,buttons,modifiers):
    data.mode.on_mouse_drag(s,y,dx,dy,buttons,modifiers)
@window.event
def on_close():
    data.mode.on_close()
    return pyglet.event.EVENT_HANDLED

init()
setup()
data.keys = key.KeyStateHandler()
window.push_handlers(data.keys)
pyglet.clock.schedule_interval(update,1/data.frameRate)
pyglet.app.run()