import random
import numpy as np

from ui_classes import textures, conditions, num_participants, trials_per_texture


def generate_random_orders(num_participants, textures):
    file_path = f"order.csv"
    participants_data = []

    for participant in range(0, num_participants*len(conditions)):
        random_repeated_textures = textures * trials_per_texture
        random.shuffle(random_repeated_textures)
        print(participant, random_repeated_textures)
        participants_data.append(random_repeated_textures)

    np.savetxt(file_path, participants_data, delimiter=",", fmt='%s')

# Generate the randomized orders
generate_random_orders(num_participants, textures)
