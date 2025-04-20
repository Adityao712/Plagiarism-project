from DeepImageSearch import Load_Data, Search_Setup
import matplotlib.pyplot as plt

# Load image dataset
image_list = Load_Data().from_folder(['images_for_project'])

# Setup search
st = Search_Setup(
    image_list=image_list,
    model_name='vgg19',
    pretrained=True,
    image_count=len(image_list)
)

# Run indexing
st.run_index()

# Set query image path separately
query_image_path = r'C:\Users\Konan\OneDrive\Desktop\SAP\plagiarism-project\imageSearch\input_image.jpg'

# Search similar images
results = st.get_similar_images(image_path=query_image_path, number_of_images=5)

# Print results
print("Top similar images:")
for path in results:
    print(path)

# Optionally display results
st.plot_similar_images(image_path=query_image_path, number_of_images=5)












# from DeepImageSearch import Load_Data, Search_Setup
# import matplotlib.pyplot as plt

# # Load your image dataset folder
# image_list = Load_Data().from_folder(['images_for_project'])

# # Setup image search
# st = Search_Setup(
#     image_list=image_list,
#     model_name='vgg19',
#     pretrained=True,
#     image_count=len(image_list)
# )

# # Run indexing ONCE
# st.run_index()

# # Input image to search with (any image, even outside dataset)
# query_image_path = query_image_path = query_image_path = r'C:\Users\Konan\OneDrive\Desktop\SAP\plagiarism-project\imageSearch\input_image.jpg'



# # Get similar images
# results = st.get_similar_images(image_path=query_image_path = query_image_path = r'C:\Users\Konan\OneDrive\Desktop\SAP\plagiarism-project\imageSearch\input_image.jpg'

# , number_of_images=5)

# # Print the paths of similar images
# print("Top similar images:")
# for path in results:
#     print(path)

# # Display results (optional)
# st.plot_similar_images(image_path=query_image_path =query_image_path = r'C:\Users\Konan\OneDrive\Desktop\SAP\plagiarism-project\imageSearch\input_image.jpg'

# , number_of_images=5)
