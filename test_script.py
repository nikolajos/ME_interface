from ME_interface import ME_interface

#flavours = [2, 1, -11, 12, 4, 1, 1, -4]
p = [[2.8884001842e+02, +0.0000000000e+00, +0.0000000000e+00, +2.8884001842e+02],
     [1.4777051270e+03, -0.0000000000e+00, -0.0000000000e+00, -1.4777051270e+03],
     [8.3982584721e+01, -4.6034656589e+01, +7.4242495292e+00, +6.9848159948e+01],
     [1.5532180487e+02, +2.4176532239e+01, +2.5110213225e+01, +1.5135995358e+02],
     [1.5116448383e+02, +7.8949206538e+01, +4.9352539805e+01, -1.1908841578e+02],
     [1.7803382898e+02, -4.3286817791e+01, +1.2461498659e+02, -1.1955501154e+02],
     [1.1265839769e+03, -4.1886280432e+01, -1.7992762965e+02, -1.1113339033e+03],
     [7.1458466177e+01, +2.8082016034e+01, -2.6574359498e+01, -6.0095891550e+01]]

matrix = ME_interface("params", "/home/nikolaj/Downloads/MG5_aMC_v2_4_2/test/SubProcesses")
matrix.import_libs()

matrix.set_param_card("000.dat")
#ME = matrix.get_me((flavours,p))
#print("Parameters in %s gives:\n|M|^2 = %g" % (matrix.param_card, ME))

#print(matrix.get_me(([2,3,11,-12,2,2,3,-1],p)))

#print(matrix.get_me(([2,-2,11,-12,4,3,-3,-3],p)))

#print(matrix.get_me(([1,-2,11,-12,21,21,2,-2],p)))
try:
    print(matrix.get_me([21, 1, 11, -12, 21, 21, 21, 2],p))
except KeyError:
    print matrix.mods
    raise KeyError

matrix.set_param_card("001.dat")

#ME = matrix.get_me((flavours,p))
#print("Parameters in %s gives:\n|M|^2 = %g" % (matrix.param_card, ME))

#print(matrix.get_me(([2,3,11,-12,2,2,3,-1],p)))

#print(matrix.get_me(([2,-2,11,-12,4,3,-3,-3],p)))

#print(matrix.get_me(([1,-2,11,-12,21,21,2,-2],p)))

print(matrix.get_me([21, 1, 11, -12, 21, 21, 21, 2],p))

