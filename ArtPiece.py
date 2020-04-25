class ArtPiece:

    def __init__(self, row):
        self.name = row[1]
        self.artist = row[2]
        self.month = row[3]
        self.year = row[4]
        self.country = row[5]
        self.city = row[6]
        self.material = row[7]
        self.length = float(str(row[8]).replace('\xa0', ''))
        self.width = float(str(row[9]).replace('\xa0', ''))
        self.description = row[10]
        self.related_artist = row[11]
        self.link = row[12]
        self.image_path = row[13]
        self.image_gif = row[14]
        self.icon = row[15]
        self.neighbours = {}

    def insert_neighbour(self, neighbour, weight):
        """
        This function inserts a neighbour to the art piece neighbour dictionary
        :param neighbour: The node to insert
        :param weight: The weight on the edge connecting them
        :return:
        """
        self.neighbours[neighbour] = weight

    def __str__(self):
        str_representation = "Name:"+str(self.name)
        str_representation+= "\n"
        str_representation+= "Artist:"+str(self.artist)
        str_representation += "\n"
        str_representation += "Month:" + str(self.month)
        str_representation += "\n"
        str_representation += "Year:" + str(self.year)
        str_representation += "\n"
        str_representation += "Country:" + str(self.country)
        str_representation += "\n"
        str_representation += "City:" + str(self.city)
        str_representation += "\n"
        str_representation += "Material:" + str(self.material)
        str_representation += "\n"
        str_representation += "Length:" + str(self.length)
        str_representation += "\n"
        str_representation += "Width:" + str(self.width)
        str_representation += "\n"
        str_representation += "Description:" + str(self.description)
        str_representation += "\n"
        str_representation += "Link:" + str(self.link)
        return str_representation
