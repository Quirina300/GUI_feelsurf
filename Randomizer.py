import random
import numpy as np

# Parameters
num_participants = 20  # Adjust this as needed
textures = ["Wood", "RoughFoam", "Texture 3","Texture 4","Texture 5"]  # List of textures
file_path = f"order.csv"
def generate_random_orders(num_participants, textures, repeat=3, conditions=2):
    print(type(len(textures)))
    participants_data = []

    for participant in range(0, num_participants*conditions):
        randomized_pairs = textures * repeat
        random.shuffle(randomized_pairs)
        print(participant, randomized_pairs)
        participants_data.append(randomized_pairs)

    np.savetxt(file_path, participants_data, delimiter=",", fmt='%s')

# Function to generate random order for each participant
def generate_random_order(num_participants, textures, repeat=1):
    all_pairs = [(texture) for texture in textures]
    participants_data = {}
    for participant in range(1, num_participants + 1):
        randomized_pairs = all_pairs * repeat  # Repeat each pair twice
        random.shuffle(randomized_pairs)
        participants_data[participant] = randomized_pairs
    
    return participants_data

# Generate the randomized orders
random_orders = generate_random_orders(num_participants, textures)
random_orders = generate_random_order(num_participants, textures)

# # Print the results
# for participant, pairs in random_orders.items():
#     print(f"Participant {participant}:")
#     for i, (texture) in enumerate(pairs, start=1):
#         print(f"  {i}. {texture}")
#     print()  # Add a blank line for readability

# #Save file
# with open("randomized_orders.txt", "w") as file:
#     for participant, pairs in random_orders.items():
#         file.write(f"Participant {participant}:\n")
#         for i, (texture) in enumerate(pairs, start=1):
#             file.write(f"  {i}. {texture}\n")
#         file.write("\n")  # Add a blank line for readability
