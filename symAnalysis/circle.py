import numpy as np
import matplotlib.pyplot as plt

import sys

sys.path.append(".")
from dbMerge import ResultAnalysis

modelDict = {
    "glm-4-9b-chat": "GLM-4-9B-Chat",
    "Llama-3.1-70B-Instruct": "Llama3.1-70B-Instruct",
    "TableGPT2-7B": "TableGPT2-7B",
    "o1-mini": "GPT-o1-mini",
    "deepseek-r1": "DeepSeek-R1",
}

nameVals = ["Overall", "EL", "TS", "CNT", "SUM", "AVG", "CC", "COR"]

if __name__ == "__main__":
    ra = ResultAnalysis("tmp.sqlite")
    results = ra.count(5, 14)
    qtNames = list(results.keys())
    qtC = len(qtNames)
    angles = np.linspace(0, 2 * np.pi, qtC, endpoint=False).tolist()
    angles += angles[:1]

    plt.style.use("ggplot")
    fig, axs = plt.subplots(1, 4, figsize=(24, 6), subplot_kw=dict(polar=True))
    idx = 0
    for scale in ["8k", "16k", "32k", "64k"]:
        saveDict = {}
        for model in modelDict.keys():
            # for model in [
            #     "glm-4-9b-chat",
            #     "Llama-3.1-70B-Instruct",
            #     "TableGPT2-7B",
            #     "gpt-4o",
            # ]:
            saveDict[model] = []
            for qtn in qtNames:
                tab = results[qtn]
                row = tab[
                    (tab["model"] == model)
                    & (tab["scale"] == scale)
                    & (tab["markdown"] == 1)
                ]
                acc = row.iloc[0].tolist()[-1]
                saveDict[model].append(acc)

        axs[idx].set_theta_offset(np.pi / 2)
        axs[idx].set_theta_direction(-1)
        axs[idx].set_xticks(angles[:-1])
        axs[idx].set_xticklabels(nameVals, fontsize=18, weight="bold")
        axs[idx].set_rscale("linear")
        axs[idx].set_ylim(0, 1)

        for k, v in saveDict.items():
            v.append(v[0])
            axs[idx].plot(angles, v, label=modelDict[k], alpha=0.6)
            axs[idx].fill(angles, v, alpha=0.1)

        axs[idx].set_title(scale.upper(), fontsize=24, y=1.1)
        if idx == 3:
            axs[idx].legend(loc="upper right", bbox_to_anchor=(1.3, 1.2), fontsize=14)
        axs[idx].set_yticks([0.2, 0.4, 0.6, 0.8, 1])  # Keep grid levels
        axs[idx].set_yticklabels([])  # Hide the labels

        idx += 1
    plt.tight_layout()
    plt.savefig("symDataset/charts/circle-new.pdf", bbox_inches="tight")
    plt.show()
