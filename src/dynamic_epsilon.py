from decimal import getcontext
from transformers import AutoTokenizer
import numpy as np
import json
import tqdm
from typing import List
def compute_p_j(tokens, sensitive_words, window_size, index):
    
    L = len(tokens)
    start = index
    end = min(index + window_size, L)
    window_tokens = tokens[start:end]

    n_j = sum(1 for t in window_tokens if t in sensitive_words)
    w_j = (end - start) if end > start else 1  
    p_j = n_j / w_j
    return p_j

def compute_dynamic_epsilon(p_j, epsilon_max):
    if p_j == 1:
        return epsilon_max * 10.0
    return epsilon_max * np.exp(p_j / (p_j - 1))
def cosine_similarity_vectors(A, B):
    dot_product = np.dot(A, B)
    norm_a = np.linalg.norm(A)
    norm_b = np.linalg.norm(B)
    similarity = dot_product / (norm_a * norm_b)
    return similarity


def add_laplace_noise_to_vector(vector, epsilon, delta_f_new):
    vector = np.asarray(vector, dtype=np.longdouble)
    if epsilon == 0:
        beta_values = delta_f_new * 0
    else:
        beta_values = delta_f_new / (0.5 * epsilon)
    noise = np.random.laplace(loc=0, scale=beta_values, size=len(beta_values))
    noisy_vector = vector + noise

    return noisy_vector


def perturb_sentence(sent,
                     epsilon_max,
                     tokenizer,
                     token_to_vector_dict,
                     sorted_distance_data,
                     delta_f_new,
                     sensitive_words,
                     window_size=5):
    tokens = tokenizer.tokenize(sent)
    new_tokens = []
    Delta_u = 1.0

    dynamic_epsilons = []
    for i in range(len(tokens)):
        p_j = compute_p_j(tokens, sensitive_words, window_size, i)
        epsilon_d = compute_dynamic_epsilon(p_j, epsilon_max=epsilon_max)
        dynamic_epsilons.append(epsilon_d)

    for i, origin_token in enumerate(tokens):
        if origin_token[0] == ' ':
            origin_token = origin_token[1:]
        origin_embed = token_to_vector_dict.get(origin_token, None)
        if origin_embed is None:
            new_tokens.append(origin_token)
            continue

        epsilon_d = dynamic_epsilons[i]
        exp_factor = epsilon_d / (2 * Delta_u)

        noise_embed = add_laplace_noise_to_vector(origin_embed, epsilon_d, delta_f_new)
        similarity = cosine_similarity_vectors(origin_embed, noise_embed)
        sorted_distances_for_token = sorted_distance_data.get(origin_token, None)
        if sorted_distances_for_token is None or len(sorted_distances_for_token) < 2:
            new_tokens.append(origin_token)
            continue
        token_only = sorted_distances_for_token[0]
        similarity_only = sorted_distances_for_token[1]
        arr = np.flip(similarity_only)
        index = np.searchsorted(arr, similarity)
        index = len(arr) - index
        close_tokens = token_only[:index]
        close_similarities = similarity_only[:index]
        if len(close_tokens) == 0:
            new_tokens.append(origin_token)
            continue
        unnormalized_probabilities = np.exp(exp_factor * np.array(close_similarities))
        total_unnormalized_prob = np.sum(unnormalized_probabilities)
        probabilities = unnormalized_probabilities / total_unnormalized_prob
        selected_token = np.random.choice(close_tokens, p=probabilities)
        new_tokens.append(selected_token)

    token_ids = tokenizer.convert_tokens_to_ids(new_tokens)
    sentence = tokenizer.decode(token_ids)
    return sentence
