def get_subtraction_steps(initial_value, target_value, steps):
    """
    Returns a list of equal subtraction amounts to adjust initial_value to target_value in specified steps.
    Works for both positive and negative differences (uses abs() for step calculation).

    Args:
        initial_value (int/float): Starting value.
        target_value (int/float): Target value.
        steps (int): Number of subtraction steps.

    Returns:
        list: Equal amounts to subtract in each step (sign indicates direction).
              Empty list if steps <= 0 or if no adjustment is needed.
    """
    difference = initial_value - target_value
    if steps <= 0:
        return []  # Invalid step count

    if difference == 0:
        return []  # No adjustment needed

    step_amount = abs(difference) / steps
    # Determine the sign: subtract if initial > target, add if initial < target
    signed_step = -step_amount if difference > 0 else step_amount

    return [signed_step] * steps


# Ejemplo de uso / Example usage:
initial_value = 206
target_value = 958
steps = 8

subtraction_list = get_subtraction_steps(initial_value, target_value, steps)
print(f"Subtracting from {initial_value} to {target_value} in {steps} steps:")
for step, amount in enumerate(subtraction_list):
    print(f"Step {step}: Subtract {amount}")