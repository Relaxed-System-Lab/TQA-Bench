import matplotlib.pyplot as plt
import matplotlib.image as mpimg

plt.style.use("ggplot")
plt.figure(figsize=[24, 5])
models = "GLM-4-9B-Chat DeepSeek-V2-Lite-Chat Baichuan2-7B-Chat Baichuan2-13B-Chat Vicuna-7B-V1.5-16K Vicuna-13B-V1.5-16K Mistral-7B-Instruct Mistral-Nemo-Instruct Llama3.1-8B-Instruct Llama3.1-70B-Instruct Qwen2.5-3B-Instruct Qwen2.5-7B-Instruct Qwen2.5-Coder-7B-Instruct Qwen2.5-14B-Instruct Qwen2.5-72B-Instruct Gemma2-2B-It Gemma2-9B-It Gemma2-27B-It DeepSeek-V3 TableGPT2-7B TableLlama GPT-4o-mini GPT-4o GPT-o1-mini GPT-o3-mini DeepSeek-R1-Distill-Qwen-7B DeepSeek-R1-Distill-Qwen-14B DeepSeek-R1 QwQ-32B-Preview".split()
values = "29.18 21.93 21.25 3.68 20.64 13.64 20.09 23.96 40.21 54.61 26.50 43.93 44.21 46.00 43.80 28.14 38.17 42.86 74.16 37.93 0.00 56.07 70.81 71.92 84.91 22.76 39.07 89.39 2.24".split()
models = "GLM-4-9B-Chat Baichuan2-7B-Chat Baichuan2-13B-Chat Vicuna-7B-V1.5-16K Vicuna-13B-V1.5-16K Mistral-7B-Instruct Mistral-Nemo-Instruct Llama3.1-8B-Instruct Llama3.1-70B-Instruct Qwen2.5-3B-Instruct Qwen2.5-7B-Instruct Qwen2.5-Coder-7B-Instruct Qwen2.5-14B-Instruct Qwen2.5-72B-Instruct Gemma2-2B-It Gemma2-9B-It Gemma2-27B-It DeepSeek-V3 TableGPT2-7B TableLlama GPT-4o-mini GPT-4o GPT-o1-mini GPT-o3-mini DeepSeek-R1-Distill-Qwen-7B DeepSeek-R1-Distill-Qwen-14B DeepSeek-R1 QwQ-32B-Preview".split()
values = "29.18 21.25 3.68 20.64 13.64 20.09 23.96 40.21 54.61 26.50 43.93 44.21 46.00 43.80 28.14 38.17 42.86 74.16 37.93 0.00 56.07 70.81 71.92 84.91 22.76 39.07 89.39 2.24".split()
values = [float(item) for item in values]
colors = ["red"] * 5 + ["blue"] * 13 + ["yellow"] * 2 + ["green"] * 4 + ["purple"] * 4
labels = (
    ["Chat Models"]
    + [None] * 4
    + ["Instruct Models"]
    + [None] * 12
    + ["Table Specific Models", None]
    + ["Close-Source Models"]
    + [None] * 3
    + ["Reasoning Models"]
    + [None] * 3
)
x = list(range(28))
plt.xticks(x, models, fontsize=12, weight="bold")
plt.bar(x, values, color=colors, alpha=0.6, label=labels, width=0.6)
plt.xticks(rotation=20, ha="right")

for i in range(len(values)):
    plt.text(i, values[i], str(values[i]), ha="center", fontsize=12)
plt.legend(fontsize=20)
plt.tight_layout()
plt.savefig("symDataset/charts/bar-new-new-new-resize.pdf", bbox_inches="tight")
plt.show()
