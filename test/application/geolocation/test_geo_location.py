from lxml import etree
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
import utm

def test_geo_load():
    PATH_TEST_GEO = "data/geo"
    x: etree = etree.parse(os.path.join(PATH_TEST_GEO, "activity_12304194656.kml"))
    el_coord = x.xpath('//x:kml/x:Folder/x:Placemark/x:LineString/x:coordinates', namespaces={
        'x': 'http://earth.google.com/kml/2.1'
    })[0]
    coords = el_coord.text.split()
    l_coords = []
    for el in coords:
        l_coords.append(list(map(lambda x: float(x), el.split(','))))
    coords_arr = np.array(l_coords)
    plt.plot(coords_arr[:, 0], coords_arr[:, 1], color='blue', linestyle='--')

    len_valid = -50
    plt.plot(coords_arr[:len_valid, 0], coords_arr[:len_valid, 1], color='green')
    hull = ConvexHull(coords_arr[:len_valid])
    utm_coord = []
    for simplex in hull.simplices:
        plt.plot(coords_arr[simplex, 0],coords_arr[simplex, 1], 'k-')
        c = utm.from_latlon(coords_arr[simplex, 1], coords_arr[simplex, 0])
        utm_coord.append(c)
    plt.grid()
    plt.show()
    # Area calculation
    utm_conv_coord = utm.from_latlon(coords_arr[:len_valid, 1], coords_arr[:len_valid, 0])
    u_co = np.array([utm_conv_coord[0], utm_conv_coord[1]]).T
    print()

    #plt.show()

    min_coord = np.min(u_co, 0)
    u = u_co - min_coord

    hull = ConvexHull(u[:len_valid])
    control_points = [

        hull.simplices[10][0],
        hull.simplices[4][1],
        hull.simplices[5][0],
        hull.simplices[7][0],
        hull.simplices[0][0],

        hull.simplices[2][0],
        hull.simplices[10][0],
    ]

    orig = u[control_points[6]]


    u = u - orig

    print(f"Minimal coordinate: {min_coord}")
    print(f"Origin coordinate: {orig}")
    for x in u:
        plt.plot(x[0], x[1], color='magenta')
    for simplex in hull.simplices:
        plt.plot(u[simplex, 0], u[simplex, 1], 'k--')
    for i, simplex in enumerate(control_points):
        plt.text(float(u[simplex, 0]), float(u[simplex, 1]), f"#{i} ({round(u[simplex, 0],1)},{round(u[simplex, 1], 1)})")
        plt.scatter(u[simplex, 0], u[simplex, 1], color='cyan', linewidth=5)
    for simplex in control_points:
        plt.plot(u[simplex, 0], u[simplex, 1], color='cyan', linewidth=1, linestyle='-')
    plt.grid()
    plt.show()

    for i, cv in enumerate(control_points[:-1]):
        print(f"Coord #{i}: {u[cv]}")
    # Calculate distance between points
    for i, cv in enumerate(control_points[:-1]):
        nx = u[control_points[i+1]]
        d = np.sqrt((u[cv][0] - nx[0])**2 + (u[cv][1] - nx[1])**2)
        print(f"Distance #{i}-#{i+1}: {d}")


    print(hull.volume)
