import sys
import pygame
import numpy as np
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
    if number % 2 == 1:
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
        # if choice == 0:
        #     print("constant sanding")
        #     self.sanding = self.const_sand()
        if choice == 0:
            print('slow mid sanding')
            self.sanding = self.slow_mid()
        elif choice == 1:
            print("slow outer sanding")
            self.sanding = self.slow_outer()
        elif choice == 2:
            print("staggered sanding")
            self.sanding = self.staggered()

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

    def staggered(self):
        mu1 = random.uniform(0.1,0.2)
        mu2 = random.uniform(0.2,0.25)
        mu3 = random.uniform(0.25,0.3)
        print("middle zone: ", mu1)
        print("1 and 2 pt: ", mu2)
        print("3 and 4 pt: ", mu3)
        def sand_func(pos):
            if self.left1 < pos[0] > self.right1:
                return mu1
            elif self.left4 < pos[0] < self.left2 or self.right2 < pos[0] < self.right4:
                return mu2
            else:
                return mu3
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

def drawBoard(screen,tableWidth,tableHeight,margin):
    ##draws the underlying board
    pygame.draw.rect(screen, (245, 225, 169), pygame.Rect(margin, margin, tableWidth, tableHeight))

    ##draws the left side point regions
    pygame.draw.line(screen, (255,0,0), (left_1,margin), (left_1,margin + tableHeight))
    pygame.draw.line(screen, (0,0,0), (left_2,margin), (left_2,margin + tableHeight))
    pygame.draw.line(screen, (0,0,0), (left_3,margin), (left_3,margin + tableHeight))
    pygame.draw.line(screen, (0,0,0), (left_4,margin), (left_4,margin + tableHeight))

    ##draws the right side point regions
    pygame.draw.line(screen, (0,0,0), (right_4,margin), (right_4,margin + tableHeight))
    pygame.draw.line(screen, (0,0,0), (right_3,margin), (right_3,margin + tableHeight))
    pygame.draw.line(screen, (0,0,0), (right_2,margin), (right_2,margin + tableHeight))
    pygame.draw.line(screen, (255, 0, 0), (right_1,margin), (right_1,margin + tableHeight))

    ##putting the labels
    tableFont = pygame.font.SysFont("Comic Sans MS", 30)

    OneText = tableFont.render("1",False,(0,0,0))
    TwoText = tableFont.render("2", False, (0,0,0))
    ThreeText = tableFont.render("3", False, (0,0,0))
    FourText = tableFont.render("4", False, (0,0,0))
    screen.blit(OneText, ((right_1+right_2)//2, tableHeight//2 + margin))
    screen.blit(OneText, ((left_1+left_2)//2, tableHeight//2 + margin))

    screen.blit(TwoText, ((right_2+right_3)//2, tableHeight//2 + margin))
    screen.blit(TwoText, ((left_2 + left_3) // 2,tableHeight//2 + margin))

    screen.blit(ThreeText, ((right_3 + right_4) // 2, tableHeight//2 + margin))
    screen.blit(ThreeText, ((left_3 + left_4) // 2, tableHeight//2 + margin))

    screen.blit(FourText, ((right_4 + tableWidth+margin) // 2, tableHeight//2 + margin))
    screen.blit(FourText, ((margin + left_4) // 2, tableHeight//2 + margin))

# def drawBoard(screen,screenWidth,screenHeight,margin):
#     ##draws the underlying board
#     pygame.draw.rect(screen, (245, 225, 169), pygame.Rect(margin, margin, screenWidth - 2 * margin, screenHeight - 2 * margin))
#
#     ##draws the left side point regions
#     pygame.draw.line(screen, (255,0,0), (left_1,margin), (left_1,screenHeight-margin))
#     pygame.draw.line(screen, (0,0,0), (left_2,margin), (left_2,screenHeight-margin))
#     pygame.draw.line(screen, (0,0,0), (left_3,margin), (left_3,screenHeight-margin))
#     pygame.draw.line(screen, (0,0,0), (left_4,margin), (left_4,screenHeight-margin))
#
#     ##draws the right side point regions
#     pygame.draw.line(screen, (0,0,0), (right_4,margin), (right_4,screenHeight-margin))
#     pygame.draw.line(screen, (0,0,0), (right_3,margin), (right_3,screenHeight-margin))
#     pygame.draw.line(screen, (0,0,0), (right_2,margin), (right_2,screenHeight-margin))
#     pygame.draw.line(screen, (255, 0, 0), (right_1,margin), (right_1,screenHeight-margin))
#
#     ##putting the labels
#     tableFont = pygame.font.SysFont("Comic Sans MS", 30)
#
#     OneText = tableFont.render("1",False,(0,0,0))
#     TwoText = tableFont.render("2", False, (0,0,0))
#     ThreeText = tableFont.render("3", False, (0,0,0))
#     FourText = tableFont.render("4", False, (0,0,0))
#     screen.blit(OneText, ((right_1+right_2)//2, screenHeight//2))
#     screen.blit(OneText, ((left_1+left_2)//2, screenHeight//2))
#
#     screen.blit(TwoText, ((right_2+right_3)//2, screenHeight//2))
#     screen.blit(TwoText, ((left_2 + left_3) // 2, screenHeight // 2))
#
#     screen.blit(ThreeText, ((right_3 + right_4) // 2, screenHeight // 2))
#     screen.blit(ThreeText, ((left_3 + left_4) // 2, screenHeight // 2))
#
#     screen.blit(FourText, ((right_4 + screenWidth-margin) // 2, screenHeight // 2))
#     screen.blit(FourText, ((margin + left_4) // 2, screenHeight // 2))

def writeScore(screen,margin):
    scoreFont = pygame.font.SysFont("Comic Sans MS", 35)
    p1Score_text = scoreFont.render("Blue: " + str(p1Score),False,(255,255,255))
    p2Score_text = scoreFont.render("Red: " + str(p2Score), False, (255, 255, 255))

    screen.blit(p1Score_text, (screenWidth//3,margin//2-10))
    screen.blit(p2Score_text, (2*screenWidth//3,margin//2-10))

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

def score(puck):
    x = puck.pos[0]
    if shootRight:
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
    else:
        if left_2 < x <= left_1:
            return 1
        elif left_3 < x <= left_2:
            return 2
        elif left_4 < x <= left_3:
            return 3
        elif margin < x <= left_4:
            return 4
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

##this is for a partially inelastic collision
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

        CR = 0.7 #this is coefficient of restitution. 1 if perfectly elastic and 0 if perfectly inelastic
        v1n_new = (CR*(v2n-v1n) + v1n + v2n)/2
        v2n_new = (CR*(v1n-v2n) + v1n+v2n)/2

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

tableWidth = screenWidth - 2*margin
tableHeight = 400 - 2*margin


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
shootRight = True
p1Win = False
sandingChanged = False
mode = 'splash'
submode = ''
gameType = ''


#keeps track of pucks that are in play or not
activePucks = []
inactivePucks = []


#puck numbering
num = 0

#scores
p1Score = 0
p2Score = 0

#keeps track of how many games have gone by
shotCount = 0
gameNum = 0
p1GameWins = 0

#keeps track of scores for best of 3 and best of 5 matches
p1Scores = []
p2Scores = []

while not done:
    #need this to be able to close window with no issues
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit();
            sys.exit()

    if mode == 'play':
        #draw board and pucks
        screen.fill((0, 0, 0))
        drawBoard(screen,tableWidth,tableHeight,margin)

        #aiming the pucks during a play
        if submode == 'aiming':
            drawPuck(screen,newPuck)
            mousePos = pygame.mouse.get_pos()

            #this is the aiming line. puck will go in this direction with power proportional to length
            direction = np.array(mousePos) - newPuck.pos
            aim_len = 100
            aim_line = aim_len*unitVec(direction) + newPuck.pos
            pygame.draw.line(screen,(0,0,0),(newPuck.pos[0],newPuck.pos[1]),(round(aim_line[0]),round(aim_line[1])))

            #to move the puck up and down when aiming
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and newPuck.pos[1] > margin:
                    newPuck.pos[1] -= 1
                elif event.key == pygame.K_DOWN and newPuck.pos[1] < screenHeight-margin:
                    newPuck.pos[1] += 1

            #to shoot the puck
            if pygame.mouse.get_pressed()[0]:
                #shot happened
                shotCount += 1
                print(shotCount)

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
                #round only lasts 8 shots. Goes to "round_over" submode which asks players if they are ready for next round
                if shotCount % 8 == 0 and num != 0:
                    submode = 'round_over'

                    #these scores are the scores from that single round
                    score1 = 0
                    score2 = 0
                    for puck in activePucks:
                        if puck.num % 2 == 1:
                            score1 += score(puck)
                        else:
                            score2 += score(puck)

                    #actual new total scores from all rounds calculated from the scores from this round
                    p1Score += score1
                    p2Score += score2

                    #scoring convention for sudden death
                    if gameType == 'SD':
                        # if someone gets to >=11 and wins by 2, game over
                        if p1Score >= 11 and p1Score - p2Score >= 2:
                            p1Win = True
                            mode = 'gameOver'
                            submode = ''
                        elif p2Score >= 11 and p2Score - p1Score >= 2:
                            p1Win = False
                            mode = 'gameOver'
                            submode = ''

                    #scoring convention for best of 3
                    elif gameType == 'bo3':
                        # if someone gets to >= 21 and wins by 2, current game is over.
                        # This if statement is for player 1
                        if p1Score >= 21 and p1Score - p2Score >= 2:
                            p1GameWins += 1
                            gameNum += 1

                            #if player 1 reaches 2 game wins, then they have won the match. Takes them to game over screen.
                            #Otherwise next game starts
                            if p1GameWins == 2:
                                p1Win = True
                                mode = 'gameOver'
                                submode = ''
                            else:
                                submode = 'next_game'

                            #the final scores from game are kept track of to display at the end of match
                            p1Scores.append(p1Score)
                            p2Scores.append(p2Score)

                        # if someone gets to >= 21 and wins by 2, current game is over.
                        # This if statement is for player 2
                        elif p2Score >= 21 and p2Score - p1Score >= 2:
                            gameNum += 1
                            # if player 2 reaches 2 game wins, then they have won the match. Takes them to game over screen.
                            # Otherwise next game starts
                            if gameNum - p1GameWins == 2:
                                p1Win = False
                                mode = 'gameOver'
                                submode = ''
                            else:
                                submode = 'next_game'

                            # the final scores from game are kept track of to display at the end of match
                            p1Scores.append(p1Score)
                            p2Scores.append(p2Score)

                    #scoring convention for best of 5
                    elif gameType == 'bo5':
                        # if someone gets to >= 21 and wins by 2, current game is over.
                        # This if statement is for player 1
                        if p1Score >= 21 and p1Score - p2Score >= 2:
                            p1GameWins += 1
                            gameNum += 1
                            # if player 1 reaches 3 game wins, then they have won the match. Takes them to game over screen.
                            # Otherwise next game starts
                            if p1GameWins == 3:
                                p1Win = True
                                mode = 'gameOver'
                                submode = ''
                            else:
                                submode = 'next_game'

                            # the final scores from game are kept track of to display at the end of match
                            p1Scores.append(p1Score)
                            p2Scores.append(p2Score)

                        # if someone gets to >= 21 and wins by 2, current game is over.
                        # This if statement is for player 2
                        elif p2Score >= 21 and p2Score - p1Score >= 2:
                            gameNum += 1
                            # if player 2 reaches 2 game wins, then they have won the match. Takes them to game over screen.
                            # Otherwise next game starts
                            if gameNum - p1GameWins == 3:
                                p1Win = False
                                mode = 'gameOver'
                                submode = ''
                            else:
                                submode = 'next_game'

                            # the final scores from game are kept track of to display at the end of match
                            p1Scores.append(p1Score)
                            p2Scores.append(p2Score)

                #new puck for aiming is initialized
                else:
                    submode = 'aiming'
                    num += 1

                    #initialize new pucks for the next aiming phase
                    if shootRight:
                        newPuck = Puck(num, np.array([margin, screenHeight // 2]), np.array([0, 0]))
                    else:
                        newPuck = Puck(num, np.array([screenWidth-margin,screenHeight//2]),np.array([0,0]))

        #at the end of the round, it just asks if the players are ready for the next round
        if submode == 'round_over':
            s = pygame.Surface((screenWidth, screenHeight), pygame.SRCALPHA)
            s.fill((255, 255, 255, 100))
            screen.blit(s, (0, 0))
            if button('Next Round?', (255, 0, 0), screenWidth // 2-75, screenHeight // 2-35, 150, 70):
                #once ready for next round, the active and inactive pucks are reset
                inactivePucks = []
                activePucks = []

                #switches what side to shoot from and goes back to aiming phase
                shootRight = not shootRight
                submode = 'aiming'

                #num is incremented by 2 so that the color that shot last goes first and shot count is reset
                num += 2
                shotCount = 0

                # initialize new pucks for the next aiming phase
                if shootRight:
                    newPuck = Puck(num, np.array([margin, screenHeight // 2]), np.array([0, 0]))
                else:
                    newPuck = Puck(num, np.array([screenWidth - margin, screenHeight // 2]), np.array([0, 0]))
                time.sleep(0.2)

        # at the end of a game, it just asks if the players are ready for the next game
        if submode == 'next_game':
            s = pygame.Surface((screenWidth, screenHeight), pygame.SRCALPHA)
            s.fill((255, 255, 255, 100))
            screen.blit(s, (0, 0))
            if button('Next Game?', (255, 0, 0), screenWidth // 2-75, screenHeight // 2-35, 150, 70):
                # once ready for next round, the active and inactive pucks are reset
                inactivePucks = []
                activePucks = []

                # switches what side to shoot from and goes back to aiming phase
                shootRight = not shootRight
                submode = 'aiming'

                #the puck numbering, shot count, and scores are all reset
                num = 0
                shotCount = 0
                p1Score = 0
                p2Score = 0
                sandingChanged = False #this lets people know if the sanding has changed or not

                # initialize new pucks for the next aiming phase
                if shootRight:
                    newPuck = Puck(num, np.array([margin, screenHeight // 2]), np.array([0, 0]))
                else:
                    newPuck = Puck(num, np.array([screenWidth - margin, screenHeight // 2]), np.array([0, 0]))
                time.sleep(0.2)

            if button('Change Sanding',(0,0,255), screenWidth//2-75, screenHeight//3 - 50, 150, 70):
                playingField = PlayingField(left_1, left_2, left_3, left_4, right_1, right_2, right_3, right_4)
                sandingChanged = True

            if sandingChanged:
                sandChangeText = headingFont.render('Sanding Changed',False,(0,0,0))
                screen.blit(sandChangeText, (screenWidth//2,2*screenHeight//3))

        #Draws the pucks and writes the score. This is done at the end of the loop rather than beginning
        #because it allows any pucks that fell off the table to not be drawn. Otherwise you get some bugs.
        for puck in activePucks:
            drawPuck(screen, puck)
        writeScore(screen, margin)

    #super simple splash screen
    elif mode == 'splash':
        pygame.init()
        screen.fill((0,0,0))
        if button('Play Ruffle', (255, 0, 0), screenWidth // 2-125, screenHeight//2-25, 250, 50):
            mode = 'choose_game_type'
            submode = ''
            time.sleep(0.2)

    #this screen just asks what game type the players have agreed on
    elif mode == 'choose_game_type':
        #best of 5
        if button('Best of 5',(255,0,0),screenWidth//4-125,screenHeight//2-25,250,50):
            gameType = 'bo5'
            mode = 'play'
            submode = 'aiming'
            newPuck = Puck(num, np.array([margin, screenHeight // 2]), np.array([0, 0]))
            #need this short sleep or else immediately shoots a puck
            time.sleep(0.2)

        #best of 3
        if button('Best of 3',(0,255,0),2 *screenWidth //4 -125, screenHeight//2 - 25, 250,50):
            gameType = 'bo3'
            mode = 'play'
            submode = 'aiming'
            newPuck = Puck(num, np.array([margin, screenHeight // 2]), np.array([0, 0]))
            #need this short sleep or else immediately shoots a puck
            time.sleep(0.2)

        #sudden death
        if button('Sudden Death',(0,0,255),3 * screenWidth //4 - 125, screenHeight//2 - 25, 250,50):
            gameType = 'SD'
            mode = 'play'
            submode = 'aiming'
            newPuck = Puck(num, np.array([margin, screenHeight // 2]), np.array([0, 0]))
            #need this short sleep or else immediately shoots a puck
            time.sleep(0.2)

    #game over screen for when someone wins
    elif mode == 'gameOver':
        #the final arrangement of pucks is shown in the background for players to still see
        screen.fill((0, 0, 0))
        drawBoard(screen, tableWidth, tableHeight, margin)
        for puck in activePucks:
            drawPuck(screen, puck)
        writeScore(screen, margin)

        #a slightly see-through surface so u can still see the pucks and board
        s = pygame.Surface((screenWidth, screenHeight), pygame.SRCALPHA)
        s.fill((100, 255, 255, 100))
        screen.blit(s, (0, 0))

        #game over screen for sudden death just shows final score
        if gameType == 'SD':
            gg_text = titleFont.render('GAME OVER',False,(0,0,0))
            score_text = headingFont.render(str(p1Score)+ ' - ' + str(p2Score),False,(0,0,0))

            screen.blit(gg_text,(screenWidth//2,screenHeight//4))
            screen.blit(score_text,(screenWidth//2,2*screenHeight//4))

        #game over screen for best of 3 and best of 5 shows all the scores from all games
        elif gameType == 'bo3' or gameType == 'bo5':
            gg_text = titleFont.render('GAME OVER', False, (0, 0, 0))
            score_string = ''
            for i in range(len(p1Scores)):
                p1 = p1Scores[i]
                p2 = p2Scores[i]
                score_string = score_string + str(p1) + '-' + str(p2) + '      '

            score_text = headingFont.render(score_string, False, (0, 0, 0))
            screen.blit(score_text,(screenWidth//2,2*screenHeight//3))

        #some text to say congrats to who won
        if p1Win:
            p1Win_text = titleFont.render('Good job Blue', False, (0, 0, 0))
            screen.blit(p1Win_text, (screenWidth // 2, 3 * screenHeight // 4))
        else:
            p2Win_text = titleFont.render('Good job Red', False, (0, 0, 0))
            screen.blit(p2Win_text, (screenWidth // 2, 3 * screenHeight // 4))

        #takes u back to splash screen so u can play again if u wish
        if button('Back to Home Menu', (0,0,0),screenWidth//4,screenHeight//2,200,50):
            mode = 'splash'
            submode = ''

            #game state is fully reset along with scores and a new playing field is made
            activePucks = []
            inactivePucks = []
            num = 0
            p1Score = 0
            p2Score = 0
            p1Win = False
            gameNum = 0
            shotCount = 0
            playingField = PlayingField(left_1,left_2,left_3,left_4,right_1,right_2,right_3,right_4)

    pygame.display.update()