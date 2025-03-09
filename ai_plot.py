import matplotlib.pyplot as plt
from IPython import display
import os

plt.ion()

def save_scores(scores, filename="history.txt"):
    with open(filename, "w") as file:
        for score in scores:
            file.write(f"{score}\n")
    print(f"History file | Save Successed to {filename}")

def load_scores(filename="history.txt"):
    if not os.path.exists(filename):  
        print(f"History file | {filename} does not exist. Starting with an empty history")
        return []
    with open(filename, "r") as file:
        scores_base = [float(line.strip()) for line in file]  
    print(f"History file | {filename} Load Successed")
    return scores_base


def mean_cal(scores):
    mean_scores, index, total_scores = [], 1, 0
    for score in scores:
        total_scores += score
        mean_scores.append(total_scores/index)
        index += 1

    return mean_scores


def plot_scores(scores1, scores2):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Training...')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')

    mean_scores1 = mean_cal(scores1)
    mean_scores2 = mean_cal(scores2)
    
    plt.plot(scores1, color='gray', label='Scores 1')
    plt.plot(mean_scores1, color='gray', linestyle='--', label='Mean Scores 1')
    plt.plot(scores2, color='green', label='Scores 2')
    plt.plot(mean_scores2, color='green', linestyle='--', label='Mean Scores 2')

    plt.legend()

    # plt.ylim(ymin=0)

    plt.text(len(scores1)-1, scores1[-1], f"{scores1[-1]:.2f}")
    plt.text(len(mean_scores1)-1, mean_scores1[-1], f"{mean_scores1[-1]:.2f}")
    plt.text(len(scores2)-1, scores2[-1], f"{scores2[-1]:.2f}")
    plt.text(len(mean_scores2)-1, mean_scores2[-1], f"{mean_scores2[-1]:.2f}")

    plt.show(block=False)
    plt.pause(.1/60)


    # Save history
    save_scores(scores1, filename="history1.txt")
    save_scores(scores2, filename="history2.txt")