import pygame
import sys, os, random, time
import cv2
import numpy as np
from math import *

pygame.init()

#WINDOW DETAILS
WIDTH  = 400
HEIGHT = 400

window = pygame.display.set_mode((WIDTH,HEIGHT))
canvas = window.copy()
pygame.display.set_caption("You've been a bad Artist")
pygame.mouse.set_visible(False)

#COLORS
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)

colour = RED

#IMAGES
Triangle = pygame.image.load('triangle.png')
Circle = pygame.image.load('circle.png')
Square = pygame.image.load('square.png')
Pentagon = pygame.image.load('pentagon.png')
C_Rect = pygame.image.load('curvedrectangle.png')
Star = pygame.image.load('star.png')
Weird_Star = pygame.image.load('kindaweirdstar.png')

images = [Triangle, Square, C_Rect, Pentagon, Circle, Star, Weird_Star]

CV_Triangle = cv2.imread("triangle.png")
CV_Circle = cv2.imread("circle.png")
CV_Square = cv2.imread("square.png")
CV_Pentagon = cv2.imread("pentagon.png")
CV_CRect = cv2.imread("curvedrectangle.png")
CV_Star = cv2.imread("star.png")
CV_WeirdStar = cv2.imread("kindaweirdstar.png")

CV_images = [CV_Triangle, CV_Square, CV_CRect, CV_Pentagon, CV_Circle, CV_Star, CV_WeirdStar]

#FUNCTIONS

def img(x,y, Img, surface):
    surface.blit(Img, (x,y))

def roundline(surface, colour, start, end, radius):
    dx = end[0]-start[0]
    dy = end[1]-start[1]
    distance = max(abs(dx), abs(dy))
    for i in range(distance):
        x = int(start[0]+float(i)/distance*dx)
        y = int(start[1]+float(i)/distance*dy)
        pygame.draw.circle(surface, colour, (x,y), radius)

def text_objects(text, font):
    textSurface = font.render(text, True, BLACK)
    return textSurface, textSruface.get_rect()

def message_display(text):
    largeText = pygame.font.SysFont('Cosolas', 115)
    TextSurf, TextRect = text_objects(text, largeText)
    TextRect.center = ((WIDTH/2),(HEIGHT/2))
    window.blit(TextSurf, TextRect)

    pygame.display.update()
    time.sleep(2)

def make_image_array(image):
    array = pygame.surfarray.array3d(image)
    array = cv2.transpose(array)

    CV_array = cv2.cvtColor(array, cv2.COLOR_RGB2BGR)
    CV_array = cv2.cvtColor(CV_array, cv2.COLOR_BGR2GRAY)
    
    return CV_array

def get_moments(image):
    _,image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY)
    moments = cv2.moments(image)
    huMoments = cv2.HuMoments(moments)

    for i in range(0,7):
        huMoments[i] = -1*copysign(1.0, huMoments[i])*log10(abs(huMoments[i]))
        
    return huMoments

def compare_moments(imageA, imageB):
    total = 0
    for i in range(0,7):
        total = total + (imageB[i] - imageA[i])**2

    distance = sqrt(total)
    return distance

def game_loop():
    
    index = 0
    image = images[index]
    CV_image = CV_images[index]
    
    clock = pygame.time.Clock()
    counter, text = 1, '10'
    pygame.time.set_timer(pygame.USEREVENT, 1200)
    font = pygame.font.SysFont('Cosolas', 30)

    last_pos = (0,0)
    draw_on = False
    radius = 2
    canvas.fill(WHITE)
    canvas.set_colorkey(WHITE)
    img(0,0,image, window)

    #distances = []
    
    playing = True

    while playing:

        image = images[index]
        CV_image = CV_images[index]
        mouse = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type ==pygame.USEREVENT:
                counter -= 1
                if counter >= 0:
                    text = str(counter)
                else:
                    index = index + 1
                    if index > 6:
                        user_image = make_image_array(canvas)
                        huUser = get_moments(user_image)
                        CV_image = cv2.cvtColor(CV_image, cv2.COLOR_BGR2GRAY)
                        huOriginal = get_moments(CV_image)

                        distance = compare_moments(huUser, huOriginal)
                        print(distance)
                        #distances.append(distance)
                        
                        text = 'FINISH'
                        window.blit(font.render(text, True, BLACK), (45,10))
                        
                        pygame.display.update()
                        time.sleep(5)
                        playing = False             

                    else:
                        image = images[index]

                        user_image = make_image_array(canvas)
                        huUser = get_moments(user_image)
                        CV_image = cv2.cvtColor(CV_image, cv2.COLOR_BGR2GRAY)
                        huOriginal = get_moments(CV_image)

                        distance = compare_moments(huUser, huOriginal)
                        print(distance)
                        #distances.append(distance)
                        
                        canvas.fill(WHITE)
                        time.sleep(1)
                        counter = 1
                        img(0,0,image,window)
            
            if event.type == pygame.QUIT:
                playing = False

            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:
                    pygame.draw.circle(canvas, colour, mouse, radius)
                    draw_on = True
                
            if event.type == pygame.MOUSEBUTTONUP:
                draw_on = False

            if event.type == pygame.MOUSEMOTION:

                if draw_on:
                    pygame.draw.circle(canvas, colour, mouse, radius)
                    roundline(canvas, colour, event.pos, last_pos, radius)
                last_pos = event.pos            
                    

            #print(event)
        window.fill(WHITE)
        img(0,0,image,window)
        window.blit(canvas, (0,0))
        
        window.blit(font.render(text, True, BLACK), (30,10))
        pygame.draw.circle(window, RED, (pygame.mouse.get_pos()), radius)
        pygame.display.update()


game_loop()
pygame.quit()
sys.exit()
quit()
