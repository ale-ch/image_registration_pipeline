import pickle

def save_pickle(object, path):
    # Open a file in binary write mode
    with open(path, 'wb') as file:
        # Serialize the object and write it to the file
        pickle.dump(object, file)

def load_pickle(path):
    # Open the file in binary read mode
    with open(path, 'rb') as file:
    # Deserialize the object from the file
        loaded_data = pickle.load(file)

    return loaded_data