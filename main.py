# ----------------- imports --------------------------------------------
from functools import partial
from ArtPiece import ArtPiece
import pandas as pd
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import messagebox
import random

# ----------------- global variables ---------------------------------------


YEAR_SEPARATOR = 2
SIZE_SEPARATOR = 5

art_pieces = []
learning_exhibition = []

characteristics = {"Name": 0, "Artist": 0, "Month": 0, "Year": 0,
                   "Material": 0, "Size": 0, "City": 0, "Country": 0,
                   "Corr": 0, "Description": 0, "B_distance": 0}

create = False


# ----------------- functions --------------------------------------------


def find_characters(i):
    """
    This function finds the characters that are common between the srt piece
    located in art_pieces[i] and art_pieces[i+1]
    :param i: index
    :return:
    """
    if learning_exhibition[i].artist == learning_exhibition[i + 1].artist:
        characteristics["Artist"] += 1

    if (type(learning_exhibition[i].month != float)):
        if learning_exhibition[i].month == learning_exhibition[i + 1].month:
            characteristics["Month"] += 1

    if (not np.isnan(learning_exhibition[i].year)):
        if learning_exhibition[i].year - YEAR_SEPARATOR <= learning_exhibition[
                    i + 1].year <= learning_exhibition[
            i].year + YEAR_SEPARATOR:
            characteristics["Year"] += 1

    if (type(learning_exhibition[i].material != float)):
        if learning_exhibition[i].material == learning_exhibition[
                    i + 1].material:
            characteristics["Material"] += 1

    if (type(learning_exhibition[i].city != float)):
        if learning_exhibition[i].city == learning_exhibition[i + 1].city:
            characteristics["City"] += 1

    if (type(learning_exhibition[i].country != float)):
        if learning_exhibition[i].country == learning_exhibition[
                    i + 1].country:
            characteristics["Country"] += 1

    if (not np.isnan(learning_exhibition[i].length) and (
            not np.isnan(learning_exhibition[i].width))):
        if (learning_exhibition[i].length - SIZE_SEPARATOR <=
                learning_exhibition[i + 1].length <= learning_exhibition[
            i].length + SIZE_SEPARATOR) or (
                            learning_exhibition[i].width - SIZE_SEPARATOR <=
                        learning_exhibition[i + 1].width <=
                        learning_exhibition[i].width + SIZE_SEPARATOR):
            characteristics["Size"] += 1

    corr, b_distance = compare_histogram(learning_exhibition[i],
        learning_exhibition[i + 1])

    characteristics["Corr"] += corr

    characteristics["B_distance"] += b_distance

    if (type(learning_exhibition[i].description) != float) and (
                type(learning_exhibition[i + 1].description) != float):
        characteristics["Description"] += float(
            compare_description(learning_exhibition[i].description,
                learning_exhibition[i + 1].description))


def investigate_existing_exhibition(file_path):
    """
    This function go over all the art pieces in the art pieces array and
    characterize the elements priorities for the art pieces order.
    :param file_path: The csv file name/path.
    :return:
    """
    df = pd.read_csv(file_path)
    df = df.to_numpy()
    for line in df:
        learning_exhibition.append(ArtPiece(line))
    for i in range(len(learning_exhibition) - 1):
        find_characters(i)
    size = len(learning_exhibition)

    # averaging the values
    for key, value in characteristics.items():
        characteristics[key] = float(value / (size - 1))


def build_nodes(file_name):
    """
    This function creates an objects out of the csv file
    :return:
    """
    df = pd.read_csv(file_name)
    df = df.to_numpy()
    for line in df:
        art_pieces.append(ArtPiece(line))
    random.shuffle(art_pieces)


def find_start_node(start_name):
    """
    finding the objects which has the matching names for the start art piece
    and the finish art piece.
    :param start_name: The name of the starting art piece
    :param end_name: The name of the finish art piece
    :return: the matching objects - Assuming they exist in the csv file,
            and they are not the same piece.
    """
    start = None
    for art_piece in art_pieces:
        if art_piece.name == start_name:
            start = art_piece
    return start


