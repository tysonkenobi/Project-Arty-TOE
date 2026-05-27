import numpy as np
import h5py
import time
import os
from collections import deque
from pathlib import Path

# ==============================================================================
# NKST SIMULATION ENGINE (v6.4 - COMPLETED PRODUCTION BASELINE)
# Core Logic: Continuous Asymptotic Field Mapping on Strict Integer Thresholds
# ==============================================================================

class NKST_Universe:
    def __init__(self, max_history=1000):
        print("[System] Initializing Minkowski Vacuum (Planck Normalized)...")
        self.PHI = 1.6180339887
        self.PLANCK_LIMIT = 1.0
        self.EPSILON = 1e-9
        
        # Space-Time Metric and Mass-Density Tensors
        self.g_tensor = np.zeros((4, 4))
        np.fill_diagonal(self.g_tensor, [-1.0, 1.0, 1.0, 1.0])
        self.R_tensor = np.zeros((4, 4))
        
        # Rigorous Rigid Body Scalar Constants: Moments of Inertia (I1 < I2 < I3)
        self.I1 = 1.0
        self.I2 = 2.0
        self.I3 = 3.0
        
        # State Vector: Angular Velocity components for each respective axis
        self.omega = np.array([0.5, 0.4, 0.1])
        
        # Quantum Phase Space
        self.I_tensor = np.zeros((4, 4), dtype=complex)
        self.I_tensor.fill(0 + 1j * self.PHI)
        
        # Simulation Parameters
        self.history = deque(maxlen=max_history)
        self.t_step = 0.0
        self.dt = 1.0
        self.momentum_direction = 1.0 

    def _update_metric_geometry(self, axis=1):
        """
        Maps mass density to spatial curvature using a smooth asymptotic curve.
        Utilizes a micro-buffer to prevent flat step-clamping on strict integer walls.
        """
        density = float(self.R_tensor[axis, axis])
        
        # Dynamic continuous boundary scaling
        if density >= self.PLANCK_LIMIT:
            # Micro-buffer to maintain high-resolution curvature scaling at the apex
            effective_gap = self.EPSILON * 100
        else:
            effective_gap = self.PLANFLIMIT = self.PLANCK_LIMIT - density
            if effective_gap < self.EPSILON:
                effective_gap = self.EPSILON
            
        self.g_tensor[axis, axis] = 1.0 / effective_gap

    def inject_mass(self, density_amount, axis=1):
        """Integrates mass along the active coordinate vector path."""
        increment = density_amount * self.momentum_direction
        self.R_tensor[axis, axis] += increment
        
        if self.R_tensor[axis, axis] < 0.0:
            self.R_tensor[axis, axis] = 0.0
            self.momentum_direction = 1.0 
            
        self._update_metric_geometry(axis)

    def run_dzhanibekov_flip_check(self, axis=1):
        """Executes explicit scalar rigid-body intermediate-axis Euler updates."""
        status_report = "Stable Trajectory"
        boundary_wall = self.PLANCK_LIMIT - self.EPSILON
        local_density = float(self.R_tensor[axis, axis])
        
        # Boundary Condition Encountered
        if local_density >= boundary_wall and self.momentum_direction > 0:
            status_report = "!!! DZHANIBEKOV FLIP (AXIAL INVERSION) !!!"
            
            # Isolated scalar rotation calculations to avoid matrix alignment dampening
            for _ in range(5):
                alpha1 = ((self.I2 - self.I3) / self.I1) * self.omega * self.omega
                alpha2 = ((self.I3 - self.I1) / self.I2) * self.omega * self.omega
                alpha3 = ((self.I1 - self.I2) / self.I3) * self.omega * self.omega
                
                self.omega += alpha1 * 0.05
                self.omega += alpha2 * 0.05
                self.omega += alpha3 * 0.05
            
            self.momentum_direction = -1.0
            self.I_tensor[axis, axis] = np.conj(self.I_tensor[axis, axis])
            
        elif self.momentum_direction < 0:
            decay_factor = 1.0 / self.PHI
            self.I_tensor[axis, axis] *= decay_factor
            status_report = ">>> RAMP DOWN (ENERGY ESCAPE CYCLE) >>>"
            self.omega *= 0.95
            
        return status_report

    def step(self, axis=1):
        """Calculates time dilation driven by coordinate tracking fields."""
        current_density = float(self.R_tensor[axis, axis])
        
        # Wrapped calculation in np.sum() to flatten vectors into a scalar kinetic energy value
        rot_ke = 0.5 * np.sum(self.I1*(self.omega**2) + self.I2*(self.omega**2) + self.I3*(self.omega**2))
        
        total_energy_stress = current_density + rot_ke
        compression_factor = 1.0 / (self.PHI ** 3)
        
        if total_energy_stress > 0.0:
            drag = 1.0 + (total_energy_stress / compression_factor)
            self.dt = 1.0 / drag
        else:
            self.dt = 1.0
            
        self.t_step += self.dt
        status = self.run_dzhanibekov_flip_check(axis)
        
        snapshot = {
            "time": float(self.t_step),
            "density_r": float(self.R_tensor[axis, axis]),
            "metric_g": float(self.g_tensor[axis, axis]),
            "phase_imag": float(self.I_tensor[axis, axis].imag),
            "direction": float(self.momentum_direction),
            "rot_energy": float(rot_ke),
            "status": status
        }
        self.history.append(snapshot)
        return snapshot

    def export_data(self, filename="nkst_telemetry.h5"):
        """Saves telemetry stream utilizing safe output operations."""
        safe_name = Path(filename).name
        target_path = Path("./exports").resolve() / safe_name
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        tmp_path = target_path.with_suffix('.tmp')
        
        t_series = [s["time"] for s in self.history]
        r_series = [s["density_r"] for s in self.history]
        g_series = [s["metric_g"] for s in self.history]
        i_series = [s["phase_imag"] for s in self.history]
        ke_series = [s["rot_energy"] for s in self.history]
        
        try:
            with h5py.File(tmp_path, "w") as f:
                f.create_dataset("time", data=t_series)
                f.create_dataset("density", data=r_series)
                f.create_dataset("metric_g", data=g_series)
                f.create_dataset("phase_spin", data=i_series)
                f.create_dataset("kinetic_energy", data=ke_series)
                f.attrs["engine_version"] = "6.4 (Completed Baseline Build)"
            
            os.replace(tmp_path, target_path)
            print(f"[System] Telemetry smoothly exported to {target_path}")
        except Exception as e:
            if tmp_path.exists():
                tmp_path.unlink()
            print(f"[Error] Storage Write Failure: {str(e)}")
            raise e

if __name__ == "__main__":
    sim = NKST_Universe()
    print("\n[Sim] Beginning Coupled Dzhanibekov Inversion Sequence...")
    
    for t in range(50):
        sim.inject_mass(0.25, axis=1)
        data = sim.step(axis=1)
        
        if t % 3 == 0 or "!!!" in data['status'] or ">>>" in data['status']:
            print(f"Loop={t:02d} | Density={data['density_r']:.4f} | Rot_KE={data['rot_energy']:.4f} | Metric_G={data['metric_g']:.2f} | {data['status']}")
            
    sim.export_data()
