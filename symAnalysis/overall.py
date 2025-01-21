import matplotlib.pyplot as plt
import matplotlib.image as mpimg

plt.style.use('ggplot')
plt.figure(figsize=[24, 6])
models = 'GLM-4-9B-Chat DeepSeek-V2-Lite-Chat Baichuan2-7B-Chat Baichuan2-13B-Chat Vicuna-7B-V1.5-16K Vicuna-13B-V1.5-16K Mistral-7B-Instruct Mistral-Nemo-Instruct Llama3.1-8B-Instruct Llama3.1-70B-Instruct Qwen2.5-3B-Instruct Qwen2.5-7B-Instruct Qwen2.5-Coder-7B-Instruct Qwen2.5-14B-Instruct Qwen2.5-72B-Instruct Gemma2-2B-It Gemma2-9B-It Gemma2-27B-It TableGPT2-7B TableLlama GPT-4o-mini GPT-4o'.split()
values = '29.18 21.93 21.25 3.68 20.64 13.64 20.09 23.96 40.21 54.61 26.50 43.93 44.21 46.00 43.80 28.14 38.17 42.86 37.93 0.00 56.07 70.81'.split()
values = [float(item) for item in values]
colors = ['red'] * 6 + ['blue'] * 12 + ['yellow'] * 2 + ['green'] * 2
labels = ['Chat Models'] + [None] * 5 + ['Instruct Models'] + [None] * 11 + ['Table Specific Models', None] + ['Close-Source Models', None]
x = list(range(22))
plt.xticks(x, models, fontsize=12, weight='bold')
plt.bar(x, values, color=colors, alpha=0.6, label=labels, width=0.6)
plt.xticks(rotation=45, ha='right')

for i in range(len(values)):
    plt.text(i, values[i], str(values[i]), ha='center', fontsize=12)
plt.legend(fontsize=20)
plt.tight_layout()
plt.savefig('symDataset/charts/bar.pdf', bbox_inches='tight')
plt.show()
