import numpy as np
import h5py
import time
import os

# ==============================================================================
#  NKST SIMULATION ENGINE (v2.1)
#  Project: Plan Breakthrough
#  Logic: The "McTwist" Vector Inversion Protocol
#  Equation: g_mu_nu * ln( I_mu_nu / Phi_mu_nu ) = - (G * h / c^3) * R_mu_nu
# ==============================================================================

class NKST_Universe:
    def __init__(self):
        """
        Initialize the Space-Time Manifold.
        Uses Strict Planck Unit Normalization (G=1, h=1, c=1).
        """
        print("[System] Initializing Minkowski Vacuum (Planck Normalized)...")
        
        # 1. CONSTANTS
        self.PHI = 1.6180339887  # The Golden Ratio (Geometric Compression)
        self.PLANCK_LIMIT = 1.0  # The Hard "Pixel" Limit of Reality
        
        # 2. TENSORS (4x4 Matrices for Space-Time)
        # g_tensor: The Metric (Geometry). Default = Minkowski Flat (-1, 1, 1, 1)
        self.g_tensor = np.zeros((4, 4))
        np.fill_diagonal(self.g_tensor, [-1.0, 1.0, 1.0, 1.0])

        # R_tensor: The Ricci Curvature (Gravity/Mass). 
        self.R_tensor = np.zeros((4, 4))

        # I_tensor: The Quantum Phase (Information). 
        # Stores Complex Amplitudes. Initialized with Phi to prevent resonance.
        self.I_tensor = np.zeros((4, 4), dtype=complex)
        self.I_tensor.fill(0 + 1j * self.PHI) 

        # Telemetry Storage
        self.history = []
        self.t_step = 0

    def inject_mass(self, density_amount, axis=1):
        """
        Simulates matter falling into the coordinate system.
        Increases Curvature (R) at the specified spatial axis.
        """
        self.R_tensor[axis, axis] += density_amount
        
        # Update Metric Distortion (Gravity bends Space)
        # Simple linear approximation for demo purposes
        self.g_tensor[axis, axis] = 1.0 / (1.0 - self.R_tensor[axis, axis])

    def run_taber_phase_check(self):
        """
        THE CORE LOGIC: The Vector Inversion Monitor.
        Checks if local density has hit the Planck Wall (1.0).
        If YES -> Trigger 'The McTwist' (Reflect Vector).
        """
        status_report = "Stable"
        
        # Iterate through spatial dimensions (1, 2, 3)
        for i in range(1, 4):
            local_density = self.R_tensor[i, i]
            
            # === THE BOUNDARY CONDITION ===
            if local_density >= self.PLANCK_LIMIT:
                
                # 1. THE ARROW OPERATOR ($i \to -i$)
                # We do not stop. We do not crash. We Invert.
                current_phase = self.I_tensor[i, i]
                
                # Logic: Take Conjugate and Flip Sign
                # This converts Linear Compression into Angular Momentum (Spin)
                new_phase = np.conj(current_phase) * -1.0
                
                self.I_tensor[i, i] = new_phase
                
                # 2. DATA CONSERVATION
                # The mass is now "encrypted" in the spin.
                # We clamp R at the wall so the math doesn't explode.
                self.R_tensor[i, i] = self.PLANCK_LIMIT
                
                status_report = "!!! INVERSION TRIGGERED !!!"
                
        return status_report

    def step(self):
        """
        Execute one Clock Cycle (Delta-t).
        """
        self.t_step += 1
        
        # 1. Run Physics Checks
        status = self.run_taber_phase_check()
        
        # 2. Capture Telemetry Snapshot
        # We track the 'Heartbeat' of the singularity
        snapshot = {
            "time": self.t_step,
            "density_r": self.R_tensor[1, 1],        # Gravity
            "phase_imag": self.I_tensor[1, 1].imag,  # Quantum Potential
            "metric_g": self.g_tensor[1, 1],         # Space Deformation
            "status": status
        }
        self.history.append(snapshot)
        return snapshot

    def export_data(self, filename="nkst_telemetry.h5"):
        """
        Save simulation state to HDF5 for the Scanner.
        """
        print(f"\n[IO] Exporting Telemetry to {filename}...")
        
        # Extract columns
        t_series = [s["time"] for s in self.history]
        r_series = [s["density_r"] for s in self.history]
        i_series = [s["phase_imag"] for s in self.history]
        
        with h5py.File(filename, "w") as f:
            f.create_dataset("time", data=t_series)
            f.create_dataset("density", data=r_series)
            f.create_dataset("phase_spin", data=i_series)
            
            # Store Metadata
            f.attrs["engine_version"] = "2.1"
            f.attrs["logic"] = "Vector Inversion"
            
        print("[IO] Export Complete. Ready for Scanner.")

# ==============================================================================
#  EXECUTION LOOP
# ==============================================================================
if __name__ == "__main__":
    print("--- INITIATING NKST SIMULATION ---")
    
    # 1. Instantiate Universe
    sim = NKST_Universe()
    
    # 2. Run Simulation: " The Fall "
    # We will push mass into the grid until it breaks the Planck Limit
    print("\n[Sim] Beginning Gravitational Collapse Sequence...")
    
    # Run for 20 steps
    for t in range(20):
        # Inject Mass (Gravity increases)
        sim.inject_mass(0.06) # Adds 0.06 density per step
        
        # Process Physics
        data = sim.step()
        
        # Visual Log
        # Watch the 'Phase' column. Positive = Linear Fall. Negative = Spin.
        print(f"T={data['time']:02d} | Density: {data['density_r']:.3f} | Phase Vector: {data['phase_imag']:.3f}j | {data['status']}")
        
        time.sleep(0.1)

    # 3. Save Data
    sim.export_data()
