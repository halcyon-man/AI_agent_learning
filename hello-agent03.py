# N-gram模型简单示例 计算 datawhale agent learns 出现的概率

import collections

from huggingface_hub import Collection

# 示例语料库，与上方案例讲解中的语料库保持一致
corpus = "datawhale agent learns datawhale agent works"
tokens = corpus.split()
total_tokens = len(tokens)

print(tokens)
print(total_tokens)
# 第一步计算datawhale 出现的概率
count_datawhale = tokens.count("datawhale")
p_datawhale = count_datawhale / total_tokens


# 第二步，计算 datawhale agent 出现的概率
count_agent = tokens.count("agent")
bigrams = zip(tokens,tokens[1:])
bigrams_count = collections.Counter(bigrams)
print(bigrams_count)

count_da_ag=bigrams_count[('datawhale','agent')]

p_da_ag = count_da_ag / count_datawhale

# 第三步，计算agent learns 的概率
count_ag_le = bigrams_count[('agent','learns')]
p_ag_le = count_ag_le / count_agent


# 第四步，计算概率乘积
result = p_datawhale * p_da_ag * p_ag_le


print(f'datawhale agent learns 出现的概率为{result:.5f}')

