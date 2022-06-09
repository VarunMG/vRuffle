import sys
import pygame
import numpy as np
import matplotlib.pyplot as plt
import random
import time
import itertools


###############
### GLOBALS ###
###############

mu = random.uniform(0.1,0.25)
g = 9.81
dt = 0.1
vel_tres = 0.2

###################
### Puck Object ###
###################

def unitVec(v):
    return v/np.linalg.norm(v)

def num2Color(number):
    if number % 2 == 0:
        return (0,0,255)
    else:
        return (255,0,0)

def blur(a):
    kernel = np.array([[1.0,2.0,1.0], [2.0,4.0,2.0], [1.0,2.0,1.0]])
    kernel = kernel / np.sum(kernel)
    arraylist = []
    for y in range(3):
        temparray = np.copy(a)
        temparray = np.roll(temparray, y - 1, axis=0)
        for x in range(3):
            temparray_X = np.copy(temparray)
            temparray_X = np.roll(temparray_X, x - 1, axis=1)*kernel[y,x]
            arraylist.append(temparray_X)

    arraylist = np.array(arraylist)
    arraylist_sum = np.sum(arraylist, axis=0)
    return arraylist_sum

class PlayingField:
    def __init__(self,left1,left2,left3,left4,right1,right2,right3,right4):
        self.left1  = left1
        self.left2 = left2
        self.left3 = left3
        self.left4 = left4
        self.right1 = right1
        self.right2 = right2
        self.right3 = right3
        self.right4 = right4
        choice = random.randint(0,2)
        if choice == 0:
            print("constant sanding")
            self.sanding = self.const_sand()
        elif choice == 1:
            print('slow mid sanding')
            self.sanding = self.slow_mid()
        elif choice == 2:
            print("slow outer sanding")
            self.sanding = self.slow_outer()

    def const_sand(self):
        mu = random.uniform(0.1,0.25)
        print(mu)
        def sand_func(pos):
            return mu
        return sand_func

    def slow_mid(self):
        mu1 = random.uniform(0.1,0.2)
        mu2 = random.uniform(0.2,0.3)
        print("fast zone:", mu1)
        print("slow zone:", mu2)
        def sand_func(pos):
            if self.left1 < pos[0] < self.right1:
                return mu2
            else:
                return mu1
        return sand_func

    def slow_outer(self):
        mu1 = random.uniform(0.1,0.2)
        mu2 = random.uniform(0.2,0.3)
        print("fast zone:", mu1)
        print("slow zone:", mu2)
        def sand_func(pos):
            if self.left1 < pos[0] < self.right1:
                return mu1
            else:
                return mu2
        return sand_func


class Puck:
    def __init__(self,num,pos,vel=np.array([0,0])):
        self.radius = 15
        self.mass = 1
        self.num = num
        self.color = num2Color(num)
        self.pos = pos
        self.vel = vel
        self.rest = (np.linalg.norm(vel) < vel_tres)
    
    def __repr__(self):
        if self.color == (0,0,255):
            col = 'blue'
        else:
            col = 'red'
        string = 'Puck: ' + str(self.num) + ' Color: ' + col
        return string
    
    def step(self,dt,playField):
        #self.vel = self.vel + dt*(-1*mu*g*unitVec(self.vel))
        #self.pos = self.pos + dt*self.vel
        mu = playField.sanding(self.pos)
        if np.array_equal(self.vel, np.array([0,0])):
            acc = np.array([0,0])
        else:
            acc = (-1*mu*g)*unitVec(self.vel)
        self.pos = self.pos + dt*self.vel
        self.vel = self.vel + dt*acc
        if np.linalg.norm(self.vel) < vel_tres:
            self.vel = np.array([0,0])
            self.rest = True

###################
### Easy Button ###
###################

def button(text,color,x0,y0,w,h):
    mouse = pygame.mouse.get_pressed()
    x,y = pygame.mouse.get_pos()
    if (x>=x0 and x<=x0+w and y>=y0 and y<=y0+h):
        newColor = (color[0]*0.5,color[1]*0.5,color[2]*0.5)
        pygame.draw.rect(screen,newColor,(x0,y0,w,h))
    else:
        pygame.draw.rect(screen,color,(x0,y0,w,h))
    buttonFont = pygame.font.SysFont("monospace", 25)
    buttonText = buttonFont.render(text, False, (255,255,255))
    screen.blit(buttonText,(x0+(w-buttonFont.size(text)[0])/2,y0+(h-buttonFont.size(text)[1])/2))
    if mouse[0] == 1:
        if (x>=x0 and x<=x0+w and y>=y0 and y<=y0+h):
            return True
    else:
        return False

##################
### Draw Board ###
##################

