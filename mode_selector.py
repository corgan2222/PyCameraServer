from render_modes import *

def draw_yolo_stats(input_frame, classes_index, font):
# Draw YOLO stats on frame

    # class_index_count = [
    #     [0 for x in range(80)] for x in range(len(stream_list))
    # ]
    class_index_count = [
        [0 for x in range(80)] for x in range(1)
    ]

    row_index = 1
    for m in range(80):
        for k in range(len(classes_index[0])):
            if m == classes_index[0][k]:
                class_index_count[0][m] += 1

        if class_index_count[0][m] != 0:
            row_index += 1

            if classes[m] == "person":
                cv2.rectangle(
                    input_frame,
                    (20, row_index * 40 - 25),
                    (270, row_index * 40 + 11),
                    (0, 0, 0),
                    -1,
                )
                cv2.putText(
                    input_frame,
                    classes[m] + ": " + str(class_index_count[0][m]),
                    (40, row_index * 40),
                    font,
                    1,
                    (0, 255, 0),
                    2,
                    lineType=cv2.LINE_AA,
                )

            if classes[m] == "car":
                cv2.rectangle(
                    input_frame,
                    (20, row_index * 40 - 25),
                    (270, row_index * 40 + 11),
                    (0, 0, 0),
                    -1,
                )
                cv2.putText(
                    input_frame,
                    classes[m] + ": " + str(class_index_count[0][m]),
                    (40, row_index * 40),
                    font,
                    1,
                    (255, 0, 255),
                    2,
                    lineType=cv2.LINE_AA,
                )

            if (classes[m] != "car") & (classes[m] != "person"):
                cv2.rectangle(
                    input_frame,
                    (20, row_index * 40 - 25),
                    (270, row_index * 40 + 11),
                    (0, 0, 0),
                    -1,
                )
                cv2.putText(
                    input_frame,
                    classes[m] + ": " + str(class_index_count[0][m]),
                    (40, row_index * 40),
                    font,
                    1,
                    colors_yolo[m],
                    2,
                    lineType=cv2.LINE_AA,
                )

            # Example of handbag detection
            if (classes[m] == "handbag") | (classes[m] == "backpack"):
                passFlag = True
                print("handbag detected! -> PASS")

    return input_frame

