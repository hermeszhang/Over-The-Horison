from math import cos, sin, acos, floor
######Matrix functions######
def matProd(A,B): #3x3 * 1*3 only
    #[[a,b,c],
    #[d,e,f],
    #[g,h,i]]
    #[a,b,c]
    x = A[0][0] * B[0] +A[0][1]*B[1]+A[0][2]*B[2]
    y = A[1][0] * B[0] +A[1][1]*B[1]+A[1][2]*B[2]
    z = A[2][0] * B[0] +A[2][1]*B[1]+A[2][2]*B[2]
    return [x,y,z]
def dotProd(A,B):
    return (A[0]*B[0]+A[1]*B[1]+A[2]*B[2])
def constProd(c,L):
    return [x*c for x in L ]
def Rx(theta,x,y,z):#rotate about x for theta degree
    #return x,y,z
    (x0,y0,z0) = matProd([[1,0,0],
        [0,cos(theta),-sin(theta)],
        [0,sin(theta),cos(theta)]]
        ,[x,y,z])
    return [x0,y0,z0]
def Ry(theta,x,y,z):#rotate about x for theta degree
    #return x,y,z
    (x0,y0,z0) = matProd([[cos(theta),0,sin(theta)],
        [0,1,0],
        [-sin(theta),0,cos(theta)]]
        ,[x,y,z])
    return [x0,y0,z0]
def Rz(theta,x,y,z):#rotate about x for theta degree
    #return x,y,z
    (x0,y0,z0) = matProd([[cos(theta),-sin(theta),0],
        [sin(theta),cos(theta),0],
        [0,0,1]]
        ,[x,y,z])
    return [x0,y0,z0]
def Ru(theta,u,x,y,z):#rotation of angle theta about axis U
    (x0,y0,z0)= matProd(
        [[cos(theta)+u[0]**2*(1-cos(theta)),u[0]*u[1]*(1-cos(theta))-u[2]*sin(theta),u[0]*u[2]*(1-cos(theta))+u[1]*sin(theta)],
         [u[1]*u[0]*(1-cos(theta))+u[2]*sin(theta),cos(theta)+u[1]**2*(1-cos(theta)),u[1]*u[2]*(1-cos(theta))-u[0]*sin(theta)],
         [u[2]*u[0]*(1-cos(theta))-u[1]*sin(theta),u[2]*u[1]*(1-cos(theta))+u[0]*sin(theta),cos(theta)+u[2]**2*(1-cos(theta))]],
         [x,y,z])
    return [x0,y0,z0]
def leng(L):
    return (L[0]**2+L[1]**2+L[2]**2)**(0.5)
def mod(L):
    return constProd(1/leng(L),L)
def inverse(L):
    #a b c      a d g
    #d e f ---> b e h
    #g h i      c f i
    return  [[L[0][0],L[1][0],L[2][0]],
            [L[0][1],L[1][1],L[2][1]],
            [L[0][2],L[1][2],L[2][2]]]
def vAdd(v1,v2,add=True):
    return [v1[i]+v2[i]*(-1)**(not add) for i in range(3)]

def crossProd (l1,l2):
    a,b,c = l1
    d,e,f = l2
    return [b*f-e*c,a*f-d*c,a*e-b*d]
#test_case
def testvAdd():
    print("testvAdd",end="......")
    assert(vAdd([1,2,3],[2,2,3],False) == [-1,0,0] )
    assert(vAdd([0,0,0],[0,1,2]) == [0,1,2] )
    assert(vAdd([5,6,7],[0,0,0]) == [5,6,7])
    print("passed")
# testvAdd()

######matrix Func######