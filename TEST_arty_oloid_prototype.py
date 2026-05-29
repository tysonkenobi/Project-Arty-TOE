import numpy as np


class AISemanticBoundaryEngineFixed:
    """A corrected proof-of-concept engine that utilizes the golden ratio decay

    to break state-lock deadlocks and restore normal AI generation windows.
    """

    def __init__(self, baseline_temperature: float = 0.8):
        self.PHI = 1.618033988749895
        self.LIMIT = 1.0

        # Operational metrics
        self.accumulated_entropy = 0.0
        self.baseline_temp = baseline_temperature
        self.current_temp = baseline_temperature

        # 1.0 = Accumulating Stress, -1.0 = Active Dissipation
        self.operational_mode = 1.0

    def process_token_metrics(self, raw_token_entropy: float) -> dict:
        """Processes token stream parameters.

        Applies an analytical 1/phi^3 decay factor to ensure safe recovery loops.
        """
        # Calculate background dissipation using the 1/phi^3 rule
        # This provides a constant relaxation pressure on the system load
        background_decay = 1.0 / (self.PHI**3)  # Approx 0.236

        if self.operational_mode > 0:
            # Normal state: build stress based on token inputs
            self.accumulated_entropy += raw_token_entropy
        else:
            # Active mitigation state: drain stress using background decay properties
            # This ensures that even with 0.0 input, the system clears its load
            self.accumulated_entropy -= background_decay

        # Rigid boundary enforcement
        self.accumulated_entropy = np.clip(
            self.accumulated_entropy, 0.0, self.LIMIT
        )

        status = "NORMAL_GENERATION"

        # The Inversion Trigger Boundary
        if self.accumulated_entropy >= self.LIMIT and self.operational_mode > 0:
            self.operational_mode = -1.0
            status = "[!] HORIZON BREACHED: ENFORCING MAXIMUM CONSTRAINT"
            self.current_temp = 0.01

        elif self.operational_mode < 0:
            status = "[>] MITIGATION ACTIVE: DRAINING LATENT ENTROPY"

            # Dynamically recalculate decoding temperature based on remaining load
            recovery_ratio = 1.0 - (self.accumulated_entropy / self.LIMIT)
            self.current_temp = self.baseline_temp * recovery_ratio

            # Clean reset condition: return to baseline generation mode
            if self.accumulated_entropy <= 0.01:
                self.operational_mode = 1.0
                self.current_temp = self.baseline_temp
                status = "[*] COGNITIVE FLOW STABILIZED"

        return {
            "current_entropy": float(self.accumulated_entropy),
            "applied_temperature": float(self.current_temp),
            "system_status": status,
        }


if __name__ == "__main__":
    engine = AISemanticBoundaryEngineFixed(baseline_temperature=0.8)
    print("=== Fixed AI Token Stream Guardrail Run ===")

    # Test stream: 5 steps of rising entropy, followed by 5 steps of zero input
    simulated_entropy_input = [0.1, 0.2, 0.3, 0.3, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0]

    for step, token_entropy in enumerate(simulated_entropy_input):
        data = engine.process_token_metrics(token_entropy)
        print(
            f"Token {step:02d} | Input Entropy: {token_entropy:.2f} | "
            f"Accumulated Load: {data['current_entropy']:.3f} | "
            f"Temp: {data['applied_temperature']:.3f} | {data['system_status']}"
        )
