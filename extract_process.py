import re
import os

pdg = {"a":22, "Z":23, "W+":24, "W-":-24, "g":21, "ghA":9000001, "ghA~":-9000001, "ghZ":9000002, "ghZ~":-9000002, "ghWp":9000003, "ghWp~":-9000003, "ghWm":9000004, "ghWm~":-9000004, "ghG":9000005, "ghG~":-9000005, "ve":12, "ve~":-12, "vm":14, "vm~":-14, "vt":16, "vt~":-16, "u":2, "u~":-2, "c":4, "c~":-4, "t":6, "t~":-6, "d":1, "d~":-1, "s":3, "s~":-3, "b":5, "b~":-5, "H":25, "G0":250, "G+":251, "G-":-251, "e-":11, "e+":-11, "mu-":13, "mu+":-13, "ta-":15, "ta+":-15}

def extract_process(direc):
    result = direc.rsplit('/',1)[1]
    start = False
    with open(direc+"/matrix.f", "r") as f:
        for line in f:
            m = re.match("C *Process: ", line)
            if m:
                start = True
                proc = (s for s in line[m.end():].split() if s.islower())
                result += ','+' '.join(str(pdg[p]) for p in proc)
            if start and not m: break
    return result

def create_index(subprocesses):
    procs = os.walk(subprocesses).next()[1]
    with open("index", "w") as idx:
        for proc in procs:
            try:
                line = extract_process("%s/%s" % (subprocesses, proc))
            except IOError:
                print("Warning: %s does not contain matrix.f" % proc)
                continue
            idx.write(line+"\n")

if __name__=="__main__":
    import sys
    if len(sys.argv) > 1:
        if len(sys.argv) > 2 and "-i" in sys.argv[1:]:
            if sys.argv[1] == "-i": create_index(sys.argv[2])
            else: create_index(sys.argv[1])
        else:
            try:
                print(extract_process(sys.argv[1]))
            except IOError:
                raise IOError("matrix.f does not exist in specified directory")
    else:
        print("Usage:")
        print("    extract_process.py lib_dir")
        print("    extract_process.py -i subproc_dir")
        print("The first form prints the processes handled by the")
        print("library in lib_dir. The second form creates an index")
        print("of the libraries in subdirectories in subproc_dir.")    
