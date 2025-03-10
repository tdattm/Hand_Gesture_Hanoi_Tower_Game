import cv2
import mediapipe as mp
import numpy as np
import time

# Mediapipe Hand Detection
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Cấu hình các màn chơi
class HanoiGame:
    def __init__(self, levels=[(3, 7, 60), (4, 15, 90), (5, 31, 120)]):
        self.levels = levels  # Danh sách các màn chơi (số đĩa, giới hạn bước, giới hạn thời gian)
        self.current_level = 0
        self.num_disks, self.move_limit, self.time_limit = self.levels[self.current_level]
        self.pegs = [[i for i in range(self.num_disks, 0, -1)], [], []]
        self.selected_disk = None
        self.selected_peg = None
        self.holding_disk = False
        self.hand_position = (0, 0)
        self.move_count = 0
        self.last_selected_peg = None
        self.start_time = time.time()
        
        # Định nghĩa màu sắc cho các đĩa
        self.disk_colors = [(0, 0, 255), (255, 0, 0), (0, 255, 0), (255, 255, 255), (255, 0, 255), (0, 165, 255)]  # Đỏ, Xanh dương, Xanh lá, Trắng, Tím, Cam
        self.disk_color_map = {0: self.disk_colors[0], 1: self.disk_colors[1], 2: self.disk_colors[2], 3: self.disk_colors[3], 4: self.disk_colors[4], 5: self.disk_colors[5]}

    def check_game_over(self):
        return len(self.pegs[2]) == self.num_disks

    def check_time_out(self):
        return time.time() - self.start_time > self.time_limit

    def check_move_limit(self):
        return self.move_count >= self.move_limit

    def draw_hanoi(self, frame):
        height, width, _ = frame.shape
        peg_width = 20
        base_height = 50
        peg_height = 200
        disk_height = 30
        peg_positions = [width // 4, width // 2, 3 * width // 4]
        
        # Vẽ các cột và đĩa
        for i, peg in enumerate(self.pegs):
            cv2.rectangle(frame, (peg_positions[i] - peg_width//2, height - base_height - peg_height),
                          (peg_positions[i] + peg_width//2, height - base_height), (100, 100, 100), -1)
            
            for j, disk in enumerate(peg):
                color = self.disk_color_map[disk % 6]  # Chọn màu cho đĩa dựa trên chỉ số
                disk_width = 50 + disk * 20
                y_pos = height - base_height - (j+1) * disk_height
                
                if self.holding_disk and self.selected_disk == disk:
                    cv2.rectangle(frame, (self.hand_position[0] - disk_width//2, self.hand_position[1]),
                                  (self.hand_position[0] + disk_width//2, self.hand_position[1] + disk_height), color, -1)
                else:
                    cv2.rectangle(frame, (peg_positions[i] - disk_width//2, y_pos),
                                  (peg_positions[i] + disk_width//2, y_pos + disk_height), color, -1)
        
        # Hiển thị thông tin về trò chơi
        cv2.putText(frame, f"Moves: {self.move_count}/{self.move_limit}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Level: {self.current_level + 1}", (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.putText(frame, f"Time: {int(time.time() - self.start_time)}/{self.time_limit}s", (50, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Ký hiệu "Nguồn", "Trung gian", "Đích" dưới mỗi cột
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, "Source", (peg_positions[0] - 30, height - base_height + 30), font, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, "Medium", (peg_positions[1] - 60, height - base_height + 30), font, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, "Destination", (peg_positions[2] - 30, height - base_height + 30), font, 0.7, (0, 255, 255), 2)
        
        if self.check_game_over():
            self.next_level(frame, "Level Completed!")
        elif self.check_time_out() or self.check_move_limit():
            self.end_game(frame, "Game Over!")

    def next_level(self, frame, message):
        height, width, _ = frame.shape
        cv2.putText(frame, message, (width // 4, height // 2), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 3)
        cv2.imshow("Hanoi Tower with Hand Control", frame)
        cv2.waitKey(2000)
        
        if self.current_level < len(self.levels) - 1:
            self.current_level += 1
            self.num_disks, self.move_limit, self.time_limit = self.levels[self.current_level]
            self.pegs = [[i for i in range(self.num_disks, 0, -1)], [], []]
            self.selected_disk = None
            self.selected_peg = None
            self.holding_disk = False
            self.last_selected_peg = None
            self.move_count = 0
            self.start_time = time.time()
        else:
            self.end_game(frame, "Game Over!")

    def end_game(self, frame, message):
        height, width, _ = frame.shape
        cv2.putText(frame, message, (width // 3, height // 2), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
        cv2.imshow("Hanoi Tower with Hand Control", frame)
        cv2.waitKey(3000)
        cap.release()
        cv2.destroyAllWindows()
        exit()

    def move_disk(self, from_peg, to_peg):
        if self.pegs[from_peg] and (not self.pegs[to_peg] or self.pegs[from_peg][-1] < self.pegs[to_peg][-1]):
            self.pegs[to_peg].append(self.pegs[from_peg].pop())
            self.move_count += 1

# Mở camera
cap = cv2.VideoCapture(0)
game = HanoiGame()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    height, width, _ = frame.shape
    
    # Chuyển đổi ảnh sang RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            index_finger = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_finger = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            
            x = int(index_finger.x * width)
            y = int(index_finger.y * height)
            thumb_x = int(thumb_finger.x * width)
            thumb_y = int(thumb_finger.y * height)
            
            distance = np.sqrt((x - thumb_x) ** 2 + (y - thumb_y) ** 2)
            peg_positions = [width // 4, width // 2, 3 * width // 4]
            peg_detected = np.argmin([abs(x - pos) for pos in peg_positions])
            
            game.hand_position = (x, y)
            
            if not game.holding_disk and distance < 50:
                if game.pegs[peg_detected]:
                    game.selected_disk = game.pegs[peg_detected][-1]
                    game.selected_peg = peg_detected
                    game.holding_disk = True
            elif game.holding_disk and distance > 50:
                game.move_disk(game.selected_peg, peg_detected)
                game.holding_disk = False
    
    game.draw_hanoi(frame)
    cv2.imshow("Hanoi Tower with Hand Control", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
