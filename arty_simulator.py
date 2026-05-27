import numpy as np
import h5py
import time

# ==============================================================================
# NKST SIMULATION ENGINE (v2.3 - RELATIVISTIC BUILD)
# Architect: Tyson N. Taber
# Logic: Vector Inversion Protocol + Relativistic Time Dilation (1/Phi^3)
# ==============================================================================

class NKST_Universe:
    def __init__(self):
        print("[System] Initializing Minkowski Vacuum (Planck Normalized)...")
        self.PHI = 1.6180339887
        self.PLANCK_LIMIT = 1.0
        
        # Metric (Geometry) and Ricci (Mass)
        # g_tensor: The fabric of space-time (Metric).
        # R_tensor: The mass/energy curving that fabric (Curvature).
        self.g_tensor = np.zeros((4, 4))
        np.fill_diagonal(self.g_tensor, [-1.0, 1.0, 1.0, 1.0])
        self.R_tensor = np.zeros((4, 4))
        
        # Quantum Phase (Information)
        # Initialized with Phi to prevent integer harmonic resonance.
        self.I_tensor = np.zeros((4, 4), dtype=complex)
        self.I_tensor.fill(0 + 1j * self.PHI)
        
        self.history = []
        self.t_step = 0.0  # Float precision required for relativistic drift

    def inject_mass(self, density_amount, axis=1):
        self.R_tensor[axis, axis] += density_amount
        
        # Update Metric Distortion (Gravity bends Space)
        # As R -> 1.0, the Metric denominator -> 0 (Infinite Curve).
        if self.R_tensor[axis, axis] < 1.0:
            self.g_tensor[axis, axis] = 1.0 / (1.0 - self.R_tensor[axis, axis])

    def run_taber_phase_check(self):
        status_report = "Stable"
        for i in range(1, 4):
            local_density = self.R_tensor[i, i]
            
            # === THE BOUNDARY CONDITION (The Taber Phase) ===
            if local_density >= self.PLANCK_LIMIT:
                # 1. THE ARROW OPERATOR (i -> -i)
                # Instead of a Singularity (Crash), we invert the Vector.
                current_phase = self.I_tensor[i, i]
                
                # CRITICAL LOGIC: The Conjugate Flip.
                # Input: Linear Compression (+i)
                # Output: Rotational Spin (-i)
                # Result: Conservation of Information via Phase Shift.
                new_phase = np.conj(current_phase)
                self.I_tensor[i, i] = new_phase
                
                # 2. DATA CONSERVATION LOCK
                # Prevent density from exceeding the Planck "Pixel Size".
                self.R_tensor[i, i] = self.PLANCK_LIMIT
                status_report = "!!! INVERSION TRIGGERED (SPIN) !!!"
                
        return status_report

    def step(self):
        # === PATCH v2.3: RELATIVISTIC TIME DILATION ===
        # Problem: Linear time (t+=1) skips the Event Horizon transition.
        # Solution: We apply Gravitational Time Dilation.
        # As Local Density approaches the Limit, the local clock slows down.
        
        current_density = self.R_tensor[1, 1]
        
        # The "Ring Width" Factor: 1 / Phi^3 (~0.236)
        # This geometric constant governs the compression rate of the horizon.
        compression_factor = 1.0 / (self.PHI ** 3)

        if current_density > 0.0:
             # DYNAMIC DELTA-T (The Zeno Effect)
             # As Density -> 1.0, dt -> 0.0.
             # This allows the simulation to render "Infinite Time" inside
             # a finite loop, capturing the micro-physics of the Inversion.
             drag = 1.0 + (current_density / compression_factor)
             dt = 1.0 / drag
             self.t_step += dt
        else:
             self.t_step += 1.0 # Vacuum Baseline (Newtonian Time)
        # ==============================================

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
        # Extract columns for visualization
        t_series = [s["time"] for s in self.history]
        r_series = [s["density_r"] for s in self.history]
        i_series = [s["phase_imag"] for s in self.history] 
        
        with h5py.File(filename, "w") as f:
            f.create_dataset("time", data=t_series)
            f.create_dataset("density", data=r_series)
            f.create_dataset("phase_spin", data=i_series)
            f.attrs["engine_version"] = "2.3 (Relativistic)"

if __name__ == "__main__":
    sim = NKST_Universe()
    print("\n[Sim] Beginning Gravitational Collapse Sequence...")
    print("[Sim] Mode: Relativistic (Time Dilation Active)")
    
    # We run 50 loops, but 'SimTime' will lag behind due to gravity.
    for t in range(50): 
        sim.inject_mass(0.025) 
        data = sim.step()
        
        # Note the divergence between 'Loop' and 'SimTime'
        print(f"Loop={t:02d} | SimTime={data['time']:06.3f} | Density: {data['density_r']:.3f} | {data['status']}")
        
        time.sleep(0.02)
    
    sim.export_data()
    print("\n[System] Telemetry Exported to 'nkst_telemetry.h5'.")
