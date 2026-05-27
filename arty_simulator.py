import numpy as np
import h5py
import time

# ==============================================================================
# NKST SIMULATION ENGINE (v2.5 - HYBRID PHYSICS BUILD)
# Logic: Matter freezes (Time Dilation) | Energy escapes (Golden Decay)
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
        self.I_tensor = np.zeros((4, 4), dtype=complex)
        self.I_tensor.fill(0 + 1j * self.PHI)
        
        self.history = []
        self.t_step = 0.0 
        self.dt = 0.0 

    def inject_mass(self, density_amount, axis=1):
        self.R_tensor[axis, axis] += density_amount
        if self.R_tensor[axis, axis] < 1.0:
            self.g_tensor[axis, axis] = 1.0 / (1.0 - self.R_tensor[axis, axis])

    def run_taber_phase_check(self):
        status_report = "Stable"
        for i in range(1, 4):
            local_density = self.R_tensor[i, i]
            current_phase = self.I_tensor[i, i]
            
            # === THE BOUNDARY CONDITION ===
            if local_density >= self.PLANCK_LIMIT:
                
                # STATE CHECK: Falling or Spinning?
                if current_phase.imag > 0:
                    # === EVENT A: THE INVERSION (Impact) ===
                    # The "McTwist". Matter hits the Planck Wall.
                    new_phase = np.conj(current_phase)
                    self.I_tensor[i, i] = new_phase
                    status_report = "!!! INVERSION (IMPACT) !!!"
                    
                else:
                    # === EVENT B: THE RINGDOWN (Entropy) ===
                    # Physics Fix: Gravitational Waves (Energy) escape at 'c'.
                    # They decay according to the Golden Ratio Observer Metric.
                    decay_factor = 1.0 / self.PHI
                    self.I_tensor[i, i] = current_phase * decay_factor
                    status_report = ">>> RINGDOWN (DECAY) >>>"

                # Lock Density (Frozen Star)
                self.R_tensor[i, i] = self.PLANCK_LIMIT
                
        return status_report

    def step(self):
        # === RELATIVISTIC TIME DILATION (Affects Clock, not Waves) ===
        current_density = self.R_tensor[1, 1]
        compression_factor = 1.0 / (self.PHI ** 3)

        if current_density > 0.0:
             drag = 1.0 + (current_density / compression_factor)
             self.dt = 1.0 / drag 
             self.t_step += self.dt
        else:
             self.dt = 1.0
             self.t_step += 1.0

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
        t_series = [s["time"] for s in self.history]
        r_series = [s["density_r"] for s in self.history]
        i_series = [s["phase_imag"] for s in self.history] 
        
        with h5py.File(filename, "w") as f:
            f.create_dataset("time", data=t_series)
            f.create_dataset("density", data=r_series)
            f.create_dataset("phase_spin", data=i_series)
            f.attrs["engine_version"] = "2.5 (Hybrid)"

if __name__ == "__main__":
    sim = NKST_Universe()
    print("\n[Sim] Beginning Gravitational Collapse Sequence...")
    
    for t in range(40): 
        sim.inject_mass(0.04) 
        data = sim.step()
        # Printing minimal info to keep terminal clean
        if t % 5 == 0 or data['phase_imag'] < 0:
            print(f"Loop={t:02d} | Phase: {data['phase_imag']:.4f}j | {data['status']}")
        time.sleep(0.02)
    
    sim.export_data()
    print("[System] Telemetry Exported.")
