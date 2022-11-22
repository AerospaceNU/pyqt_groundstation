import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from numpy.linalg import eig, inv
from scipy.spatial import ConvexHull

csv = pd.read_csv("output/beanboozler-calibration.csv")


# csv.loc[csv['crc'] == "Good", 'crc'] = 1
# csv.loc[csv['crc'] == "Bad", 'crc'] = 0

# only good crc
good_crc = csv[(csv["crc"] == "Good")]
good_crc = good_crc[(csv["magnetic_field_z"] > 0.3)]
good_crc = good_crc[["magnetic_field_x", "magnetic_field_y", "magnetic_field_z"]]
good_crc = good_crc.dropna()
# good_crc = csv[(csv['time_stamp_ms'] < 418000)]
# good_crc = csv[(csv['time_stamp_ms'] > 280000)]

# t = good_crc["time_stamp_ms"]
x = good_crc["magnetic_field_x"]
y = good_crc["magnetic_field_y"]
z = good_crc["magnetic_field_z"]


def ls_ellipsoid(xx, yy, zz):
    # finds best fit ellipsoid. Found at http://www.juddzone.com/ALGORITHMS/least_squares_3D_ellipsoid.html
    # least squares fit to a 3D-ellipsoid
    #  Ax^2 + By^2 + Cz^2 +  Dxy +  Exz +  Fyz +  Gx +  Hy +  Iz  = 1
    #
    # Note that sometimes it is expressed as a solution to
    #  Ax^2 + By^2 + Cz^2 + 2Dxy + 2Exz + 2Fyz + 2Gx + 2Hy + 2Iz  = 1
    # where the last six terms have a factor of 2 in them
    # This is in anticipation of forming a matrix with the polynomial coefficients.
    # Those terms with factors of 2 are all off diagonal elements.  These contribute
    # two terms when multiplied out (symmetric) so would need to be divided by two

    # change xx from vector of length N to Nx1 matrix so we can use hstack
    x = xx[:, np.newaxis]
    y = yy[:, np.newaxis]
    z = zz[:, np.newaxis]

    #  Ax^2 + By^2 + Cz^2 +  Dxy +  Exz +  Fyz +  Gx +  Hy +  Iz = 1
    J = np.hstack((x * x, y * y, z * z, x * y, x * z, y * z, x, y, z))
    K = np.ones_like(x)  # column of ones

    # np.hstack performs a loop over all samples and creates
    # a row in J for each x,y,z sample:
    # J[ix,0] = x[ix]*x[ix]
    # J[ix,1] = y[ix]*y[ix]
    # etc.

    JT = J.transpose()
    JTJ = np.dot(JT, J)
    InvJTJ = np.linalg.inv(JTJ)
    ABC = np.dot(InvJTJ, np.dot(JT, K))

    # Rearrange, move the 1 to the other side
    #  Ax^2 + By^2 + Cz^2 +  Dxy +  Exz +  Fyz +  Gx +  Hy +  Iz - 1 = 0
    #    or
    #  Ax^2 + By^2 + Cz^2 +  Dxy +  Exz +  Fyz +  Gx +  Hy +  Iz + J = 0
    #  where J = -1
    eansa = np.append(ABC, -1)

    return eansa


def polyToParams3D(vec, printMe):
    # gets 3D parameters of an ellipsoid. Found at http://www.juddzone.com/ALGORITHMS/least_squares_3D_ellipsoid.html
    # convert the polynomial form of the 3D-ellipsoid to parameters
    # center, axes, and transformation matrix
    # vec is the vector whose elements are the polynomial
    # coefficients A..J
    # returns (center, axes, rotation matrix)

    # Algebraic form: X.T * Amat * X --> polynomial form

    if printMe:
        print("\npolynomial\n", vec)

    Amat = np.array([[vec[0], vec[3] / 2.0, vec[4] / 2.0, vec[6] / 2.0], [vec[3] / 2.0, vec[1], vec[5] / 2.0, vec[7] / 2.0], [vec[4] / 2.0, vec[5] / 2.0, vec[2], vec[8] / 2.0], [vec[6] / 2.0, vec[7] / 2.0, vec[8] / 2.0, vec[9]]])

    if printMe:
        print("\nAlgebraic form of polynomial\n", Amat)

    # See B.Bartoni, Preprint SMU-HEP-10-14 Multi-dimensional Ellipsoidal Fitting
    # equation 20 for the following method for finding the center
    A3 = Amat[0:3, 0:3]
    A3inv = inv(A3)
    ofs = vec[6:9] / 2.0
    center = -np.dot(A3inv, ofs)
    if printMe:
        print("\nCenter at:", center)

    # Center the ellipsoid at the origin
    Tofs = np.eye(4)
    Tofs[3, 0:3] = center
    R = np.dot(Tofs, np.dot(Amat, Tofs.T))
    if printMe:
        print("\nAlgebraic form translated to center\n", R, "\n")

    R3 = R[0:3, 0:3]
    # R3test = R3 / R3[0, 0]
    # print('normed \n',R3test)
    s1 = -R[3, 3]
    R3S = R3 / s1
    (el, ec) = eig(R3S)

    recip = 1.0 / np.abs(el)
    axes = np.sqrt(recip)
    if printMe:
        print("\nAxes are\n", axes, "\n")

    inve = inv(ec)  # inverse is actually the transpose here
    if printMe:
        print("\nRotation matrix\n", inve)
    return (center, axes, inve)


# let us assume some definition of x, y and z

# get convex hull
surface = np.stack((x, y, z), axis=-1)
hullV = ConvexHull(surface)
lH = len(hullV.vertices)
hull = np.zeros((lH, 3))
for i in range(len(hullV.vertices)):
    hull[i] = surface[hullV.vertices[i]]
hull = np.transpose(hull)

# fit ellipsoid on convex hull
eansa = ls_ellipsoid(hull[0], hull[1], hull[2])  # get ellipsoid polynomial coefficients
print("coefficients:", eansa)
center, axes, inve = polyToParams3D(eansa, False)  # get ellipsoid 3D parameters
print("center:", center)
print("axes:", axes)
print("rotationMatrix:", inve)

# use center to offset XYZ
offsetX = x - center[0]
offsetY = y - center[1]
offsetZ = z - center[2]

# eansa is in the form: A x^2 + B y^2 + C z^2 + D x y + E x z + F y z + G x + H y + I z + J = 0 where J = -1


# plt.figure()

# plt.scatter(x, y, label="Flux, XY cross-section")
# plt.scatter(x, z, label="Flux, XZ cross-section")
# plt.scatter(y, z, label="Flux, YZ cross-section")
# plt.legend()

# plt.show()

fig = plt.figure()
ax = fig.add_subplot(projection="3d")
ax.scatter(x, y, z)
ax.scatter(offsetX, offsetY, offsetZ)
plt.show()
