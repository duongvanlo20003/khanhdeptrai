import matplotlib.pyplot as plt
from IPython import display

plt.ion()

def mean_cal(scores):
    mean_scores, index, total_scores = [], 1, 0
    for score in scores:
        total_scores += score
        mean_scores.append(total_scores/index)
        index += 1

    return mean_scores
def save_plot_data(scores1, scores2, filename="C:/Users/khanh/Desktop/plot_data.txt"):
    """ Lưu thông tin đồ thị vào file text """
    mean_scores1 = mean_cal(scores1)
    mean_scores2 = mean_cal(scores2)

    with open(filename, "w") as f:
        f.write("Game_Number, Score1, Mean_Score1, Score2, Mean_Score2\n")
        for i in range(len(scores1)):
            f.write(f"{i+1}, {scores1[i]:.2f}, {mean_scores1[i]:.2f}, {scores2[i]:.2f}, {mean_scores2[i]:.2f}\n")

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
    save_plot_data(scores1, scores2)
