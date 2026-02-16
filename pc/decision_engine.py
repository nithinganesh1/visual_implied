#!/usr/bin/env python3
"""
Decision Engine - PC Optimized
Handles scene analysis and crossing safety logic
"""



from detector import ObjectDetector


class DecisionEngine:
    def __init__(self, audio_manager):
        self.audio = audio_manager

    # --------------------------------------------------
    # SCENE ANALYSIS
    # --------------------------------------------------

    def analyze_scene(self, detections, speak=True):
        """
        Analyze scene and optionally announce important objects.

        If `speak` is False the method returns the summary string but does
        not queue per-item TTS; this allows callers to speak a single
        concise summary themselves.
        """

        if not detections:
            if speak:
                self.audio.speak("No significant objects detected")
            return "No significant objects detected"

        objects_by_type = {}

        for det in detections:
            class_name = det["class"]
            objects_by_type.setdefault(class_name, []).append(det)
        announcements = []

        # Handle currency detections (announce denominations)
        currency_announcements = []
        currency_classes = getattr(ObjectDetector, "CURRENCY_CLASSES", set())
        for denom in sorted(currency_classes):
            if denom in objects_by_type:
                count = len(objects_by_type[denom])
                currency_announcements.append(f"{denom} rupee notes {count}")

        if currency_announcements:
            cur_msg = "Detected currency: " + ", ".join(currency_announcements)
            announcements.append(cur_msg)
            if speak:
                self.audio.speak(cur_msg, priority=2, obj_type="currency")

        # 1️⃣ VEHICLES (Highest Priority)
        if "vehicle" in objects_by_type:
            for vehicle in objects_by_type["vehicle"]:
                location = vehicle["location"]
                distance = vehicle["distance"]

                msg = f"Vehicle {distance} on {location}"
                announcements.append(msg)

                if speak:
                    self.audio.speak(
                        msg,
                        priority=1,
                        obj_type="vehicle"
                    )

        # 2️⃣ RED PEDESTRIAN LIGHT
        if "red_pedestrian_light" in objects_by_type:
            msg = "Red pedestrian light detected"
            announcements.append(msg)

            if speak:
                self.audio.speak(
                    msg,
                    priority=2,
                    obj_type="red_light"
                )

        # 3️⃣ GREEN PEDESTRIAN LIGHT
        elif "green_pedestrian_light" in objects_by_type:
            msg = "Green pedestrian light detected"
            announcements.append(msg)

            if speak:
                self.audio.speak(
                    msg,
                    priority=3,
                    obj_type="green_light"
                )

        # 4️⃣ ZEBRA CROSSING
        if "zebra" in objects_by_type:
            zebra = objects_by_type["zebra"][0]
            location = zebra["location"]
            distance = zebra["distance"]

            msg = f"Zebra crossing {distance} in {location}"
            announcements.append(msg)

            if speak:
                self.audio.speak(
                    msg,
                    priority=4,
                    obj_type="zebra"
                )

        # 5️⃣ OBSTACLES
        obstacle_types = ["bench", "stair", "Toilet"]

        friendly_names = {
            "Toilet": "restroom",
            "bench": "bench",
            "stair": "stairs",
        }

        for obstacle_type in obstacle_types:
            if obstacle_type in objects_by_type:
                obstacle = objects_by_type[obstacle_type][0]
                location = obstacle["location"]
                distance = obstacle["distance"]

                friendly = friendly_names.get(obstacle_type, obstacle_type)

                msg = f"{friendly.capitalize()} {distance} on {location}"
                announcements.append(msg)

                if speak:
                    self.audio.speak(
                        msg,
                        priority=5,
                        obj_type=obstacle_type
                    )

        return ". ".join(announcements)

    # --------------------------------------------------
    # CROSSING SAFETY CHECK
    # --------------------------------------------------

    def check_crossing_safety(self, detector, num_frames=5, interval=0.2):
        """
        Multi-frame crossing safety logic.
        """

    
        detections_over_time = detector.detect_continuous(
            num_frames=num_frames,
            interval=interval
        )

        if not detections_over_time:
            return False, "Unable to analyze scene"

        latest_detections = detections_over_time[-1]

        # 1️⃣ Zebra required
        zebra_detections = [
            d for d in latest_detections if d["class"] == "zebra"
        ]

        if not zebra_detections:
            return False, "No zebra crossing detected"

        # 2️⃣ Light check
        red_light = any(
            d["class"] == "red_pedestrian_light"
            for d in latest_detections
        )

        green_light = any(
            d["class"] == "green_pedestrian_light"
            for d in latest_detections
        )

        if red_light:
            return False, "Red pedestrian light detected"

        if not green_light:
            return False, "No green pedestrian light detected"

        # 3️⃣ Vehicle movement check
        moving_vehicles = detector.detect_vehicle_movement(
            detections_over_time
        )

        zebra_center = zebra_detections[0]["center"]

        for mv in moving_vehicles:
            vehicle_center = mv["detection"]["center"]

            horizontal_distance = abs(
                vehicle_center[0] - zebra_center[0]
            )

            if horizontal_distance < 200:
                return False, "Vehicle approaching crossing"

        return True, "Green light and no approaching vehicles"

    # --------------------------------------------------
    # QUICK WAIT CHECK
    # --------------------------------------------------

    def should_wait_at_crossing(self, detections):

        if any(d["class"] == "red_pedestrian_light" for d in detections):
            return True, "Red light"

        vehicles = [
            d for d in detections if d["class"] == "vehicle"
        ]

        for vehicle in vehicles:
            if vehicle["distance"] in ["very close", "near"]:
                return True, "Vehicle nearby"

        return False, "Clear"

    # --------------------------------------------------
    # OBSTACLE WARNINGS
    # --------------------------------------------------

    def get_obstacle_warnings(self, detections):

        warnings = []

        obstacle_classes = ["bench", "stair", "Toilet"]

        friendly_names = {
            "Toilet": "restroom",
            "bench": "bench",
            "stair": "stairs",
        }

        for det in detections:
            if det["class"] in obstacle_classes:
                if det["distance"] == "very close":
                    name = friendly_names.get(det["class"], det["class"])
                    msg = f"Warning. {name} very close on {det['location']}"
                    warnings.append(msg)

        return warnings
