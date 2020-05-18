import gym
import math
import numpy as np
from gym.utils import seeding
from gym import error, spaces, utils


class MountainCliffEnv(gym.Env):
    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second': 30
    }

    def __init__(self):
        self.cliff_position = -1.2
        self.min_position = -1.2
        self.max_position = .6
        self.max_speed = .07
        self.goal_position = .5
        self.force = .001
        self.gravity = .0025
        self.cliff_penalty = -100.
        self.low = np.array([self.cliff_position, -self.max_speed], dtype=np.float32)
        self.high = np.array([self.max_position, self.max_speed], dtype=np.float32)
        self.viewer = None
        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Box(self.low, self.high, dtype=np.float32)
        self.seed()
    
    def seed(self, seed = None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]
    
    def step(self, action):
        assert self.action_space.contains(action), "%r (%s) invalid" % (action, type(action))
        position, velocity = self.state
        velocity += (action - 1) * self.force + math.cos(3 * position) * (-self.gravity)
        velocity = np.clip(velocity, -self.max_speed, self.max_speed)
        position += velocity
        position = np.clip(position, self.cliff_position, self.max_position)
        if position <= self.cliff_position:
            reward = self.cliff_penalty
            self.state = self.reset()
        else:
            reward = -1.
            self.state = (position, velocity)

        done = bool(position >= self.goal_position)
        return np.array(self.state), reward, done, {}

    def reset(self):
        self.state = np.array([self.np_random.uniform(low = -.6, high = -.4), 0])
        return np.array(self.state)
        
    def _height(self, xs):
        return np.sin(3 * xs) * .45 + .55

    def render(self, mode = 'human'):
        screen_width = 600
        screen_height = 400
        world_width = self.max_position - self.min_position
        scale = screen_width / world_width
        carwidth = 40
        carheight = 20
        if self.viewer is None:
            from gym.envs.classic_control import rendering
            self.viewer = rendering.Viewer(screen_width, screen_height)
            xs = np.linspace(self.cliff_position, self.max_position, 100)
            ys = self._height(xs)
            xys = list(zip((xs - self.min_position) * scale, ys * scale))
            self.track = rendering.make_polyline(xys)
            self.track.set_linewidth(4)
            self.viewer.add_geom(self.track)
            cliff_x = (self.cliff_position - self.min_position) * scale
            cliff_y = self._height(self.cliff_position) * scale
            cliff = rendering.Line((cliff_x, cliff_y), (cliff_x, cliff_y - 1000))
            cliff.linewidth.stroke = 4
            self.viewer.add_geom(cliff)
            clearance = 10
            l, r, t, b = -carwidth/2, carwidth/2, carheight, 0
            car = rendering.FilledPolygon([(l, b), (l, t), (r, t), (r, b)])
            car.add_attr(rendering.Transform(translation = (0, clearance)))
            self.cartrans = rendering.Transform()
            car.add_attr(self.cartrans)
            self.viewer.add_geom(car)
            frontwheel = rendering.make_circle(carheight / 2.5)
            frontwheel.set_color(.5, .5, .5)
            frontwheel.add_attr(rendering.Transform(translation = (carwidth / 4, clearance)))
            frontwheel.add_attr(self.cartrans)
            self.viewer.add_geom(frontwheel)
            backwheel = rendering.make_circle(carheight / 2.5)
            backwheel.add_attr(rendering.Transform(translation = (-carwidth / 4, clearance)))
            backwheel.add_attr(self.cartrans)
            backwheel.set_color(.5, .5, .5)
            self.viewer.add_geom(backwheel)
            flagx = (self.goal_position - self.min_position) * scale
            flagy1 = self._height(self.goal_position) * scale
            flagy2 = flagy1 + 50
            flagpole = rendering.Line((flagx, flagy1), (flagx, flagy2))
            self.viewer.add_geom(flagpole)
            flag = rendering.FilledPolygon([(flagx, flagy2), (flagx, flagy2 - 10), (flagx + 25, flagy2 - 5)])
            flag.set_color(.8, .8, 0)
            self.viewer.add_geom(flag)
        pos = self.state[0]
        self.cartrans.set_translation((pos - self.min_position) * scale, self._height(pos) * scale)
        self.cartrans.set_rotation(math.cos(3 * pos))
        return self.viewer.render(return_rgb_array = mode == 'rgb_array')

    def close(self):
        if self.viewer:
            self.viewer.close()
            self.viewer = None
