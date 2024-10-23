def scale_to_fit(
        original_x: float, original_y: float, bound_x: float, bound_y: float
    ) -> tuple[float, float]:
        """
        Given a bounding box and some dimensions, scale down/up the dimensions
        such that they fit (maximally) within the bounding box.
        """
        scale = min(1, bound_x / original_x, bound_y / original_y)
        scaled_x = original_x * scale
        scaled_y = original_y * scale
        scale_up = min(bound_x / scaled_x, bound_y / scaled_y)
        return (scaled_x * scale_up, scaled_y * scale_up)