def render_with_mode(requested_modes_dictionary, sliders_dictionary, main_frame, frame_background,
                     f, f1, yolo_network, rcnn_network, caffe_network, superres_network,
                     dain_network, esrgan_network, device, output_layers, classes_index, zip_obj, zip_is_opened,
                     zipped_images, server_states, started_rendering_video
):
    # YOLO Modes
    if requested_modes_dictionary["using_yolo_network"]:
        # Find all boxes with classes
        boxes, indexes, class_ids, confidences, classes_out = find_yolo_classes(
            main_frame, yolo_network, output_layers, int(sliders_dictionary["confidenceSliderValue"])
        )
        classes_index.append(classes_out)

        # Draw boxes with labels on frame
        # Extract all image regions with objects and add them to zip
        if requested_modes_dictionary["extract_objects_yolo_mode"]:
            main_frame, zipped_images, zip_obj, zip_is_opened = extract_objects_yolo(
                main_frame,
                boxes,
                indexes,
                class_ids,
                confidences,
                zip_obj,
                zip_is_opened,
                zipped_images,
                server_states.source_mode,
                started_rendering_video,
            )

        # If it is image, close zip immediately
        if server_states.source_mode == "image" and zip_is_opened:
            zip_obj.close()

        # Prepare zip to reopening
        if server_states.source_mode == "image" and zipped_images == False:
            zipped_images = True
            zip_is_opened = False

        # Draw YOLO objects with ASCII effect
        if requested_modes_dictionary["text_render_yolo"]:
            main_frame = objects_to_text_yolo(
                main_frame,
                boxes,
                indexes,
                class_ids,
                int(sliders_dictionary["asciiSizeSliderValue"]),
                int(sliders_dictionary["asciiIntervalSliderValue"]),
                int(sliders_dictionary["rcnnBlurSliderValue"]),
                int(sliders_dictionary["asciiThicknessSliderValue"]),
            )

        # Draw YOLO objects with canny edge detection on black background
        if requested_modes_dictionary["canny_people_on_black"]:
            main_frame = canny_people_on_black_yolo(
                main_frame, boxes, indexes, class_ids
            )

        # Draw YOLO objects with canny edge detection on source colored background
        if requested_modes_dictionary["canny_people_on_background"]:
            main_frame = canny_people_on_background_yolo(
                main_frame, boxes, indexes, class_ids
            )

    # MASK R-CNN Modes
    if requested_modes_dictionary["using_mask_rcnn_network"]:
        # Find all masks with classes
        boxes, masks, labels, colors = find_rcnn_classes(main_frame, rcnn_network)

        # Convert background to grayscale and add color objects
        if requested_modes_dictionary["color_objects_on_gray"]:
            main_frame = colorizer_people_rcnn(
                main_frame, boxes, masks, int(sliders_dictionary["confidenceSliderValue"]), int(sliders_dictionary["rcnnSizeSliderValue"])
            )

        # Convert background to grayscale with blur and add color objects
        if requested_modes_dictionary["color_objects_on_gray_blur"]:
            main_frame = colorizer_people_with_blur_rcnn(
                main_frame, boxes, masks, int(sliders_dictionary["confidenceSliderValue"])
            )

        # Blur background behind RCNN objects
        if requested_modes_dictionary["color_objects_blur"]:
            main_frame = people_with_blur_rcnn(
                main_frame,
                boxes,
                masks,
                labels,
                int(sliders_dictionary["confidenceSliderValue"]),
                int(sliders_dictionary["rcnnSizeSliderValue"]),
                int(sliders_dictionary["rcnnBlurSliderValue"]),
            )

        # Draw MASK R-CNN objects with canny edge detection on black background
        if requested_modes_dictionary["extract_and_cut_background"]:
            main_frame = extract_and_cut_background_rcnn(
                main_frame, boxes, masks, labels, int(sliders_dictionary["confidenceSliderValue"])
            )

        # Draw MASK R-CNN objects on animated background
        if requested_modes_dictionary["extract_and_replace_background"]:
            main_frame = extract_and_replace_background_rcnn(
                main_frame,
                frame_background,
                boxes,
                masks,
                labels,
                colors,
                int(sliders_dictionary["confidenceSliderValue"]),
            )

        # Draw MASK R-CNN objects with canny edge detection on canny blurred background
        if requested_modes_dictionary["color_canny"]:
            main_frame = color_canny_rcnn(
                main_frame, boxes, masks, labels, int(sliders_dictionary["confidenceSliderValue"]), int(sliders_dictionary["rcnnBlurSliderValue"]),
            )

        # Draw MASK R-CNN objects with canny edge detection on source background
        if requested_modes_dictionary["color_canny_on_background"]:
            main_frame = color_canny_on_color_background_rcnn(
                main_frame, boxes, masks, labels, int(sliders_dictionary["confidenceSliderValue"])
            )

    # Grayscale frame color restoration with caffe neural network
    if requested_modes_dictionary["using_caffe_network"]:
        if requested_modes_dictionary["caffe_colorization"]:
            main_frame = colorizer_caffe(caffe_network, main_frame)

    # Cartoon effect (canny, dilate, color quantization with k-means, denoise, sharpen)
    if requested_modes_dictionary["cartoon_effect"]:
        frame_copy = main_frame.copy()

        if int(sliders_dictionary["cannyBlurSliderValue"]) % 2 == 0:
            sliders_dictionary["cannyBlurSliderValue"] += int(sliders_dictionary["cannyBlurSliderValue"]) + 1
            main_frame = cv2.GaussianBlur(
                main_frame, (int(sliders_dictionary["cannyBlurSliderValue"]), int(sliders_dictionary["cannyBlurSliderValue"])), int(sliders_dictionary["cannyBlurSliderValue"]),
            )
        else:
            main_frame = cv2.GaussianBlur(
                main_frame, (int(sliders_dictionary["cannyBlurSliderValue"]), int(sliders_dictionary["cannyBlurSliderValue"])), int(sliders_dictionary["cannyBlurSliderValue"]),
            )

        main_frame = cv2.Canny(main_frame, int(sliders_dictionary["cannyThres1SliderValue"]), int(sliders_dictionary["cannyThres2SliderValue"]))
        main_frame = cv2.cvtColor(main_frame, cv2.COLOR_GRAY2BGR)
        kernel = np.ones((int(sliders_dictionary["lineThicknessSliderValue"]), int(sliders_dictionary["lineThicknessSliderValue"])), np.uint8)
        main_frame = cv2.dilate(main_frame, kernel, iterations=1)
        frame_copy[np.where((main_frame > [0, 0, 0]).all(axis=2))] = [0, 0, 0]
        frame_copy = limit_colors_kmeans(frame_copy, int(sliders_dictionary["colorCountSliderValue"]))
        # frame_copy = cv2.GaussianBlur(frame_copy, (3, 3), 2)
        main_frame = frame_copy
        main_frame = sharpening(main_frame, int(sliders_dictionary["sharpenSliderValue"]), int(sliders_dictionary["sharpenSliderValue2"]))
        main_frame = denoise(main_frame, int(sliders_dictionary["denoiseSliderValue"]), int(sliders_dictionary["denoise2SliderValue"]))
        main_frame = cv2.GaussianBlur(main_frame, (3,3), 1)

    # Pencil drawer (canny, k-means quantization to 2 colors, denoise)
    if requested_modes_dictionary["pencil_drawer"]:
        frame_copy = main_frame.copy()

        if int(sliders_dictionary["cannyBlurSliderValue"]) % 2 == 0:
            sliders_dictionary["cannyBlurSliderValue"] = int(sliders_dictionary["cannyBlurSliderValue"]) + 1
            main_frame = cv2.GaussianBlur(
                main_frame, (int(sliders_dictionary["cannyBlurSliderValue"]), int(sliders_dictionary["cannyBlurSliderValue"])), int(sliders_dictionary["cannyBlurSliderValue"]),
            )
        else:
            main_frame = cv2.GaussianBlur(
                main_frame, (int(sliders_dictionary["cannyBlurSliderValue"]), int(sliders_dictionary["cannyBlurSliderValue"])), int(sliders_dictionary["cannyBlurSliderValue"]),
            )

        # main_frame = morph_edge_detection(main_frame)
        main_frame = cv2.Canny(main_frame, int(sliders_dictionary["cannyThres1SliderValue"]), int(sliders_dictionary["cannyThres1SliderValue"]))
        main_frame = cv2.cvtColor(main_frame, cv2.COLOR_GRAY2BGR)
        kernel = np.ones((int(sliders_dictionary["lineThicknessSliderValue"]), int(sliders_dictionary["lineThicknessSliderValue"])), np.uint8)
        main_frame = cv2.dilate(main_frame, kernel, iterations=1)
        frame_copy[np.where((main_frame > [0, 0, 0]).all(axis=2))] = [0, 0, 0]
        frame_copy = limit_colors_kmeans(frame_copy, 2)
        # frame_copy = cv2.GaussianBlur(frame_copy, (3, 3), 2)
        main_frame = frame_copy
        main_frame = sharpening(main_frame, int(sliders_dictionary["sharpenSliderValue"]), int(sliders_dictionary["sharpenSliderValue2"]))
        main_frame = denoise(main_frame, int(sliders_dictionary["denoiseSliderValue"]), int(sliders_dictionary["denoise2SliderValue"]))
        # main_frame = np.bitwise_not(main_frame)

    # Pencil drawer (k-means quantization to 2 colors, denoise)
    if requested_modes_dictionary["two_colored"]:
        frame_copy = main_frame.copy()
        # main_frame = morph_edge_detection(main_frame)
        kernel = np.ones((int(sliders_dictionary["lineThicknessSliderValue"]), int(sliders_dictionary["lineThicknessSliderValue"])), np.uint8)
        # main_frame = cv2.dilate(main_frame,kernel,iterations = 1)
        # frame_copy[np.where((main_frame > [0, 0, 0]).all(axis=2))] = [0,0,0]
        frame_copy = limit_colors_kmeans(frame_copy, 2)
        # frame_copy = cv2.GaussianBlur(frame_copy, (3, 3), 2)
        main_frame = frame_copy
        main_frame = sharpening(main_frame, int(sliders_dictionary["sharpenSliderValue"]), int(sliders_dictionary["sharpenSliderValue2"]))
        main_frame = denoise(main_frame, int(sliders_dictionary["denoiseSliderValue"]), int(sliders_dictionary["denoise2SliderValue"]))

    # Super-resolution upscaler with EDSR, LapSRN and FSRCNN
    if requested_modes_dictionary["upscale_opencv"]:
        main_frame = upscale_with_superres(superres_network, main_frame)
        main_frame = sharpening(main_frame, int(sliders_dictionary["sharpenSliderValue"]), int(sliders_dictionary["sharpenSliderValue2"]))

    # Super-resolution upscaler with ESRGAN (FALCOON, MANGA, PSNR models)
    if requested_modes_dictionary["upscale_esrgan"]:
        main_frame = upscale_with_esrgan(esrgan_network, device, main_frame)
        main_frame = sharpening(main_frame, int(sliders_dictionary["sharpenSliderValue"]), int(sliders_dictionary["sharpenSliderValue2"]))

    # Draw frame with ASCII chars
    if requested_modes_dictionary["ascii_painter"]:
        main_frame = ascii_paint(
            main_frame,
            int(sliders_dictionary["asciiSizeSliderValue"]),
            int(sliders_dictionary["asciiIntervalSliderValue"]),
            int(sliders_dictionary["asciiThicknessSliderValue"]),
            int(sliders_dictionary["rcnnBlurSliderValue"]),
        )

    # Denoise and sharpen
    if requested_modes_dictionary["denoise_and_sharpen"]:
        main_frame = sharpening(main_frame, int(sliders_dictionary["sharpenSliderValue"]), int(sliders_dictionary["sharpenSliderValue2"]))
        main_frame = denoise(main_frame, int(sliders_dictionary["denoiseSliderValue"]), int(sliders_dictionary["denoise2SliderValue"]))

    # Sobel filter
    if requested_modes_dictionary["sobel"]:
        main_frame = denoise(main_frame, int(sliders_dictionary["denoiseSliderValue"]), int(sliders_dictionary["denoise2SliderValue"]))
        main_frame = sharpening(main_frame, int(sliders_dictionary["sharpenSliderValue"]), int(sliders_dictionary["sharpenSliderValue2"]))
        grad_x = cv2.Sobel(main_frame, cv2.CV_64F, 1, 0, ksize=int(sliders_dictionary["sobelSliderValue"]))
        grad_y = cv2.Sobel(main_frame, cv2.CV_64F, 0, 1, ksize=int(sliders_dictionary["sobelSliderValue"]))
        main_frame = cv2.addWeighted(grad_x, 0.5, grad_y, 0.5, 0)

    # Boost fps with Depth-Aware Video Frame Interpolation
    # Process interpolation only if user pressed START button
    frame_boost_sequence = None
    frame_boost_list = None
    if requested_modes_dictionary["boost_fps_dain"] and started_rendering_video:
        frame_boost_sequence, frame_boost_list = boost_fps_with_dain(
            dain_network, f, f1, True
        )

    # Apply brightness and contrast settings for all modes
    main_frame = adjust_br_contrast(main_frame, int(sliders_dictionary["contrastSliderValue"]), int(sliders_dictionary["brightnessSliderValue"]))
    main_frame = adjust_saturation(main_frame, int(sliders_dictionary["saturationSliderValue"]))

    return main_frame, frame_boost_sequence, frame_boost_list, classes_index, zipped_images, zip_obj, zip_is_opened