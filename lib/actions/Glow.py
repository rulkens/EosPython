import logging

FRAMERATE = 60
SLEEP_TIME = 1/FRAMERATE

class Glow():
    def __init__(self, driver, options=None):
        self.driver = driver
        self.speed = 0.009
        self.spacing = 0.2
        self.start = 2
        self.end = 25

    def start(self):
        logging.info('glowing starts!')
        self.x = 0
        self.timer = Timer(SLEEP_TIME, self.step)
        self.timer.start()

    def stop(self):
        self.timer.cancel()

    def step(self):
        vals = [noise(x, y) for y in range(0,32)]
#         logging.info('glowing %s' % vals)
        # determine what part should be illuminated
        for i in range(0,start):
            vals[i] = 0
        for i in range(end, 32):
            vals[i] = 0

        eos.set(vals)
#         print(eos.status)
        logging.info('total intensity: %.4f | average intensity %.4f' % (sum(vals), np.mean(vals)))
        self.x += 1

def noise(x, y):
    basenoise = pnoise2(x*speed, y*spacing, octaves=2)+.4
    basenoise *= 0.8
    return math.pow(basenoise, 3)

