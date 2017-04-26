import ME_interface

flavours = [2, 1, -11, 12, 4, 1, 1, -4]
p = [[+0.0000000000e+00, +0.0000000000e+00, +2.8884001842e+02, 2.8884001842e+02],
     [-0.0000000000e+00, -0.0000000000e+00, -1.4777051270e+03, 1.4777051270e+03],
     [-4.6034656589e+01, +7.4242495292e+00, +6.9848159948e+01, 8.3982584721e+01],
     [+2.4176532239e+01, +2.5110213225e+01, +1.5135995358e+02, 1.5532180487e+02],
     [+7.8949206538e+01, +4.9352539805e+01, -1.1908841578e+02, 1.5116448383e+02],
     [-4.3286817791e+01, +1.2461498659e+02, -1.1955501154e+02, 1.7803382898e+02],
     [-4.1886280432e+01, -1.7992762965e+02, -1.1113339033e+03, 1.1265839769e+03],
     [+2.8082016034e+01, -2.6574359498e+01, -6.0095891550e+01, 7.1458466177e+01]]

matrix = ME_interface.ME_interface("params")
matrix.import_list("../SubProcesses")
matrix.param_card = "00.dat"
matrix.mods['P1_ud_epvecddcx'].initialise(matrix.param_dir+'/'+matrix.param_card)
ME = matrix.get_me((flavours,p))
print("Parameters in %s gives:\n|M|^2 = %g" % (matrix.param_card, ME))

matrix.param_card = "01.dat"
matrix.mods['P1_ud_epvecddcx'].initialise(matrix.param_dir+'/'+matrix.param_card)
ME = matrix.get_me((flavours,p))
print("Parameters in %s gives:\n|M|^2 = %g" % (matrix.param_card, ME))
