import numpy as np
from numba import jit
from scipy.optimize import differential_evolution
import threading
from concurrent.futures import ProcessPoolExecutor

pool = ProcessPoolExecutor(1)


@jit
def estimate(all_data, predrange, dist_decay, endweight, mult1, mult2):
    match_weight = np.linspace(endweight, 1, num=predrange)
    final_move, final_val = 0, 0
    for movemult, predmove in ((1.0, 0), (mult1, 1), (mult2, 2)):
        totalval = 0
        for loc in np.where(all_data == predmove)[0]:
            if loc >= predrange:
                match = all_data[loc-predrange: loc] == all_data[-predrange:]
                thisval = movemult * (dist_decay ** loc) * np.sum(match_weight[match])
                totalval += thisval
        if totalval > final_val:
            final_move = predmove
            final_val = totalval
    return final_move


def metric(test_params, data):
    dist_decay, endweight= test_params
    mult1, mult2  = 1.0, 1.0
    predrange = int(8)
    good, bad = 0, 1
    for i in range(1, min(30, len(data))):
        pred = estimate(np.array(data[-i:]), predrange, dist_decay, endweight, mult1, mult2)
        if pred == data[-i]:
            good += 1
        else:
            bad += 1
    return -good / (good + bad)

def get_new_x(player_moves, initial):
    result = differential_evolution()
    return result.x

class PredictionEngine:
    def __init__(self):
        self.player_moves = []
        self.computer_moves = []
        self.params = [0.7, 0.0]#, 1.0, 1.0]
        self.running = True
        self.recalibration_pending = threading.Event()
        self.parameter_lock = threading.Lock()
        self.thread = threading.Thread(target=self.optimize_parameters, daemon=True)
        self.thread.start()

    def parameter_estimate(self, test_params, data):
        dist_decay, endweight = test_params
        mult1, mult2 =  1.0, 1.0
        predrange = int(8)
        return estimate(np.array(data), predrange, dist_decay, endweight, mult1, mult2)


    def optimize_parameters(self):
        while self.running:
            self.recalibration_pending.wait()  # Wait until the event is set
            self.recalibration_pending.clear()  # Wait until the event is set
            result = differential_evolution( metric, [(0.5, 1.0), (0.0, 1.0)], 
                                    tol=0.05, polish=False, args=(self.player_moves[-100:],), x0=self.params)
            with self.parameter_lock:
                self.params = result.x
                print("PARAMETERS UPDATED TO", self.params)

    def predict(self, player_nmove, computer_move):
        self.player_moves.append(player_nmove)
        self.computer_moves.append(computer_move)
        with self.parameter_lock:
            print("RUNNING ESTIMATE")
            nextmove = self.parameter_estimate(self.params, self.player_moves[-100:])
            print("DONE ESTIMATE")
        print(nextmove, self.params)
        self.recalibration_pending.set()
        return (nextmove + 1) % 3

    def stop(self):
        self.running = False
        self.thread.join()
