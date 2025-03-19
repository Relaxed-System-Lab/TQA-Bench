import os
import sqlite3
import numpy as np
import matplotlib.pyplot as plt


if __name__ == "__main__":
    savePath = "symDataset/charts/"
    os.makedirs(savePath, exist_ok=True)
    plt.style.use("ggplot")
    modelList = (
        "glm-4-9b-chat Qwen2.5-7B-Instruct Llama3.1-8B-Instruct gpt-4o-mini".split()
    )
    nameList = (
        "GLM-4-9B-Chat Qwen2.5-7B-Instruct Llama3.1-8B-Instruct GPT-4o-mini".split()
    )
    avgs = [0.3343, 0.4986, 0.4657, 0.6086]
    msz = len(modelList)
    conn = sqlite3.connect("tmp.sqlite")
    cur = conn.cursor()
    fig, axes = plt.subplots(2, msz, figsize=(18, 9))

    hms = []
    for idx in range(msz):
        model = modelList[idx]
        cur.execute(
            "SELECT dbIdx, sampleIdx, SUM(correct) * 1.0 / COUNT(*) as acc FROM airline WHERE markdown=1 AND scale='8k' AND model='{model}' GROUP BY dbIdx, sampleIdx ORDER BY dbIdx, sampleIdx;".format(
                model=model
            )
        )
        lst = cur.fetchall()
        cur.execute(
            "SELECT SUM(correct) * 1.0 / COUNT(*) as acc FROM airline WHERE markdown=1 AND scale='8k' AND model='{model}' AND dbIdx<5 AND sampleIdx=1;".format(
                model=model
            )
        )
        avg = cur.fetchone()[0]
        grid = np.zeros((10, 10), dtype=np.float32)
        vals = []
        for x, y, val in lst:
            grid[x, y] = val
            vals.append(val)
        avgVal = sum(vals) / len(vals)
        print(avgVal)
        ims = axes[0][idx].imshow(grid, cmap="viridis", vmin=0, vmax=1)
        hms.append(ims)
        axes[0][idx].set_title(nameList[idx])
        axes[0][idx].grid(False)
        if idx == 0:
            axes[0][idx].set_xlabel("database instance index")
            axes[0][idx].set_ylabel("question instance batch index")
        axes[1][idx].hist(vals, range=[0, 1], alpha=0.6)
        axes[1][idx].axvline(
            x=avg, color="gray", linestyle="--", linewidth=2, label=f"5 in airline"
        )
        axes[1][idx].axvline(
            x=avgVal, color="black", linestyle="-.", linewidth=2, label="all in airline"
        )
        axes[1][idx].axvline(
            x=avgs[idx], color="brown", linestyle=":", linewidth=2, label="5 in all"
        )
        if idx == 0:
            axes[1][idx].set_xlabel("accuracy")
            axes[1][idx].set_ylabel("count")
            axes[1][idx].legend()
    cbar = fig.colorbar(
        hms[0], ax=axes, orientation="vertical", fraction=0.02, pad=0.04
    )
    cbar.set_label("Accuracy")
    plt.savefig(os.path.join(savePath, "sensitive.pdf"), bbox_inches="tight")