def drawBoard(screen,screenWidth,screenHeight,margin):
    ##draws the underlying board
    pygame.draw.rect(screen, (245, 225, 169), pygame.Rect(margin, margin, screenWidth - 2 * margin, screenHeight - 2 * margin))

    ##draws the left side point regions
    pygame.draw.line(screen, (255,0,0), (left_1,margin), (left_1,screenHeight-margin))
    pygame.draw.line(screen, (0,0,0), (left_2,margin), (left_2,screenHeight-margin))
    pygame.draw.line(screen, (0,0,0), (left_3,margin), (left_3,screenHeight-margin))
    pygame.draw.line(screen, (0,0,0), (left_4,margin), (left_4,screenHeight-margin))

    ##draws the right side point regions
    pygame.draw.line(screen, (0,0,0), (right_4,margin), (right_4,screenHeight-margin))
    pygame.draw.line(screen, (0,0,0), (right_3,margin), (right_3,screenHeight-margin))
    pygame.draw.line(screen, (0,0,0), (right_2,margin), (right_2,screenHeight-margin))
    pygame.draw.line(screen, (255, 0, 0), (right_1,margin), (right_1,screenHeight-margin))

    ##putting the labels
    tableFont = pygame.font.SysFont("Comic Sans MS", 30)

    OneText = tableFont.render("1",False,(0,0,0))
    TwoText = tableFont.render("2", False, (0,0,0))
    ThreeText = tableFont.render("3", False, (0,0,0))
    FourText = tableFont.render("4", False, (0,0,0))
    screen.blit(OneText, ((right_1+right_2)//2, screenHeight//2))
    screen.blit(OneText, ((left_1+left_2)//2, screenHeight//2))

    screen.blit(TwoText, ((right_2+right_3)//2, screenHeight//2))
    screen.blit(TwoText, ((left_2 + left_3) // 2, screenHeight // 2))

    screen.blit(ThreeText, ((right_3 + right_4) // 2, screenHeight // 2))
    screen.blit(ThreeText, ((left_3 + left_4) // 2, screenHeight // 2))

    screen.blit(FourText, ((right_4 + screenWidth-margin) // 2, screenHeight // 2))
    screen.blit(FourText, ((margin + left_4) // 2, screenHeight // 2))


def drawPuck(screen,puck):
    pos = puck.pos
    x = int(pos[0])
    y = int(pos[1])
    pygame.draw.circle(screen,puck.color,(x,y),puck.radius)

def allRested(puck_collection):
    for puck in puck_collection:
        if not puck.rest:
            return False
    return True

def score_right(puck):
    x = puck.pos[0]
    if screenWidth-margin > x >= right_4:
        return 4
    elif right_4 > x >= right_3:
        return 3
    elif right_3 > x >= right_2:
        return 2
    elif right_2 > x >= right_1:
        return 1
    else:
        return 0

def onBoard(puck):
    x = puck.pos[0]
    y = puck.pos[1]

    if y < margin:
        return False
    elif y > screenHeight-margin:
        return False
    elif x < margin:
        return False
    elif x > screenWidth-margin:
        return False
    else:
        return True

def pucksMovingTogether(puck1,puck2):
    dist1 = np.linalg.norm(puck1.pos-puck2.pos)
    puck1posf = puck1.pos+puck1.vel*dt
    puck2posf = puck2.pos+puck2.vel*dt
    dist2 = np.linalg.norm(puck1posf-puck2posf)
    if dist2 < dist1:
        return True
    return False


# def collision(puck1,puck2):
#     dist = np.linalg.norm(puck1.pos-puck2.pos)
#     if dist < puck1.radius + puck2.radius and pucksMovingTogether(puck1,puck2):
#         numerator1 = np.dot(puck1.vel - puck2.vel, puck1.pos - puck2.pos)
#         denom1 = (np.linalg.norm(puck1.pos - puck2.pos)) ** 2
#         puck1.vel = puck1.vel - (numerator1 / denom1) * (puck1.pos - puck2.pos)
#         numerator2 = np.dot(puck2.vel - puck1.vel, puck2.pos - puck1.pos)
#         denom2 = (np.linalg.norm(puck2.pos - puck1.pos)) ** 2
#         puck2.vel = puck2.vel - (numerator2 / denom2) * (puck2.pos - puck1.pos)

def collision(puck1,puck2):
    dist = np.linalg.norm(puck1.pos - puck2.pos)
    if dist < puck1.radius + puck2.radius and pucksMovingTogether(puck1, puck2):
        puck1.rest = False
        puck2.rest = False
        displacement = puck2.pos - puck1.pos
        normal = displacement/np.linalg.norm(displacement)
        tangent = np.array([-1*normal[1],normal[0]])
        v1n = np.dot(normal,puck1.vel)
        v1t = np.dot(tangent,puck1.vel)
        v2n = np.dot(normal,puck2.vel)
        v2t = np.dot(tangent,puck2.vel)
        v1n_new = (v2n)/(puck1.mass)
        v2n_new = (v1n)/(puck2.mass)

        V1n = v1n_new*normal
        V1t = v1t*tangent
        V2n = v2n_new*normal
        V2t = v2t*tangent

        puck1.vel = V1n + V1t
        puck2.vel = V2n + V2t

#######################################
### Defining some screen dimensions ###
#######################################


screenWidth = 1270
screenHeight = 400
margin = 30

######################################################################################
### Defining various properties of the playing field + the playing field itself ######
######################################################################################

### demarcations of points ###
ptWidth = screenWidth/20


left_4 = margin+ptWidth
left_3 = margin+2*ptWidth
left_2 = margin+3*ptWidth
left_1 = margin+screenWidth/3

right_1 = screenWidth-margin-screenWidth/3
right_2 = screenWidth-margin-3*ptWidth
right_3 = screenWidth-margin-2*ptWidth
right_4 = screenWidth-margin-ptWidth


### This is the actual playing field ###
playingField = PlayingField(left_1,left_2,left_3,left_4,right_1,right_2,right_3,right_4)

################################################################
### Initializing the pygame window and other base properties ###
################################################################

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((screenWidth, screenHeight))

#font stuff
pygame.font.init()
myFont = pygame.font.SysFont('Comic Sans MS', 15)
titleFont = pygame.font.SysFont('Comic Sans MS',40)
headingFont = pygame.font.SysFont('Comic Sans MS',30)

#game modes and submodes
done = False
mode = 'splash'
submode = ''
gameType = ''

#keeps track of pucks that are in play or not
activePucks = []
inactivePucks = []


#puck numbering
num = 0

while not done:
    #need this to be able to close window with no issues
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit();
            sys.exit()

    if mode == 'play':
        #draw board and pucks
        screen.fill((0, 0, 0))
        drawBoard(screen,screenWidth,screenHeight,margin)

        #aiming the pucks during a play
        if submode == 'aiming':
            drawPuck(screen,newPuck)
            mousePos = pygame.mouse.get_pos()

            #this is the aiming line. puck will go in this direction with power proportional to length
            pygame.draw.line(screen,(0,0,0),(newPuck.pos[0],newPuck.pos[1]),(mousePos[0],mousePos[1]))

            #to move the puck up and down when aiming
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and newPuck.pos[1] > margin:
                    newPuck.pos[1] -= 1
                elif event.key == pygame.K_DOWN and newPuck.pos[1] < screenHeight-margin:
                    newPuck.pos[1] += 1

            #to shoot the puck
            if pygame.mouse.get_pressed()[0]:
                #determines direction and velocity of puck shot
                direction = np.array(mousePos) - newPuck.pos
                vel = min(np.linalg.norm(np.array(direction) / 10),150)
                newPuck.vel=vel*unitVec(direction)
                newPuck.rest = False

                #adds puck to play
                activePucks.append(newPuck)
                submode = 'moving'

        #this is mode where all movement of pucks occurs. The actual "simulation".
        if submode == 'moving':
            if not allRested(activePucks):
                for puck in activePucks:

                    #detect if a puck goes off board and remove it from active pucks list
                    if not onBoard(puck):
                        puck.pos = None
                        puck.vel = None
                        puck.rest = True
                        inactivePucks.append(puck)
                        activePucks.remove(puck)
                    else:
                        # step all pucks until they are still
                        puck.step(dt, playingField)

                #collision detection and velocity updates all done here
                for puckPair in itertools.combinations(activePucks, 2):
                    collision(puckPair[0],puckPair[1])

            #if all rested, resets for a new aiming/shooting turn
            else:
                for puck in activePucks:
                    score = score_right(puck)
                    print(puck)
                    print(score)
                    print("---------")
                #new puck for aiming is initialized
                submode = 'aiming'
                num += 1
                newPuck = Puck(num, np.array([margin, screenHeight // 2]), np.array([0, 0]))

        for puck in activePucks:
            drawPuck(screen, puck)

    #super simple splash screen
    elif mode == 'splash':
        pygame.init()
        if button('Play Ruffle', (255, 0, 0), screenWidth // 2-125, screenHeight//2-25, 250, 50):
            mode = 'choose_game_type'
            submode = ''
            time.sleep(0.2)


    elif mode == 'choose_game_type':
        if button('Best of 5',(255,0,0),screenWidth//4-125,screenHeight//2-25,250,50):
            gameType = 'bo5'
            mode = 'play'
            submode = 'aiming'
            newPuck = Puck(num, np.array([margin, screenHeight // 2]), np.array([0, 0]))
            #need this short sleep or else immediately shoots a puck
            time.sleep(0.2)

        if button('Best of 3',(0,255,0),2 *screenWidth //4 -125, screenHeight//2 - 25, 250,50):
            gameType = 'bo3'
            mode = 'play'
            submode = 'aiming'
            newPuck = Puck(num, np.array([margin, screenHeight // 2]), np.array([0, 0]))
            #need this short sleep or else immediately shoots a puck
            time.sleep(0.2)

        if button('Sudden Death',(0,0,255),3 * screenWidth //4 - 125, screenHeight//2 - 25, 250,50):
            gameType = 'SD'
            mode = 'play'
            submode = 'aiming'
            newPuck = Puck(num, np.array([margin, screenHeight // 2]), np.array([0, 0]))
            #need this short sleep or else immediately shoots a puck
            time.sleep(0.2)

    pygame.display.update()

