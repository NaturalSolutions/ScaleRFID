from multiprocessing import Process
# import Pesee_Rework as pr
import Killswitch as ks

myprocess = []
# myprocess.append(Process(target=pr.main, args=()))
myprocess.append(Process(target=ks.main, args=()))

for t in myprocess:
    print('fo,ik^vefk')
    t.start()