import numpy as np
import h5py
import time
import os

# ==============================================================================
# NKST SIMULATION ENGINE (v3.9 - RIGOROUS LINEAR INTERSECT BUILD)
# Core Logic: Matter Freezes (Time Dilation) | Energy Escapes (Golden Decay)
# Fix: Linear density accumulation that naturally strikes and cycles the wall
# ==============================================================================

class NKST_Universe:
    def __init__(self):
        print("[System] Initializing Minkowski Vacuum (Planck Normalized)...")
        self.PHI = 1.6180339887
        self.PLANCK_LIMIT = 1.0
        self.EPSILON = 1e-9  # Rigorous floating-point guardrail from v2.6
        
        # Metric Tensor (Geometry) and Ricci Tensor (Mass-Density Distribution)
        self.g_tensor = np.zeros((4, 4))
        np.fill_diagonal(self.g_tensor, [-1.0, 1.0, 1.0, 1.0])
        self.R_tensor = np.zeros((4, 4))
        
        # Quantum Phase Space (Information Topology)
        self.I_tensor = np.zeros((4, 4), dtype=complex)
        self.I_tensor.fill(0 + 1j * self.PHI)
        
        self.history = []
        self.t_step = 0.0
        self.dt = 1.0

    def inject_mass(self, density_amount, axis=1):
        """
        Carries forward the authentic linear mass accumulation from v2.5/2.6.
        Allows density to grow cleanly right into the boundary layer.
        """
        # Linear accumulation allows the system to cross the threshold naturally
        self.R_tensor[axis, axis] += density_amount
        
        # Calculate metric tensor geometry using the v2.6 precision protection barrier
        denominator = 1.0 - self.R_tensor[axis, axis]
        
        # If mass accumulation hits or passes the horizon, we clamp the denominator 
        # to self.EPSILON to prevent mathematical collapse (ZeroDivisionError)
        if denominator < self.EPSILON:
            denominator = self.EPSILON
            
        self.g_tensor[axis, axis] = 1.0 / denominator

    def run_taber_phase_check(self):
        """
        AUTHENTIC BOUNDARY LOGIC: Evaluates state changes at the true Planck Wall.
        Triggers Event A (Inversion) and Event B (Ringdown Mass Decay) dynamically.
        """
        status_report = "Stable"
        
        for i in range(1, 4):
            local_density = self.R_tensor[i, i]
            current_phase = self.I_tensor[i, i]
            
            # Fire transitions the moment the density breaches or meets the Planck Limit
            if local_density >= self.PLANCK_LIMIT:
                # STATE CHECK: Falling or Spinning?
                if current_phase.imag > 0:
                    # === EVENT A: THE INVERSION (Impact / The McTwist) ===
                    new_phase = np.conj(current_phase)
                    self.I_tensor[i, i] = new_phase
                    status_report = "!!! INVERSION (IMPACT) !!!"
                else:
                    # === EVENT B: THE RINGDOWN (Entropy / Golden Decay) ===
                    decay_factor = 1.0 / self.PHI
                    self.I_tensor[i, i] = current_phase * decay_factor
                    
                    # Mass Drain Integration: Energy escape drops localized density
                    # This pulls the system back down under 1.0, completing the cycle!
                    self.R_tensor[i, i] *= decay_factor 
                    status_report = ">>> RINGDOWN (MASS-ENERGY DECAY) >>>"
                    
        return status_report

    def step(self):
        """
        Maintains Relativistic Time Dilation.
        Extracts multi-axis coordinate elements cleanly to prevent numpy truth errors.
        """
        # Pull the primary active spatial coordinate axis (Axis 1) scalar explicitly
        current_density = self.R_tensor[1, 1]
        compression_factor = 1.0 / (self.PHI ** 3)
        
        if current_density > 0.0:
            drag = 1.0 + (current_density / compression_factor)
            # Compressor scales time steps responsively without freezing completely
            self.dt = 1.0 / drag
        else:
            self.dt = 1.0
            
        self.t_step += self.dt
        status = self.run_taber_phase_check()
        
        snapshot = {
            "time": float(self.t_step),
            "density_r": float(self.R_tensor[1, 1]),
            "metric_g": float(self.g_tensor[1, 1]),
            "phase_imag": float(self.I_tensor[1, 1].imag),
            "status": status
        }
        self.history.append(snapshot)
        return snapshot

    def export_data(self, filename="nkst_telemetry.h5"):
        """
        Secured Atomic File Writing from Version 2.6.
        """
        clean_filename = os.path.basename(filename)
        t_series = [s["time"] for s in self.history]
        r_series = [s["density_r"] for s in self.history]
        g_series = [s["metric_g"] for s in self.history]
        i_series = [s["phase_imag"] for s in self.history]
        
        tmp_filename = f"{clean_filename}.tmp"
        try:
            with h5py.File(tmp_filename, "w") as f:
                f.create_dataset("time", data=t_series)
                f.create_dataset("density", data=r_series)
                f.create_dataset("metric_g", data=g_series)
                f.create_dataset("phase_spin", data=i_series)
                f.attrs["engine_version"] = "3.9 (Pure Linear Avoidance)"
            os.replace(tmp_filename, clean_filename)
            print(f"[System] Telemetry exported successfully to {clean_filename}")
        except Exception as e:
            if os.path.exists(tmp_filename):
                os.remove(tmp_filename)
            print(f"[Error] Critical IO Failure: {str(e)}")
            raise e

if __name__ == "__main__":
    sim = NKST_Universe()
    print("\n[Sim] Beginning Unified Singularity Avoidance Sequence...")
    
    # Run loop using your injection parameters to observe the true physical cycle
    for t in range(50):
        sim.inject_mass(0.25, axis=1)
        data = sim.step()
        
        # Print status updates cleanly for all boundary breaches and decay states
        if t % 5 == 0 or "!!!" in data['status'] or ">>>" in data['status']:
            print(f"Loop={t:02d} | T_Clock={data['time']:.3f} | Density={data['density_r']:.5f} | Metric_G={data['metric_g']:.1f} | Phase={data['phase_imag']:.4f}j | {data['status']}")
            time.sleep(0.01)
            
    sim.export_data()
