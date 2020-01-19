from math import *

class SelectStation:

    @staticmethod
    def get_closest_station(LAT, LON):
        # 215: Voorschoten (Lat: 52.1333 N, Lon: 4.4333E)
        # 330: Hoek van Holland (Lat: 51.98333 N, Lon: 4.1E )
        # 344: Rotterdam (Lat: 51.95N, Lon: 4.1E)

        stations = {215: (52.13333, 4.43333),
                    # 330: (51.98333, 4.1),
                    344: (51.95, 4.1)
                    }
        Voorschoten_dist = 215, SelectStation.distance_between_points(stations[215], (LAT,LON))
        # Hoek_v_Holland_dist = 330,  SelectStation.distance_between_points(stations[330], (LAT,LON))
        Rotterdam_dist= 344, SelectStation.distance_between_points(stations[344], (LAT,LON))

        closest = min(Voorschoten_dist[1], Rotterdam_dist[1]) # , Hoek_v_Holland_dist[1])

        if closest == Voorschoten_dist[1]:
            return Voorschoten_dist[0]
        # elif closest == Hoek_v_Holland_dist[1]:
        #     return Hoek_v_Holland_dist[0]
        else:
            return Rotterdam_dist[0]

    @staticmethod
    def distance_between_points(p1, p2):
        #Formula: https://www.movable-type.co.uk/scripts/latlong.html
        R = 6371 #earth radius (KM)
        LAT1, LON1 = p1
        LAT2, LON2 = p2

        LAT1 = radians(LAT1)
        LAT2 = radians(LAT2)
        LON1 = radians(LON1)
        LON2 = radians(LON2)


        dLAT = LAT2-LAT1
        dLON = LON2-LON1

        a = (sin(dLAT/2))**2 + cos(LAT1) * cos(LAT2) * (sin(dLON/2)**2)
        b = 2*atan2(sqrt(a), sqrt(1-a))

        return R*b