import numpy as np
import cv2
import cv2.aruco as aruco
import os
from collections import deque

class ArucoDetector:
    def __init__(self, calibration_file="camera_calibration.xml"):
        self.calibration_file = calibration_file
        self.camera_matrix = None
        self.dist_coeffs = None
        
        self.load_calibration()
        
        # ArUco dictionary and parameters
        self.aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
        self.aruco_params = aruco.DetectorParameters()
        
        # Create the ArUco detector
        self.detector = aruco.ArucoDetector(self.aruco_dict, self.aruco_params)
        
        self.show_id = True
        self.show_distance = True
        
        self._pose_history = {}   
        self._smooth_n = 6 
        
    def load_calibration(self):
        """Load camera calibration from XML file"""
        if os.path.exists(self.calibration_file):
            try:
                fs = cv2.FileStorage(self.calibration_file, cv2.FILE_STORAGE_READ)
                
                if fs.isOpened():
                    self.camera_matrix = fs.getNode("camera_matrix").mat()
                    self.dist_coeffs = fs.getNode("distortion_coefficients").mat()
                    fs.release()
                    
                    print(f">>> Calibration loaded from {self.calibration_file}")
                    print(f"Camera matrix:\n{self.camera_matrix}")
                    print(f"Distortion coefficients:\n{self.dist_coeffs}")
                    return True
                    
            except Exception as e:
                print(f"[error] calibração não foi carregada: {e}")
                
        print("[warning] No calibration file found.")
        return False
    
    def detect_markers(self, frame):
        """
        Detect ArUco markers in the frame
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect markers
        corners, ids, rejected = self.detector.detectMarkers(gray)
        
        # Draw detected markers
        frame_with_markers = frame.copy()
        
        if ids is not None and len(ids) > 0:
            # Draw markers
            aruco.drawDetectedMarkers(frame_with_markers, corners, ids)
            
            # If we have calibration, we can estimate pose
            if self.camera_matrix is not None and self.dist_coeffs is not None:
                self.estimate_pose_and_draw(corners, ids, frame_with_markers)
        
        return corners, ids, frame_with_markers
    
    def estimate_pose_and_draw(self, corners, ids, frame, marker_length=0.05):
        """
        Draw marker axes using solvePnP for accurate 3D pose.
        All axes (X, Y, Z) share the same origin point.
        """
        h, w = frame.shape[:2]
        
        for i, corner in enumerate(corners):
            #  Pontos 2D correspondentes na imagem (u, v)
            pts = corner[0].astype(np.float32)   # shape (4, 2)
            marker_id = int(ids[i][0])

            # 2D geometry from the bounding box
            tl = pts[0]   # top-left
            tr = pts[1]   # top-right
            br = pts[2]   # bottom-right
            bl = pts[3]   # bottom-left

            # Centre of the marker (intersection of diagonals) - COMMON ORIGIN
            origin_2d = ((tl + br) / 2).astype(int)

            # Axis vectors in pixels (half-side length each)
            x_vec = ((tr - tl) / 2)   # points right  → X axis (red)
            y_vec = ((bl - tl) / 2)   # points down   → Y axis (green)

            x_end = (origin_2d + x_vec).astype(int)
            y_end = (origin_2d + y_vec).astype(int)

            #  Helper: clip endpoint to image bounds 
            def in_frame(pt):
                return 0 <= pt[0] < w and 0 <= pt[1] < h

            orig_t = tuple(origin_2d)

            # X axis – Red (using 2D bounding box method)
            if in_frame(x_end):
                cv2.line(frame, orig_t, tuple(x_end), (0, 0, 255), 2)
                cv2.putText(frame, "X", (x_end[0] + 5, x_end[1] - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            # Y axis – Green (using 2D bounding box method)
            if in_frame(y_end):
                cv2.line(frame, orig_t, tuple(y_end), (0, 255, 0), 2)
                cv2.putText(frame, "Y", (y_end[0] + 5, y_end[1] - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Centre dot – Yellow (common origin for all axes)
            cv2.circle(frame, orig_t, 4, (0, 255, 255), -1)

            # Z axis using solvePnP
            L = marker_length / 2

            #  Pontos 3D no sistema do objeto (X_w, Y_w, Z_w)
            obj_points = np.array([
                [-L,  L, 0],
                [ L,  L, 0],
                [ L, -L, 0],
                [-L, -L, 0],
            ], dtype=np.float32)

            # Perceived marker size in pixels (used to cap axis length)
            side_px = (
                np.linalg.norm(pts[1] - pts[0]) +
                np.linalg.norm(pts[2] - pts[1]) +
                np.linalg.norm(pts[3] - pts[2]) +
                np.linalg.norm(pts[0] - pts[3])
            ) / 4

            # Pose estimation
            # solvePnP resolve [R|t] e λ implicitamente
            ret, rvec, tvec = cv2.solvePnP(
                obj_points, pts,
                self.camera_matrix, self.dist_coeffs,
                flags=cv2.SOLVEPNP_ITERATIVE
            )
            
            if ret and tvec[2, 0] > 0:
                # Sliding-window median smoothing per marker ID
                if marker_id not in self._pose_history:
                    self._pose_history[marker_id] = deque(maxlen=self._smooth_n)
                self._pose_history[marker_id].append(
                    (rvec.copy().flatten(), tvec.copy().flatten())
                )
                hist = self._pose_history[marker_id]
                rvecs_h = np.array([p[0] for p in hist])
                tvecs_h = np.array([p[1] for p in hist])
                rvec_smooth = np.median(rvecs_h, axis=0).reshape(3, 1)
                tvec_smooth = np.median(tvecs_h, axis=0).reshape(3, 1)

                # Project Z axis
                z_tip_3d = np.array([[0, 0, L]], dtype=np.float32)
                z_tip_2d, _ = cv2.projectPoints(
                    z_tip_3d, rvec_smooth, tvec_smooth, 
                    self.camera_matrix, self.dist_coeffs
                )
                
                # Calculate Z axis direction from the common origin
                z_tip_px = z_tip_2d[0, 0]
                vec_z = z_tip_px - origin_2d
                
                # Cap Z axis length to marker perceived size
                max_len = side_px * 0.7
                vec_len = np.linalg.norm(vec_z)
                
                if vec_len > max_len and vec_len > 0:
                    vec_z = vec_z * (max_len / vec_len)
                
                # Calculate Z endpoint (using the SAME origin as X and Y)
                z_end = (int(origin_2d[0] + vec_z[0]), 
                        int(origin_2d[1] + vec_z[1]))
                
                # Clip to frame bounds
                z_end = (np.clip(z_end[0], 0, w-1), np.clip(z_end[1], 0, h-1))

                # Draw Z axis – Blue (from common origin)
                cv2.line(frame, orig_t, z_end, (255, 0, 0), 2)
                cv2.putText(frame, "Z", (z_end[0] + 4, z_end[1] - 4),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)


                
    
    def run_live_detection(self, camera_id=0, mirror=False):
        """
        Run real-time ArUco marker detection using webcam
        
        Args:
            camera_id: Camera device ID (default 0 for built-in webcam)
            mirror: Flip frame horizontally (if using front-facing camera)
        """
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            print(f"Error: Could not open camera {camera_id}")
            return
        
        # Set resolution (optional)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)   # reduce capture buffer lag
        
        print("\n=== ArUco Marker Detection ===")
        print("Press 'q' to quit")
        print("Press 'd' to show debug information")
        print("-" * 35)
        
        show_debug = False
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame")
                break
            
            # Mirror if needed
            if mirror:
                frame = cv2.flip(frame, 1)
            
            # Detect markers
            corners, ids, frame_with_markers = self.detect_markers(frame)
            
            # Reset smoothing when nothing visible
            if ids is None or len(ids) == 0:
                self._pose_history.clear()
            
            # Add information overlay
            if ids is not None and len(ids) > 0:
                detected_text = f"Detected {len(ids)} marker(s)"
                cv2.putText(
                    frame_with_markers,
                    detected_text,
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )
            else:
                cv2.putText(
                    frame_with_markers,
                    "No markers detected",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2
                )
            
            # Show calibration status and toggles
            calib_status = "Calibrated" if self.camera_matrix is not None else "No Calibration"
            id_s = "ID:ON" if self.show_id else "ID:OFF"
            dist_s = "Dist:ON" if self.show_distance else "Dist:OFF"
            cv2.putText(
                frame_with_markers,
                f"{calib_status} | {id_s} | {dist_s} | q=quit i=ID t=Dist m=mirror d=debug",
                (10, frame.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1
            )
            
            # Show frame
            cv2.imshow("ArUco Marker Detection", frame_with_markers)
            
            # Show debug window if enabled
            if show_debug and corners and len(corners) > 0:
                debug_frame = frame.copy()
                gray = cv2.cvtColor(debug_frame, cv2.COLOR_BGR2GRAY)
                
                # Draw corners
                for corner in corners:
                    for point in corner[0]:
                        cv2.circle(debug_frame, tuple(point.astype(int)), 3, (0, 255, 0), -1)
                
                cv2.imshow("Debug - Corners", debug_frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('d'):
                show_debug = not show_debug
                if not show_debug:
                    cv2.destroyWindow("Debug - Corners")
        
        cap.release()
        cv2.destroyAllWindows()





def main():
    """Main function"""
    print("\n=== ArUco Marker Detection with Camera Calibration ===")
    
    # Check if calibration file exists
    calibration_file = "camera_calibration.xml"
    if os.path.exists(calibration_file):
        print(f"[pass] Found calibration file: {calibration_file}")
    else:
        print(f"[warning] Calibration file not found: {calibration_file}")
        print("  Running without distortion correction")
        print("  Run cam_calib_copy.py first for better accuracy")
    
    # Choose dictionary
    print("\nArUco dictionary:")
    print("DICT_6X6_250 (default)")
    
    # Create detector
    detector = ArucoDetector(calibration_file)
    
    # Start detection
    print("\nStarting ArUco marker detection...")
    detector.run_live_detection(camera_id=0, mirror=True)


if __name__ == "__main__":
    main()