def build_basic_graph():
    """
    This function builds the basic distance relation between nodes in the graph
    :return:
    """
    for node in art_pieces:
        for art_piece in art_pieces:
            if art_piece != node and art_piece not in node.neighbours:
                distance = 0

                if (type(art_piece.artist) != float) and (
                            type(node.artist) != float):
                    if art_piece.artist != node.artist:
                        distance += (1 - characteristics["Artist"])
                else:
                    distance += (1 - characteristics["Artist"])

                if (not np.isnan(art_piece.year)) and (
                        not np.isnan(node.year)):
                    if art_piece.year and node.year:
                        if( not (art_piece.year <= (
                                    node.year - YEAR_SEPARATOR)) or (
                                    art_piece.year >= (
                                    node.year + YEAR_SEPARATOR))):
                            distance += 1

                if (type(art_piece.month) != float) and (
                            type(node.month) != float):
                        if (not(art_piece.month != node.month)):
                            distance += 1

                # if (type(art_piece.material) != float) and (type(node.material) != float):
                #     if art_piece.material and node.material:
                #         if art_piece.material != node.material:
                #             distance += characteristics["Material"]
                # else:
                #     distance += characteristics["Material"]

                if (type(art_piece.description) != float) and (
                            type(node.description) != float):
                    distance +=  float(1 - compare_description(node.description,
                            art_piece.description))
                else:
                    distance += 1

                corr, b_distance = compare_histogram(node, art_piece)
                distance += (1 - corr)
                distance +=  b_distance

                fscore = heuristic(art_piece, node)
                node.insert_neighbour(art_piece, distance + fscore)
                art_piece.insert_neighbour(node, distance + fscore)


def print_pieces(pieces_array):
    """
    This function prints the art pieces in the pieces_array by order
    :param pieces_array:
    :return:
    """
    for art_piece in pieces_array:
        print(art_piece)
        print("-------------------")


def show_learning_characterise(file_path):
    """
    This function plots a graph of the received exhibition ordering
     characteristics.
    :return:
    """
    investigate_existing_exhibition(file_path)
    fig = plt.figure()
    plt.title("characteristics of exhibition: " + file_path)
    ax = fig.add_subplot(111)
    plt.ylim(0, 1)
    plt.bar(range(len(characteristics)), list(characteristics.values()),
        align='center')
    plt.xticks(range(len(characteristics)), list(characteristics.keys()))
    fig.autofmt_xdate()
    plt.show()

def heuristic( node_a, node_b):
    distance = 0

    if (type(node_a.artist) != float) and (type(node_b.artist) != float):
        if node_a.artist != node_b.artist:
            distance += characteristics["Artist"]

    if (not np.isnan(node_a.year)) and (not np.isnan(node_b.year)):
            if(not (node_a.year <= (node_b.year - YEAR_SEPARATOR) or node_a.year >= (node_b.year + YEAR_SEPARATOR))):
                distance += characteristics["Year"]

    if (type(node_a.month) != float) and (type(node_b.month) != float):
        if(node_a.month != node_b.month):
            distance += characteristics["Month"]

    if (type(node_a.country) != float) and (type(node_b.country) != float):
        if (node_a.month != node_b.month):
            distance += characteristics["Country"]

    if (type(node_a.city) != float) and (type(node_b.city) != float):
        if (node_a.city != node_b.city):
            distance += characteristics["City"]


    # if (type(art_piece.material) != float) and (type(node.material) != float):
    #     if art_piece.material and node.material:
    #         if art_piece.material != node.material:
    #             distance += characteristics["Material"]
    # else:
    #     distance += characteristics["Material"]

    if (type(node_a.description) != float) and (type(node_b.description) != float):
        distance += characteristics["Description"] *float(
            1 - compare_description(node_a.description, node_b.description))

    corr, b_distance = compare_histogram(node_a, node_b)
    distance += characteristics["Corr"] *(1 - corr)
    distance += b_distance * characteristics["B_distance"]

    return distance


