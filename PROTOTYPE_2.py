import pygame
import sys, os, random, time
import cv2
import numpy as np
from math import *
from bisect import bisect_left

pygame.init()

#WINDOW DETAILS
WIDTH  = 400
HEIGHT = 400

window = pygame.display.set_mode((WIDTH,HEIGHT))
canvas = window.copy()
pygame.display.set_caption("Tracing Ain't Easy")
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

def binarySearch(arr, item, low, high):
    if item == arr[high]:
        return high
    if item == arr[low]:
        return low
    if low >= high:
        return 0
    middle = int((low+high)/2)
    if arr[middle] == item:
        return middle
    if arr[middle] > item:
        return binarySearch(arr, item, low, middle)

    return binarySearch(arr, item, middle+1, high)

def getImagePixels(image, color):
    image = image.convert_alpha()
    pixel_positions = []
    for x in range(image.get_width()):
        for y in range(image.get_height()):
            if image.get_at((x,y)) == (color):
                pixel_positions.append((x,y))
                    
    return pixel_positions

def cvImageArray(image):
    array = pygame.surfarray.array3d(image)
    array = cv2.transpose(array)

    CV_array = cv2.cvtColor(array, cv2.COLOR_RGB2BGR)
    CV_array = cv2.cvtColor(CV_array, cv2.COLOR_BGR2GRAY)
    
    return CV_array

def getMoments(image):
    _,image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY)
    #cv2.imshow("image", image)
    huMoments = cv2.HuMoments(cv2.moments(image))
    
    for i in range(0,7):
        huMoments[i] = -np.sign(huMoments[i]) * np.log10(np.abs(huMoments[i]))
        
    return huMoments

def compareMoments(imageA, imageB):
    total = 0
    for i in range(6):
        total += pow((imageB[i] - imageA[i]),2)

    distance = sqrt(total)
    return distance

def huDriver(image1, image2):
    usr = cvImageArray(image1)
    game = cvImageArray(image2)
    usr_moments = getMoments(usr)
    game_moments = getMoments(game)
    return compareMoments(usr_moments, game_moments)

def game_loop():
    index = 0
    image = images[index]
    
    clock = pygame.time.Clock()
    counter, text = 10, '10'
    pygame.time.set_timer(pygame.USEREVENT, 1200)
    font = pygame.font.SysFont('Cosolas', 30)

    last_pos = (0,0)
    draw_on = False
    radius = 2
    canvas.fill(WHITE)
    canvas.set_colorkey(WHITE)
    img(0,0,image, window)
    
    playing = True

    while playing:

        image = images[index]
        mouse = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type ==pygame.USEREVENT:
                counter -= 1
                if counter >= 0:
                    text = str(counter)
                else:
                    index = index + 1
                    if index > 6:
                        score = 0
                        user_image = getImagePixels(canvas, (255,0,0,255))
                        game_image = getImagePixels(image, (0,0,0,255))

                        if len(user_image) > 0:
                            for i in game_image:
                                ind = binarySearch(user_image, i, 0, len(user_image)-1)
                                if ind != 0:
                                    del user_image[ind]
                                    score += 1
                        
                            distance = huDriver(canvas, image)

                        score /= (len(game_image)*radius/2)
                        score *= 100
                        print(int(score),"%")
                        #totalScore += score
                        
                        text = 'FINISH'
                        window.blit(font.render(text, True, BLACK), (45,10))
                        
                        pygame.display.update()
                        time.sleep(5)
                        playing = False             

                    else:
                        score = 0
                        user_image = getImagePixels(canvas, (255,0,0,255))
                        game_image = getImagePixels(image, (0,0,0,255))

                        if len(user_image) > 0:
                            for i in game_image:
                                ind = binarySearch(user_image, i, 0, len(user_image)-1)
                                if ind != 0:
                                    del user_image[ind]
                                    score += 1
                        
                            distance = huDriver(canvas, image)
                
                        score /= (len(game_image)*radius/2)
                        score *= 100
                        print(int(score),"%")
                        #totalScore += score
                        
                        image = images[index]

                        pygame.image.save(canvas, "user.png")
                        canvas.fill(WHITE)
                        time.sleep(1)
                        counter = 10
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
