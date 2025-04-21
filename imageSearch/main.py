import os
import cv2
import numpy as np
from DeepImageSearch import Load_Data, Search_Setup
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

class ImageViewer:
    def __init__(self):
        self.images = []
        self.titles = []
        self.current_idx = 0
        self.window_names = []

    def add_image(self, image, title):
        """Add an image with title"""
        self.images.append(image)
        self.titles.append(title)
        self.window_names.append(f"Window_{len(self.images)}")

    def show_opencv_windows(self):
        """Display all images in separate OpenCV windows"""
        for img, title, win_name in zip(self.images, self.titles, self.window_names):
            cv2.namedWindow(win_name, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
            cv2.imshow(win_name, img)
            cv2.setWindowTitle(win_name, title)
        
        print("\nOpenCV Window Controls:")
        print("- Press 'n' to cycle through windows")
        print("- Press 'm' to switch to Matplotlib view")
        print("- Press ESC or 'q' to quit")
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord('q'):
                break
            elif key == ord('n'):
                self._cycle_opencv_windows()
            elif key == ord('m'):
                cv2.destroyAllWindows()
                self.show_matplotlib_view()
                return
        
        cv2.destroyAllWindows()

    def _cycle_opencv_windows(self):
        """Cycle through OpenCV windows"""
        self.current_idx = (self.current_idx + 1) % len(self.images)
        for i, win_name in enumerate(self.window_names):
            if i == self.current_idx:
                cv2.moveWindow(win_name, 100, 100)
                cv2.setWindowProperty(win_name, cv2.WND_PROP_TOPMOST, 1)
            else:
                cv2.setWindowProperty(win_name, cv2.WND_PROP_TOPMOST, 0)

    def show_matplotlib_view(self):
        """Display images in Matplotlib with navigation"""
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        plt.subplots_adjust(bottom=0.2)
        
        # Add navigation buttons
        ax_prev = plt.axes([0.3, 0.05, 0.1, 0.075])
        ax_next = plt.axes([0.6, 0.05, 0.1, 0.075])
        btn_prev = Button(ax_prev, 'Previous')
        btn_next = Button(ax_next, 'Next')
        
        btn_prev.on_clicked(self._prev_image)
        btn_next.on_clicked(self._next_image)
        
        self._update_matplotlib_display()
        plt.show()

    def _update_matplotlib_display(self):
        """Update the Matplotlib display"""
        self.ax.clear()
        img_rgb = cv2.cvtColor(self.images[self.current_idx], cv2.COLOR_BGR2RGB)
        self.ax.imshow(img_rgb)
        self.ax.set_title(self.titles[self.current_idx], fontsize=12, pad=10)
        self.ax.axis('off')
        self.fig.canvas.draw()

    def _next_image(self, event):
        if self.current_idx < len(self.images) - 1:
            self.current_idx += 1
            self._update_matplotlib_display()

    def _prev_image(self, event):
        if self.current_idx > 0:
            self.current_idx -= 1
            self._update_matplotlib_display()

def main():
    # Configuration
    os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
    DATASET_FOLDER = 'images_for_project'
    QUERY_IMAGE = r'C:\Users\Konan\OneDrive\Desktop\SAP\plagiarism-project\imageSearch\input_image.jpg'
    
    viewer = ImageViewer()
    
    try:
        print("1. Loading image dataset...")
        image_list = Load_Data().from_folder([DATASET_FOLDER])
        
        print("2. Initializing search engine...")
        st = Search_Setup(
            image_list=image_list,
            model_name='vgg19',
            pretrained=True,
            image_count=len(image_list)
        )
        
        print("3. Creating search index...")
        st.run_index()
        
        print("4. Processing your image...")
        input_img = cv2.imread(QUERY_IMAGE)
        if input_img is None:
            raise FileNotFoundError(f"Input image not found at {QUERY_IMAGE}")
        
        # Get top matches
        results = st.get_similar_images(QUERY_IMAGE, number_of_images=2)
        
        if not results:
            print("No similar images found!")
            return
            
        # Add original image
        viewer.add_image(input_img, "Original Image")
        
        # Add matches
        for i, idx in enumerate(results, 1):
            match_img = cv2.imread(image_list[idx])
            if match_img is not None:
                viewer.add_image(match_img, f"Match {i}")
        
        # Let user choose view mode
        print("\nChoose display mode:")
        print("1. Native OpenCV windows (best quality)")
        print("2. Matplotlib view (easier comparison)")
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == "2":
            viewer.show_matplotlib_view()
        else:
            viewer.show_opencv_windows()
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        cv2.destroyAllWindows()
        plt.close('all')

if __name__ == "__main__":
    main()




# import os
# import cv2
# from DeepImageSearch import Load_Data, Search_Setup

# os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# # Load image dataset
# image_list = Load_Data().from_folder(['images_for_project'])

# # Setup search
# st = Search_Setup(
#     image_list=image_list,
#     model_name='vgg19',
#     pretrained=True,
#     image_count=len(image_list)
# )

# # Run indexing
# st.run_index()

# # Set query image path
# query_image_path = r'C:\Users\Konan\OneDrive\Desktop\SAP\plagiarism-project\imageSearch\input_image.jpg'

# # Show the input image first using OpenCV
# input_img = cv2.imread(query_image_path)
# if input_img is not None:
#     cv2.imshow("Input Image", input_img)
#     cv2.waitKey(1000)  # Show for 1 second, or use 0 to wait for key press

# # Search similar images
# results = st.get_similar_images(image_path=query_image_path, number_of_images=5)

# # Print the results
# print("Top similar images:")
# for i, idx in enumerate(results, 1):
#     print(f"{i}. Image index: {idx}")

# # Convert indices to paths
# image_paths = [image_list[idx] for idx in results]

# # Show similar images using OpenCV
# try:
#     for i, path in enumerate(image_paths, 1):
#         img = cv2.imread(path, cv2.IMREAD_COLOR)
#         if img is not None:
#             cv2.imshow(f"Result {i}", img)
#             cv2.waitKey(0)
#         else:
#             print(f"Warning: Image {path} could not be loaded.")
# except KeyboardInterrupt:
#     print("Process interrupted. Exiting gracefully...")
# finally:
#     cv2.destroyAllWindows()



# import os
# os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# from DeepImageSearch import Load_Data, Search_Setup
# import matplotlib.pyplot as plt

# # Load image dataset
# image_list = Load_Data().from_folder(['images_for_project'])

# # Setup search
# st = Search_Setup(
#     image_list=image_list,
#     model_name='vgg19',
#     pretrained=True,
#     image_count=len(image_list)
# )

# # Run indexing
# st.run_index()

# # Set query image path separately
# query_image_path = r'C:\Users\Konan\OneDrive\Desktop\SAP\plagiarism-project\imageSearch\input_image.jpg'

# # Search similar images
# results = st.get_similar_images(image_path=query_image_path, number_of_images=5)

# # Print results
# print("Top similar images:")
# for path in results:
#     print(path)

# # Optionally display results
# st.plot_similar_images(image_path=query_image_path, number_of_images=5)
# plt.show()












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