def find_path(source):
    """
    This function runs a find_path search on the graph, starting at the
    received start art_piece
    :param source: The first art piece in the exhibition
    :return: prev - the ordered pieces by shortest distance.
    dist - The actual distances of every node from the start.
    """
    Q = set()
    Q.add(source)
    route = []
    dist = {}
    dist[source] = 0
    route.append(source)
    u = source
    for i in range(len(art_pieces) - 1):
        v = min(u.neighbours, key=lambda x: u.neighbours[x])
        dist[v] = u.neighbours[v]
        route.append(v)
        for art_piece in art_pieces:
            art_piece.neighbours[u] = float('inf')
        u = v

    return route


def image_histogram():
    """
    This function draw histogram in python.
    :return:
    """
    img = cv.imread('self-portrait.jpg', -1)
    histogram = []
    color = ('b', 'g', 'r')
    for channel, col in enumerate(color):
        histr = cv.calcHist([img], [channel], None, [256], [0, 256])
        plt.plot(histr, color=col)
        plt.xlim([0, 256])
        histogram.append(histr)
    plt.title('Histogram for color scale picture')
    plt.show()


def compare_description(text1, text2):
    """
    This functions count the number of matching words in the two texts
    divided by the length of text1
    :param text1:
    :param text2:
    :return:
    """
    count = 0
    new_text1 = text1.split()
    new_text2 = text2.split()
    checked = set()
    checked.add("\\s")
    for word in new_text1:
        if word in new_text2 and word not in checked:
            count += 1
            checked.add(word)
    return float(count / len(text1))


def compare_histogram(base_piece, other_piece):
    """

    :return:
    """
    # if ( (type(base_piece.image_path) == float) or (type(other_piece.image_path))):
    #     return 0, 0 #TODO decideif remove
    src_base = cv.imread(base_piece.image_path)
    src_test1 = cv.imread(other_piece.image_path)
    if src_base is None or src_test1 is None:
        return 0, 0
    hsv_base = cv.cvtColor(src_base, cv.COLOR_BGR2HSV)
    hsv_test1 = cv.cvtColor(src_test1, cv.COLOR_BGR2HSV)
    h_bins = 50
    s_bins = 60
    histSize = [h_bins, s_bins]
    # hue varies from 0 to 179, saturation from 0 to 255
    h_ranges = [0, 180]
    s_ranges = [0, 256]
    ranges = h_ranges + s_ranges  # concat lists
    # Use the 0-th and 1-st channels
    channels = [0, 1]
    hist_base = cv.calcHist([hsv_base], channels, None, histSize, ranges,
        accumulate=False)
    cv.normalize(hist_base, hist_base, alpha=0, beta=1,
        norm_type=cv.NORM_MINMAX)

    hist_test1 = cv.calcHist([hsv_test1], channels, None, histSize, ranges,
        accumulate=False)
    cv.normalize(hist_test1, hist_test1, alpha=0, beta=1,
        norm_type=cv.NORM_MINMAX)

    base_test1 = []

    base_test1.append(cv.compareHist(hist_base, hist_test1, 0))
    base_test1.append(cv.compareHist(hist_base, hist_test1, 3))
    return base_test1


def process_from_path():
    """

    :return:
    """
    show_learning_characterise(r"%s" % (e1.get()))


