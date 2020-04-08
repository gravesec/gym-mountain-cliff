from gym.envs.registration import register

register(
    id='MountainCliff-v0',
    entry_point='gym_mountain_cliff.envs:MountainCliffEnv',
)
