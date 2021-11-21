import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from tqdm import tqdm
from PIL import Image
import random


DEFAULT_NEIGHBOURS = 5


class ImageFinder:
    """
    A finder able to find the most similar image (from a folder), to a given
    window.
    """
    def __init__(self, images_path, window_height, window_width):
        self.images_path = images_path
        self.window_height = window_height
        self.window_width = window_width

        self.dataset = None
        self.index_to_path = None
        self.classifier = None

    def prepare(self):
        """
        Prepare the images finder, precaching the source images and the
        classifier used to match them.
        """
        self._build_sources_dataset()
        self._build_classifier()

    def _build_sources_dataset(self):
        """
        Given a pathlib path of a folder with images, create a dataset of
        sources that can be used to find best fits for a window.
        """
        dataset = []
        self.index_to_path = {}
        for image_index, image_path in tqdm(list(enumerate(self.images_path.iterdir()))):
            image = Image.open(image_path)
            image_data = np.array(image.resize((self.window_width, self.window_height))).flatten()
            dataset.append(image_data)
            self.index_to_path[image_index] = image_path

        self.dataset = np.array(dataset)

    def _build_classifier(self):
        """
        Given a dataset of images, build a classifier able to find best fits
        from them.
        """
        self.classifier = KNeighborsClassifier(n_neighbors=1)
        self.classifier.fit(self.dataset, range(len(self.dataset)))

    def find(self, window, randomization_factor=DEFAULT_NEIGHBOURS):
        """
        Find the most similar image from the dataset, compared to a window.
        Return the path to the found image.
        randomization_factor is a number >= 1
        
        """
        inputs = np.array([window.flatten(), ])
        neighbours = self.classifier.kneighbors(inputs, n_neighbors=randomization_factor, return_distance=False)
        best_fit_index = random.choice(neighbours[0])
        return self.index_to_path[best_fit_index].name