def show_piece(art_piece):
    """

    :param art_piece:
    :return:
    """
    piece_window = Toplevel()
    piece_window.title(art_piece.name)

    window3_frame = Frame(piece_window, padx=10, pady=10)
    window3_frame.grid()

    name_label = Label(window3_frame, text="Name: " + art_piece.name,
        font="Helvetica 12 bold")
    name_label.grid()
    artist_label = Label(window3_frame, text="Artist: " + art_piece.artist,
        font="Helvetica 12 bold")
    artist_label.grid()
    if (not np.isnan(art_piece.year)):
        year_label = Label(window3_frame, text="Year: " + str(art_piece.year),
            font="Helvetica 12 bold")
        year_label.grid()
    if (type(art_piece.month) != float):
        month_label = Label(window3_frame, text="Month: " + art_piece.month,
            font="Helvetica 12 bold")
        month_label.grid()
    if (type(art_piece.image_gif) != float):
        photo = PhotoImage(file=art_piece.image_gif)
        label = Label(window3_frame, width=650, height=450, image=photo)
        label.image = photo
        label.grid()

    if (type(art_piece.description) != float):
        description_text = Text(piece_window, height=10, width=160,
            font="Helvetica 11")
        description_text.insert(END, art_piece.description)
        description_text.grid()


def draw_graph(order):
    """

    :param start:
    :param order:
    :return:
    """
    window = Toplevel()

    window4_frame = Frame(window, padx=10, pady=10)
    window4_frame.grid()
    piece_b = []
    i =1
    for piece in order:
        curr_piece = piece
        if (type(piece.icon) != float):
            photo = PhotoImage(file=piece.icon)
            piece_b.append(
                Button(window, text=piece.name, pady=5, padx=5, font="Helvetica 11", image = photo,
                    command=partial(show_piece, curr_piece)))
            piece_b[-1].image = photo
            piece_b[-1].grid(row=0,column=i)
            i+=1


def create_from_path():
    """

    :return:
    """
    start = "%s" % (e3.get())
    try:
        build_nodes(r"%s" % (e2.get()))
        build_basic_graph()
    except:
        messagebox.showerror("Error",
            "The file that you uploaded is not in the right format")
        return
    try:
        start_node = find_start_node(start)
        path = find_path(start_node)
    except:
        messagebox.showerror("Error", "Wrong art piece name was entered")
        return
    draw_graph(path)


# ----------------- main --------------------------------------------


if __name__ == '__main__':
    root = Tk()
    root.title("Exhibition Generator")

    photo = PhotoImage(file="back2.gif")
    label = Label(root, width=500, height=250, image=photo, pady=10)
    label.image = photo
    label.grid()
    # # TODO deciede weather or not to have an open image


    # ----------------------------------------------------------

    choosing_art_pieces_to_process = Frame(root, padx=10)
    choosing_art_pieces_to_process.grid(row=1, pady=5)
    upload_label = Label(choosing_art_pieces_to_process,
        text="Upload csv file with your art collection to process",
        font="Helvetica 11")
    upload_label.grid(row=1)
    e1 = Entry(choosing_art_pieces_to_process)
    e1.grid(row=1, column=1, padx=10)
    b1_send_file_name = Button(choosing_art_pieces_to_process,
        text="load data", command=process_from_path, padx=10,
        font="Helvetica 11")
    b1_send_file_name.grid(row=1, column=2)

    # ----------------------------------------------------------

    choosing_art_pieces_to_create = Frame(root, padx=10)
    choosing_art_pieces_to_create.grid(row=2, pady=5)

    upload_label1 = Label(choosing_art_pieces_to_create,
        text="Write the name of the first art piece at your wanted exhibition",
        font="Helvetica 11")
    upload_label1.grid(row=2)
    e3 = Entry(choosing_art_pieces_to_create)
    e3.grid(row=2, column=1, padx=10)

    upload_label2 = Label(choosing_art_pieces_to_create,
        text="Upload csv file with your art collection"
             " to create the ultimate exhibition out of it",
        font="Helvetica 11")
    upload_label2.grid(row=3, pady=5)
    e2 = Entry(choosing_art_pieces_to_create)
    e2.grid(row=3, column=1, padx=10)
    b2_send_file_name = Button(choosing_art_pieces_to_create, text="process",
        command=create_from_path, padx=10, font="Helvetica 11")
    b2_send_file_name.grid(row=3, column=2)

    root.mainloop()
