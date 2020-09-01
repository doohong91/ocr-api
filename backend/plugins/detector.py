# import required libraries
import numpy as np
import cv2
import imutils
from django.core.files.uploadedfile import SimpleUploadedFile


class Detection:
    def __init__(self):
        self.original_img = None
        self.result_img = None
        self.bounding_boxes = {}

    def crop_roi(self, img, orig):
        """
        이미지에서 ROI(Region of Interest)영역 추출
        1. 원본 이미지 파일에서 표의 겉 테두리 윤곽선 추출
        2. 겉 테두리 윤곽선의 꼭지점 좌표 추출
        3. 꼭지점 좌표를 바탕으로 이미지 원근 변환을 통해 ROI영역 분리

        Keyword arguments:
            img -- image(.jpg/.png)
        """
        # 이미지 그레이 스케일 변환
        # - 이미지 내의 색깔에 따른 노이즈를 제거
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 이미지 필터링(가우시안 필터링)을 통해 노이즈 제거
        # - 그레이 스케일 이미지에서 컨투어(contour)를 찾아내기 위함
        gray_img_blur = cv2.GaussianBlur(gray_img, (5, 5), 1)
        # 캐니 엣지 추출법을 통해 이미지 경계선(윤곽선)을 추출
        edged_img = cv2.Canny(gray_img_blur, 50, 300, 3)

        # 경계선 이미지에서 컨투어 추출
        all_contours = cv2.findContours(edged_img.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        all_contours = imutils.grab_contours(all_contours)
        # 컨투어 영역 크기 순으로 내림차순하여 표의 겉테두리 프레임 영역(면적이 가장 큰 컨투어) 추출
        all_contours = sorted(all_contours, key=cv2.contourArea, reverse=True)[:1]

        try:
            # 컨투어 추정을 통한 표 테두리 영역 추출
            # - Douglas-Peucker 알고리즘을 이용해 컨투어 포인트를 줄임으로써 표 테두리 부분을 추정
            perimeter = cv2.arcLength(all_contours[0], True)
            roi_dimensions = cv2.approxPolyDP(all_contours[0], 0.05 * perimeter, True)
            roi_dimensions = roi_dimensions.reshape(4, 2)
        except Exception as ex:
            # 표의 테두리 부분(사각형 형태의 컨투어)를 추청하지 못하는 경우
            print("표 테두리를 발견하지 못했습니다.", ex)
            return img

        # 표 테두리의 좌표값 변환
        rect = np.zeros((4, 2), dtype="float32")
        # top left corner will have the smallest sum, bottom right corner will have the largest sum
        s = np.sum(roi_dimensions, axis=1)
        rect[0] = roi_dimensions[np.argmin(s)]
        rect[2] = roi_dimensions[np.argmax(s)]
        # top-right will have smallest difference, botton left will have largest difference
        diff = np.diff(roi_dimensions, axis=1)
        rect[1] = roi_dimensions[np.argmin(diff)]
        rect[3] = roi_dimensions[np.argmax(diff)]
        # top-left, top-right, bottom-right, bottom-left
        (tl, tr, br, bl) = rect

        # ROI 영역의 폭 계산
        width_a = np.sqrt((tl[0] - tr[0]) ** 2 + (tl[1] - tr[1]) ** 2)
        width_b = np.sqrt((bl[0] - br[0]) ** 2 + (bl[1] - br[1]) ** 2)
        max_width = max(int(width_a), int(width_b))
        # ROI 영역의 높이 계산
        height_a = np.sqrt((tl[0] - bl[0]) ** 2 + (tl[1] - bl[1]) ** 2)
        height_b = np.sqrt((tr[0] - br[0]) ** 2 + (tr[1] - br[1]) ** 2)
        max_height = max(int(height_a), int(height_b))

        # Set of destinations points for "birds eye view"
        # dimension of the new image
        dst = np.array(
            [[0, 0], [max_width - 1, 0], [max_width - 1, max_height - 1], [0, max_height - 1]],
            dtype="float32",
        )

        # 원근 변환(perspective transform)을 통해 이미지
        # 4영행렬(perspective transform matrix) 계산
        transform_matrix = cv2.getPerspectiveTransform(rect, dst)

        # ROI 영역 원근변환
        return cv2.warpPerspective(orig, transform_matrix, (max_width, max_height))

    def resize_image(self, img):
        """
        이미지에서 크기 조정
        1. 해상도가 높은 원본 이미지 파일의 크기 조정

        Keyword arguments:
            img -- image(.jpg/.png)
        """
        height, width, _ = img.shape
        if 1024 < height or 1024 < width:
            ratio = float(1024) / max(height, width)
            return cv2.resize(img, None, fx=ratio, fy=ratio)
        return img

    def remove_wm(self, img):
        """
        이미지에서 워터마크 제거
        1. 원본 이미지에서 워터마크 부분 분리
        2. 워터마크 영역에서 필요한 부분 분리
        3. 원본이미지에서 워터마크가 분리된 영역에 결합

        Keyword arguments:
            img -- image(.jpg/.png)
        """
        # 이미지 그레이 스케일 변환
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 그레이 스케일 이미지 복사
        # - 워터마크 영역의 필요한 부분을 분리하기 위함
        wm_img = gray_img.copy()

        # 형태학적 변환(morphological transformations)을 반복함으로써 워터마크 영역 판별
        for i in range(5):
            # 이미지 필터링을 통한 형태학적 변환 적용
            img_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * i + 1, 2 * i + 1))
            # 클로징(팽창기법 -> 침식기법 적용)을 통한 워터마크 윤곽 파악
            wm_img = cv2.morphologyEx(wm_img, cv2.MORPH_CLOSE, img_kernel)
            # 오프닝(침식기법 -> 팽창기법 적용)을 통한 노이즈 제거
            wm_img = cv2.morphologyEx(wm_img, cv2.MORPH_OPEN, img_kernel)

        # 그레이 스케일 이미지에서 워터마크 영역 제거
        dif_img = cv2.subtract(wm_img, gray_img)

        # 임계처리(thresholding)를 통한 이미지 이진화
        # - 이미지 이진화를 통해 불필요한 부분(그림자, 노이즈 등) 제거
        bw_img = cv2.threshold(dif_img, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        dark = cv2.threshold(wm_img, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

        # 이진화된 워터마크 이미지에서 어두운 부분 추출
        dark_pix = gray_img[np.where(dark > 0)]

        # 더 어두운 부분을 추출하기 위해 임계처리(thresholding) 진행
        dark_pix = cv2.threshold(dark_pix, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        # 이진화된 원본이미지에 워터마크 영역의 내용 추가
        bw_img[np.where(dark > 0)] = dark_pix.T
        return bw_img

    def get_frame(self, img):
        """
        표 이미지에서 모든 셀의 테두리 영역 추출
        1. 표의 모든 가로선, 세로선 추출
        2. 가로선과 세로선을 결합한 이미지 생성
        3. 선으로만 이루어진 이미지에서 모든 컨투어 추출
        4. 기준 크기 이상의 모든 컨투어를 좌표(x, y, w, h) 변환

        Keyword arguments:
            img -- grayscale image(.jpg/.png)
        """

        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 이미지 흑백 변환(검은색 <-> 흰색)
        inv_img = 255 - img

        # 커널의 크기 설정(전체 이미지 너비/50)
        kernel_len = np.array(img).shape[1] // 50
        # 모든 세로선을 추출하기 위해 세로 커널 정의
        ver_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_len))
        # 모든 가로선을 추출하기 위해 가로 커널 정의
        hor_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_len, 1))
        # 정사각형 커널(2x2 사이즈) 정의
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))

        # 오프닝을 반복해 노이즈가 제거된 세로선 추출
        vertical_lines = cv2.morphologyEx(inv_img, cv2.MORPH_OPEN, ver_kernel, iterations=3)

        # 오프닝을 반복해 노이즈가 제거된 가로선 추출
        horizontal_lines = cv2.morphologyEx(inv_img, cv2.MORPH_OPEN, hor_kernel, iterations=3)

        # 가로선과 세로선을 결합한 새로운 이미지 생성(가로와 세로에 같은 가중치를 부여)
        vh_img = cv2.addWeighted(vertical_lines, 1, horizontal_lines, 1, 0.0)
        # 커널 영역 팽창
        vh_img = cv2.erode(~vh_img, kernel, iterations=2)
        # 평균 이미지 명도를 기준으로 이미지 이진화(평균 이상 1, 평균 이하 0)
        frame_img = vh_img // int(np.mean(vh_img))

        # 컨투어 추출을 통해 사각형 영역 검출
        contours, hierarchy = cv2.findContours(frame_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        # 모든 컨투어 영역을 위에서 아래로 순서대로 정렬.
        bounding_boxes = [cv2.boundingRect(c) for c in contours]
        contours, bounding_boxes = zip(
            *sorted(zip(contours, bounding_boxes), key=lambda b: (b[1][1], b[1][0]), reverse=False)
        )
        self.bounding_boxes = {"boxes": bounding_boxes}

    def draw_frame(self, img):
        boxes = self.bounding_boxes.get("boxes")
        for x, y, w, h in boxes:
            if w > 30 or h > 30:
                box = np.array([[x, y], [x + w, y], [x + w, y + h], [x, y + h]], np.int32)
                cv2.polylines(img, [box], True, (0, 255, 0), 2)
        # for box in boxes:
        #     img = cv2.polylines(
        #         img, np.array(box, np.int32).reshape((-1, 1, 2)), True, (0, 255, 0), 2
        #     )
        return cv2.imencode(".jpg", img)[1].tostring()

    def detect(self, img_path, crop=True, watermark=False):

        # 이미지 불러오기
        orig = cv2.imdecode(np.fromstring(img_path.read(), np.uint8), cv2.IMREAD_UNCHANGED)
        img = orig.copy()

        if crop:
            # 이미지에서 ROI 영역 분리
            img = self.crop_roi(img, orig)

        # 이미지 해상도 축소 (image => 1024px)
        img = self.resize_image(img)

        self.original_img = cv2.imencode(".jpg", img)[1].tostring()

        if watermark:
            # 워터마크 삭제
            img_wm = self.remove_wm(img)

            # 이미지에서 표 프레임 영역 및 좌표값(x, y, w, h) 추출
            self.get_frame(img_wm)
        else:
            self.get_frame(img)

        self.result_img = self.draw_frame(img)

        result = {
            "original_img": SimpleUploadedFile("original_img.png", self.original_img),
            "result_img": SimpleUploadedFile("result_img.png", self.result_img),
            "bounding_boxes": self.bounding_boxes,
        }
        return result

