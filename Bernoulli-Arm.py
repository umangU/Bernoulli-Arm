# Relevant Libraries Imported
import random
import numpy as np
import pandas as pd
import altair as alt

# Epsilon Greedy method Implementation
class EpsilonGreedy():
    def __init__(self, epsilon, counts, values):
        # Storing the probability of explore
        self.epsilon = epsilon
        # Storing the number of pulls for each arms
        self.counts = counts 
        # Storing the average amount of reward we've gotten from each arms
        self.values = values 
        return

    def initialize(self, n_arms):
        self.counts = [0 for col in range(n_arms)]
        self.values = [0.0 for col in range(n_arms)]
        return

    def ind_max(self, x):
        m = max(x)
        return x.index(m)

    def select_arm(self):
        if random.random() > self.epsilon:
            return self.ind_max(self.values)
        else:
            return random.randrange(len(self.values))

    def update(self, chosen_arm, reward):
        self.counts[chosen_arm] = self.counts[chosen_arm] + 1
        n = self.counts[chosen_arm]

        value = self.values[chosen_arm]
        new_value = ((n-1) / float(n)) * value + (1 / float(n)) * reward # weighted average of the previously estimated value and the reward we just received
        self.values[chosen_arm] = new_value
        return

# Bernoulli Arm Method Implementation
class BernoulliArm():
    def __init__(self, p):
        self.p = p

    def draw(self):
        if random.random() > self.p:
            return 0.0
        else:
            return 1.0

# Test Algorithm
def test_algorithm(algo, arms, num_sims, horizon):
    chosen_arms = [0.0 for i in range(num_sims * horizon)]
    rewards = [0.0 for i in range(num_sims * horizon)]
    cumulative_rewards = [0.0 for i in range(num_sims * horizon)]
    sim_nums = [0.0 for i in range(num_sims * horizon)]
    times = [0.0 for i in range(num_sims * horizon)]

    for sim in range(num_sims):
        sim = sim + 1
        algo.initialize(len(arms))

        for t in range(horizon):
            t = t + 1
            index = (sim -1) * horizon + t - 1 #???
            sim_nums[index] = sim
            times[index] = t

            chosen_arm = algo.select_arm()
            chosen_arms[index] = chosen_arm
            reward = arms[chosen_arms[index]].draw()
            rewards[index] = reward

            if t == 1:
                cumulative_rewards[index] = reward
            else:
                cumulative_rewards[index] = cumulative_rewards[index - 1] + reward

            algo.update(chosen_arm, reward)

    return [sim_nums, times, chosen_arms, rewards, cumulative_rewards]


random.seed(1)

means = [0.1, 0.1, 0.1, 0.1, 0.9]
n_arms = len(means)
random.shuffle(means)
arms = list(map(lambda mu: BernoulliArm(mu), means))

f = open("~/e-greedy.csv", "w")

for epsilon in [0.1, 0.2, 0.3, 0.4, 0.5]:
    algo = EpsilonGreedy(epsilon, [], [])
    algo.initialize(n_arms)
    results = test_algorithm(algo, arms, 5000, 250)
    for i in range(len(results[0])):
        f.write(str(epsilon) + "\t")
        f.write("\t".join([str(results[j][i]) for j in range(len(results))]) + "\n")

f.close()

df = pd.read_csv("e-greedy.csv", sep = "\t", header = None, names = ["epsilon", "simulation_num", "step", "chosen_arm", "reward", "cum_reward"])
df.head()

# Flag created for each step to see if best arm was chosen
df["chose_correct"] = np.select(
    [
        df["chosen_arm"] == 2,
        df["chosen_arm"] != 2
    ],
    [
        1,
        0
    ]
)

# Mean for each step for all simulations and epsilon
df_chose_correctly = df.loc[:,["epsilon","step", "chose_correct"]].groupby(["epsilon","step"]).agg("mean")

# Multi index grouping
df_chose_correctly = df_chose_correctly.reset_index()

alt.Chart(df_chose_correctly).mark_line().encode(
    alt.X("step:Q", title = "Time Step"),
    alt.Y("chose_correct:Q", title = "Mean Rate of Choosing Best Arm"),
    color = alt.Color("epsilon:N")
).properties(
    title = "Eps-Greedy: Mean Rate of Choosing Best Arm from 5000 Simulations. 5 Arms = [4 x 0.1, 1 x 0.9]",
)
