import tensorflow as tf
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
from PIL import Image
from scipy.cluster.hierarchy import linkage, dendrogram
import matplotlib.pyplot as plt

base_model = ResNet50(weights='imagenet', include_top=False, pooling='avg')

def extract_features(img_path):
    img = Image.open(img_path)
    img = img.resize((224, 224))  # Resize image to the input size expected by ResNet-50
    img_array = np.array(img)
    img_array = preprocess_input(img_array)  # Preprocess input according to ResNet-50 requirements
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    features = base_model.predict(img_array)
    return features.flatten()

images_dir = "./downloaded_images"
image_paths = [os.path.join(images_dir, img) for img in sorted(os.listdir(images_dir))[0:50] if img.endswith(('.png', '.jpg', '.jpeg'))]

print("extracting features")
# Extract features from each image
feature_matrix = np.array([extract_features(img_path) for img_path in image_paths])


print("Computing sim scores")
# pairwise cosine similarity
similarity_matrix = cosine_similarity(feature_matrix)

plt.figure(figsize=(10, 8))
plt.imshow(similarity_matrix, cmap='autumn', interpolation='nearest')
plt.colorbar(label='Cosine Similarity')
plt.xticks(np.arange(len(image_paths)), [os.path.splitext(os.path.basename(path))[0] for path in image_paths], rotation='vertical')
plt.yticks(np.arange(len(image_paths)), [os.path.splitext(os.path.basename(path))[0] for path in image_paths])
plt.title('Similarity Matrix Heatmap')
plt.show()

linkage_matrix = linkage(similarity_matrix, method='average')

# Plot dendrogram with image names as labels
plt.figure(figsize=(12, 8))
dendrogram(linkage_matrix, labels=[os.path.splitext(os.path.basename(path))[0] for path in image_paths], orientation='left')
plt.title('Hierarchical Clustering Dendrogram')
plt.xlabel('Distance between clusters')
plt.show()