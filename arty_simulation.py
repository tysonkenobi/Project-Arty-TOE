import numpy as np
import h5py
import time

# ==============================================================================
# NKST SIMULATION ENGINE (v2.2 - FIXED)
# Logic: The "McTwist" Vector Inversion Protocol
# ==============================================================================

class NKST_Universe:
    def __init__(self):
        print("[System] Initializing Minkowski Vacuum (Planck Normalized)...")
        self.PHI = 1.6180339887
        self.PLANCK_LIMIT = 1.0 
        
        # Metric (Geometry) and Ricci (Mass)
        self.g_tensor = np.zeros((4, 4))
        np.fill_diagonal(self.g_tensor, [-1.0, 1.0, 1.0, 1.0])
        self.R_tensor = np.zeros((4, 4))
        
        # Quantum Phase (Information)
        # Initialized with Phi to prevent resonance.
        self.I_tensor = np.zeros((4, 4), dtype=complex)
        self.I_tensor.fill(0 + 1j * self.PHI) 
        
        self.history = []
        self.t_step = 0

    def inject_mass(self, density_amount, axis=1):
        self.R_tensor[axis, axis] += density_amount
        # Update Metric Distortion (Gravity bends Space)
        # Simple linear approximation for demo
        if self.R_tensor[axis, axis] < 1.0:
             self.g_tensor[axis, axis] = 1.0 / (1.0 - self.R_tensor[axis, axis])

    def run_taber_phase_check(self):
        status_report = "Stable"
        for i in range(1, 4):
            local_density = self.R_tensor[i, i]
            
            # === THE BOUNDARY CONDITION ===
            if local_density >= self.PLANCK_LIMIT:
                # 1. THE ARROW OPERATOR (i -> -i)
                current_phase = self.I_tensor[i, i]
                
                # FIX APPLIED: Removed the (* -1.0) multiplier.
                # Conjugate of (bi) is (-bi). This is the correct inversion.
                new_phase = np.conj(current_phase) 
                
                self.I_tensor[i, i] = new_phase
                
                # 2. DATA CONSERVATION
                self.R_tensor[i, i] = self.PLANCK_LIMIT 
                status_report = "!!! INVERSION TRIGGERED (SPIN) !!!"
                
        return status_report

    def step(self):
        self.t_step += 1
        status = self.run_taber_phase_check()
        
        snapshot = {
            "time": self.t_step,
            "density_r": self.R_tensor[1, 1],
            "phase_imag": self.I_tensor[1, 1].imag, 
            "status": status
        }
        self.history.append(snapshot)
        return snapshot

    def export_data(self, filename="nkst_telemetry.h5"):
        # Extract columns
        t_series = [s["time"] for s in self.history]
        r_series = [s["density_r"] for s in self.history]
        i_series = [s["phase_imag"] for s in self.history] # Will now be negative after inversion

        with h5py.File(filename, "w") as f:
            f.create_dataset("time", data=t_series)
            f.create_dataset("density", data=r_series)
            f.create_dataset("phase_spin", data=i_series)
            f.attrs["engine_version"] = "2.2"

if __name__ == "__main__":
    sim = NKST_Universe()
    print("\n[Sim] Beginning Gravitational Collapse Sequence...")
    
    for t in range(25):
        sim.inject_mass(0.05) 
        data = sim.step()
        print(f"T={data['time']:02d} | Density: {data['density_r']:.3f} | Phase: {data['phase_imag']:.3f}j | {data['status']}")
        time.sleep(0.05)
        
    sim.export_data()
