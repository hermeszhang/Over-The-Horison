import pyglet
from pyglet.gl import *
from math import cos, sin, acos, floor
import os
######obj loading######
def readFile(path):
    with open(path,'rt') as f:
        return f.read()

#Bewteen two line of hash tag referenced by
#http://pyglet.readthedocs.org/en/latest/programming_guide/graphics.html#hierarchical-state
#################################################################
class BindTexture(pyglet.graphics.Group):
    def __init__(self,groupDict):
        super().__init__()
        # print("__________gpd",groupDict)
        if 'texture' in groupDict:
            self.texture = groupDict['texture']
        else: self.texture = False
        self.name = groupDict['name']
        self.dict = groupDict
    def set_state(self):
        if self.texture != False:
            glEnable(self.texture.target)
            glBindTexture(self.texture.target,self.texture.id)
            glTexParameteri(self.texture.target, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_NEAREST)
            glTexParameteri(self.texture.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        def vect(*args):#return GLfloat
            if type(args[0]) == list:
                args = args[0] + [1]
            return (GLfloat * len(args))(*args)

        glLightfv(GL_LIGHT0, GL_POSITION, vect(-1, 1, 1, 0))
        glLightfv(GL_LIGHT0, GL_SPECULAR, vect(.25, .25, .25, 1))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, vect(1, 1, 1, 1))

        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, vect(self.dict['Ka'], 1))
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, vect(self.dict['Kd'],1))
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, vect(self.dict['Ks'], 1))
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, vect(self.dict['Ks'], 1))
        # glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, 50.0)
    def unset_state(self):
        if self.texture != False:
            glBindTexture(self.texture.target,0)
            glDisable(self.texture.target)

        pass
    def __eq__(self, other):
        if self.texture == False:
            return (self.__class__ is other.__class__ and
                self.name == other.name )
        else:
            return (self.__class__ is other.__class__ and
                self.texture.id == other.texture.id and
                self.texture.target == other.texture.target )
    def __hash__(self):
        if self.texture == False:
            return hash((self.name,))
        else:
            return hash((self.texture.id, self.texture.target))
#######################################################################


def loadModel(path,files,fixed = True):#return vertex array
    print('Loading',end="")
    content = readFile(path+'/'+files).split("\n")
    vertexCord = []
    textureCord = []
    normalCord = []
    faces = []
    for i in content:
        lineContent = i.split(" ")
        if lineContent[0]=="#" or lineContent[0].startswith('#'):
            pass
        elif lineContent[0] == 'v':
            vertexCord.append(list(map(float,lineContent[1:])))
        elif lineContent[0] == 'vt':
            textureCord.append(list(map(float,lineContent[1:])))
        elif lineContent[0] =='vn':
            normalCord.append(list(map(float,lineContent[1:])))
        elif lineContent[0] == 'f':
            faces.append(tuple(map(str,lineContent[1:])))
        elif lineContent[0] == 'usemtl':
            faces.append(('usemtl',lineContent[1]))
        elif lineContent[0] == 'mtllib':
            mtls = loadMTL(path,lineContent[1])
    print("..45%..",end="")
    if fixed:
        return listTobatch(vertexCord,textureCord,normalCord,faces,mtls)
    else: return[vertexCord,textureCord,normalCord,faces,mtls]
def listTobatch(vertexCord,textureCord,normalCord,faces,mtls):
    modBatch = pyglet.graphics.Batch()
    for face in faces:
        vert = []
        text = []
        norm = []
        if face[0].startswith('usemtl'):
            #switch mode
            currentGrounp = mtls[face[1]]
            pass
        else:
            for v in face:#each vertex
                vcont = v.split("/")
                vert.extend(vertexCord[int(vcont[0])-1])
                if vcont[1]!='':
                    text.extend(textureCord[int(vcont[1])-1])
                    # print('txt',text)
                if vcont[2]!= '':                
                    norm.extend(normalCord[int(vcont[2])-1])
                    # print('nrm',norm)
            length = len(face)
            if length == 4:
                try:
                    modBatch.add(4,GL_QUADS,BindTexture(currentGrounp),
                    ('v3f',vert),('t2f',text),('n3f',norm))
                except:
                    print(vert,text,norm)
            if length == 3:
                modBatch.add(3,GL_TRIANGLES,BindTexture(currentGrounp),
                        ('v3f',vert),('t2f',text),('n3f',norm))
    # print('done',end="")
    return modBatch
    # print(faces[:20])
def loadMTL(path,files):#input mtl path, load textures and return property dict
    content = readFile(path+'/'+files).split("\n")
    properties = dict()
    textureFiles = []
    for i in content:
        lineContent = i.split(' ')
        if lineContent[0] == 'newmtl':
            curType = lineContent[1]
            properties[curType]=dict()
            properties[curType]['name']=lineContent[1]
        elif lineContent[0] == "":
            pass
        elif lineContent[0] == 'map_Kd':
            textIMG = pyglet.image.load(path+os.sep+lineContent[1].split('\\')[0]+os.sep+lineContent[1].split('\\')[1])
            properties[curType]['texture']=textIMG.get_texture()
            glGenerateMipmap(properties[curType]['texture'].target)
        elif lineContent[0]=="#" or lineContent[0].startswith('#'):
            pass
        else:
            properties[curType][lineContent[0]] = list(map(float,lineContent[1:]))
    return properties
def listTobatchReduced(vertexCord,faces,color):
    modBatch = pyglet.graphics.Batch()
    for face in faces:
        vert = []
        counter = 0
        if face[0].startswith('usemtl'):
            pass
        else:
            for v in face:#each vertex
                vcont = v.split("/")
                vert.extend(vertexCord[int(vcont[0])-1])
                counter += 1
            clr = (color*counter)
            if len(face) == 4:
                modBatch.add(4,GL_QUADS,None,
                    ('v3f',vert),('c3B',clr))
            if len(face) == 3:
                modBatch.add(3,GL_TRIANGLES,None,
                        ('v3f',vert),("c3B",clr))
    return modBatch
######obj loading######
