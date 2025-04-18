import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import load_model
from tensorflow.keras import layers, models
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.callbacks import EarlyStopping
from PIL import Image
import cv2
import os

#Importing the trained model
model = load_model("model1.keras")


# "Main logic starts here"
def process_image(filepath,rows,cols,output_path):

    img = cv2.imread( filepath )

    # Accessing the height and width of image and cell
    row = int(rows)
    column = int(cols)
    img = cv2.resize( img,(column*50,row*50) )
    height,width,_ = img.shape
    tile_h,tile_w = height // row,width // column

    # array if each cell in tiles
    tiles = []

    # All index of cell and images index in another list
    arr_indx = []
    unsafeCell = []
    safeCell = []
    roadCell = []
    groundCell = []

    # Declaring the range of colors
    gray_lower = np.array( [103,99,119] )
    gray_upper = np.array( [104,100,120] )
    green_lower = np.array( [76,255,191] )
    green_upper = np.array( [77,256,192] )

    # Main logic for image processing and predicting the data


    # divided the image into cells and save as single image
    for i in range( row ):
        for j in range( column ):
            y1,y2 = i * tile_h,(i + 1) * tile_h
            x1,x2 = j * tile_w,(j + 1) * tile_w
            tile = img[y1:y2,x1:x2]
            tiles.append( tile )
            arr_indx.append( [i,j] )
            tile = cv2.resize( tile,(128,128) )
            cv2.imwrite( f'./uploads/tile_{i}_{j}.png',tile )

            # classifying the images as green, gray or image
            hsv = cv2.cvtColor( tile,cv2.COLOR_BGR2HSV )
            mask = cv2.inRange( hsv,gray_lower,gray_upper )
            mask2 = cv2.inRange( hsv,green_lower,green_upper )
            grayPixels = cv2.countNonZero( mask )
            greenPixels = cv2.countNonZero( mask2 )
            if (grayPixels > (tile_h * tile_w) * .50):
                pass
                # print( 'Gray',i,j )
                roadCell.append( [i,j] )

            elif (greenPixels > (tile_h * tile_w) * .50):
                pass
                # print( "Green",i,j )
                groundCell.append( [i,j] )

            else:
                img1 = image.load_img( f'./uploads/tile_{i}_{j}.png',target_size=(128,128,3) )
                img_array = image.img_to_array( img1 )
                img_array = tf.expand_dims( img_array,0 )
                prediction = model.predict( img_array )
                if (prediction[0][0] < .55):
                    print( f"Image_{i}_{j}: Safe (Accuracy is: {100 - prediction[0][0] * 100} %)" )
                    safeCell.append( [i,j] )

                elif (prediction[0][0] > .55):
                    print( f"Image_{i}_{j}: Unsafe (Accuracy is: {(prediction[0][0] * 100)} %)" )
                    unsafeCell.append( [i,j] )



    # A-star algorithm for finding the distances

    start = [row-1,0]
    mediator = ()
    path_arr = []
    g = 0
    f = 0
    h = 0
    closeList = []
    openList = [[row-1,0]]
    came = {}
    # Main logic starts here
    for goal in safeCell:
        while openList:
            node = openList.pop( 0 )

            neighbour1 = [node[0] - 1,node[1]]
            neighbour2 = [node[0],node[1] + 1]
            neighbour3 = [node[0],node[1] - 1]
            neighbour4 = [node[0] + 1,node[1]]


            # Logic for moving in each direction
            def func(neighbour):
                # print(f"visiting {node}",neighbour1,neighbour2,openList,closeList)
                if (
                        neighbour in arr_indx and neighbour not in closeList and neighbour not in openList and neighbour not in unsafeCell and neighbour not in groundCell):
                    came[tuple( neighbour )] = tuple( node )
                    openList.append( neighbour )
                    if (node not in closeList and node not in openList and node not in groundCell):
                        g = abs( sum( node ) )
                        h = abs( node[0] - goal[0] ) + abs( node[1] - goal[1] )
                        f = g + h
                        closeList.append( node )
                    else:
                        # print( "Already visisted" )
                        pass


            # Calling the function to check in all four directions
            func( neighbour1 )
            func( neighbour2 )
            func( neighbour3 )
            func( neighbour4 )

            # Checking if the goal is reached break the loop to make it time effective
            if (neighbour1 == goal or neighbour2 == goal or neighbour4 == goal or neighbour4 == goal):
                break

        # Making the route for each safe zone
        mediator = tuple( goal )
        print( "Destiny: ",goal )
        destiny_arr = [tuple( goal )]
        while True:
            if (tuple( mediator ) != tuple( start )):
                try:
                    print( f"{mediator}<--{came[mediator]}" )
                    destiny_arr.append( came[mediator] )
                    mediator = came[mediator]

                except:
                    break
            else:
                break

        path_arr.append( destiny_arr )
        print( "Array format: ",destiny_arr )
        closeList = []
        openList = [[row-1,0]]
        came = {}
    print( path_arr )



    #"Print the final output image"

    for i in range(len(path_arr)):
        for j in range(len(path_arr[i])-1):
            ix = path_arr[i][j][1] * tile_w + tile_w // 2
            iy = path_arr[i][j][0] * tile_h + tile_h // 2
            fx = (path_arr[i][j+1][1] * tile_w) + tile_w // 2
            fy = (path_arr[i][j+1][0] * tile_h) + tile_h // 2
            cv2.line(img,pt1=(ix,iy),pt2=(fx,fy),color=(51,90,255),thickness=3)
            if (j == 0):
                cv2.circle(img, center=(ix, iy), radius=10, color=(76,225,227), thickness=-3)
            elif(j==len(path_arr[i])-2):
                cv2.circle(img, center=(fx, fy), radius=10, color=(30,13,196), thickness=-3)

    cv2.imwrite(output_path,img)
