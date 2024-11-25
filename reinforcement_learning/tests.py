import gymnasium as gym
import pickle
import random
import numpy as np
import time

def default_Q_value():
    return 0


def evaluate_frozen_lake(Q_table, EPSILON, visualize=False):
    total_reward = 0
    env = gym.envs.make("FrozenLake-v1")
    env.reset(seed=1)

    for i in range(100):
        obs = env.reset()[0]
        done = False
        while done == False:
            if random.uniform(0,1) < EPSILON:
                action = env.action_space.sample()
            else:
                prediction = np.array([Q_table[(obs,i)] for i in range(env.action_space.n)])
                action =  np.argmax(prediction)
            obs,reward,terminated,truncated,info = env.step(action)
            done = terminated or truncated
            total_reward += reward
            if visualize:
                env.render()
                time.sleep(.01)
    score = total_reward/100
    return score
    


def test_Q_learning(visualize = False):
    loaded_data = pickle.load(open('Q_TABLE.pkl', 'rb'))
    Q_table = loaded_data[0]
    EPSILON = loaded_data[1]
    score = evaluate_frozen_lake(Q_table,EPSILON,visualize = False)
    print("Q Learning on FrozenLake-v1:")
    print("Average episode-reward over 100 episodes is " + str(score))
    # Gradescope will test on various thresholds for score.
    # You should aim for a score of >= 0.6 if you want to achieve full points.


if __name__ == "__main__":
    print('-' * 40)
    try:
         test_Q_learning()
    except Exception as e:
        print(e)