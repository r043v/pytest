import pygame
import time
import requests

from types import SimpleNamespace

pygame.init()

width = 800
height = 600

screen = pygame.display.set_mode( (width, height) )
pygame.display.set_caption("pendu")

PINK = (255,0,255)
BLACK = (0,0,0)
WHITE = (255,255,255)
ORANGE = (255,127,0)
GREEN = (0,255,0)
RED = (255,0,0)

STATE_NONE = 0
STATE_GOOD = 1
STATE_BAD = 2

font = pygame.font.Font(None, 74)
font48 = pygame.font.Font(None, 48)

alphabet = [ None ] * 26

tick = 0
oldTick = 0
clock = pygame.time.Clock()
timer = 31
refresh = 1

word = ""
wordLen = 0

wordState = [] #[ None ] * wordLen

running = True

def generateAlphabet() :
    charWidth = 32
    charPadding = 8
    startx = ( width - ( 13 * ( charWidth + charPadding ) - charPadding ) ) / 2
    x = startx
    y = 420
    for i in range(26):
        rect = pygame.Rect(x, y, charWidth, charWidth )
        l=chr(ord('a') + i)
        alphabet[ i ] = SimpleNamespace( lettre=l, index=i + 1, rect=rect, gfx=font48.render( l, True, BLACK ), state=STATE_NONE )
        x = x + charWidth + charPadding
        if( i == 12 ) :
            y = y + charWidth + charPadding
            x = startx

generateAlphabet()

charSelected = None # current mouse hovered letter

charColors = [ ORANGE, GREEN, RED ] # letters colors for alphabet, [ untested, good, bad ]

# surface in alpha to represent selected letter
selectedSurfaceColor = pygame.Surface((32, 32), pygame.SRCALPHA)
selectedSurfaceColor.fill((*WHITE, 128))

def blitAlphabet() :
    for l in alphabet:
        color = charColors[ l.state ]
        pygame.draw.rect( screen, color, l.rect )

        if( charSelected == l.index ) :
            screen.blit(selectedSurfaceColor, l.rect.topleft)

        screen.blit( l.gfx, l.rect )


def generateWordState() :
    charWidth = 32
    charPadding = 8
    startx = ( width - ( wordLen * ( charWidth + charPadding ) - charPadding ) ) / 2
    x = startx
    y = 200
    for i in range(wordLen):
        rect = pygame.Rect(x, y, charWidth, charWidth )
        l = word[i]
        elem = SimpleNamespace( lettre=l, rect=rect, gfx=None, index=ord(l)-ord('a'), display="*" )
        
        state = alphabet[ elem.index ].state

        if state == STATE_GOOD :
            elem.display = l
            color = ORANGE
        else :
            elem.display = "*"
            color = PINK

        elem.gfx = font48.render( elem.display, True, color )

        wordState[ i ] = elem

        x = x + charWidth + charPadding

def printWordState() :
    for elem in wordState :
        screen.blit( elem.gfx, elem.rect )

def reset( w ) :
    global word, wordLen, wordState
    word = w
    wordLen = len( word )
    wordState = [ None ] * wordLen
    generateWordState()

def submitChar( c ) :
    found = [ i for i, char in enumerate(word) if char == c ]

    if len(found) == 0 : # not found
        return STATE_BAD

    return STATE_GOOD

reset( "banana" )

while running:
    tick = int( time.time() )

    if oldTick != tick :
        oldTick = tick
        timer -= 1
        text = font.render( str(timer), True, PINK )
        text_rect = text.get_rect(center=(400, 300))
        refresh = 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT :
            running = False

            response = requests.get('https://random-word-api.herokuapp.com/word?number=1')
            random_word = response.json()[0]
            print(random_word)

            break            

#        if event.type == pygame.TEXTINPUT :
#            submitChar( event.text )
#            continue

        if event.type == pygame.MOUSEMOTION :
            lastSelected = charSelected
            charSelected = None
            for l in alphabet:
                if l.rect.collidepoint( event.pos ):
                    charSelected = l.index
            
            if lastSelected != charSelected :
                refresh = 1
            continue

        if event.type == pygame.MOUSEBUTTONDOWN :
            for l in alphabet:
                if l.rect.collidepoint( event.pos ):
                    if l.state == 1 : break # already tested
                    l.state = submitChar( l.lettre )
                    if( l.state == STATE_GOOD ) :
                        generateWordState()
                    refresh = 1
            continue

        # unknow event
#       print( "unknow event", event.type, event )
  
    if refresh :
        screen.fill(BLACK)

        screen.blit( text, text_rect )

        blitAlphabet()
        printWordState()

        pygame.display.flip()
        refresh = 0
        
    clock.tick(60)

pygame.quit()
