import numpy as np
import h5py
import time
import os
from collections import deque
from pathlib import Path

# ==============================================================================
# NKST SIMULATION ENGINE (v6.8 - ENERGY CONSERVING DZHANIBEKOV SIMULATOR)
# Core Logic: Continuous Asymptotic Field Mapping Across 3D Spatial Curvatures
# ==============================================================================

class NKST_Universe:
    def __init__(self, max_history=1000):
        print("[System] Initializing Multi-Axis Minkowski Vacuum (Planck Normalized)...")
        self.PHI = 1.618033988749895
        self.PLANCK_LIMIT = 1.0
        self.EPSILON = 1e-9
        
        # 4x4 Space-Time Metric and Mass-Density Tensors
        self.g_tensor = np.zeros((4, 4), dtype=float)
        np.fill_diagonal(self.g_tensor, [-1.0, 1.0, 1.0, 1.0])
        self.R_tensor = np.zeros((4, 4), dtype=float)
        
        # Rigid Body Baseline Moments of Inertia (I1 < I2 < I3)
        self.I1_base = 1.0
        self.I2_base = 2.0
        self.I3_base = 3.0
        
        # Dynamic tracking arrays for actual moments of inertia
        self.I1 = self.I1_base
        self.I2 = self.I2_base
        self.I3 = self.I3_base
        
        # Explicit State Vector: Independent Angular Velocity components [w1, w2, w3]
        # w2 mapped to the intermediate unstable axis to trigger the McTwist mechanics
        self.w1 = 0.5
        self.w2 = 4.0
        self.w3 = 0.1
        
        # Quantum Complex Phase Space
        self.I_tensor = np.zeros((4, 4), dtype=complex)
        self.I_tensor.fill(0.0 + 1j * self.PHI)
        
        # Multi-Axis Simulation Trackers
        self.history = deque(maxlen=max_history)
        self.t_step = 0.0
        self.dt = 1.0
        
        # Momentum direction tracking vector for axes x(1), y(2), z(3)
        self.momentum_direction = np.array([0.0, 1.0, 1.0, 1.0], dtype=float)

    def _update_metric_geometry(self, axis):
        """
        Maps mass density to localized spatial curvature using Golden Ratio tensor spacing.
        Establishes coupling from metric expansions to independent moments of inertia.
        """
        density = float(self.R_tensor[axis, axis])
        
        # Micro-stepping continuous boundary safety buffers via geometric decay
        if density >= self.PLANCK_LIMIT:
            effective_gap = self.EPSILON / (self.PHI ** 2)
        else:
            effective_gap = self.PLANCK_LIMIT - density
            if effective_gap < self.EPSILON:
                effective_gap = self.EPSILON
                
        # GOLDEN RATIO TENSOR SPACING: Inflate the metric space geometrically near the boundary
        self.g_tensor[axis, axis] = (1.0 + (self.PHI / (effective_gap + self.EPSILON)))
        
        # TENSORIAL COUPLING: Perpendicular spatial deformations scale individual inertia moments
        # Component scaling reflects dimensional contraction under high localized metric stress
        g_scale_x = 1.0 / (1.0 + np.log(self.g_tensor[1, 1]))
        g_scale_y = 1.0 / (1.0 + np.log(self.g_tensor[2, 2]))
        g_scale_z = 1.0 / (1.0 + np.log(self.g_tensor[3, 3]))
        
        self.I1 = self.I1_base * g_scale_x
        self.I2 = self.I2_base * g_scale_y
        self.I3 = self.I3_base * g_scale_z

    def inject_mass_mesh(self, density_amounts):
        """
        Accepts an array/list of mass increments for spatial coordinate paths.
        Example: [0.025, 0.010, 0.005] maps to X, Y, and Z axes.
        """
        for i, amount in enumerate(density_amounts):
            axis = i + 1  # Map to index paths 1, 2, 3
            increment = amount * self.momentum_direction[axis]
            self.R_tensor[axis, axis] += increment
            
            if self.R_tensor[axis, axis] < 0.0:
                self.R_tensor[axis, axis] = 0.0
                self.momentum_direction[axis] = 1.0
                
            self._update_metric_geometry(axis)
    def run_dzhanibekov_flip_mesh(self, tracking_axis=1):
        """
        Executes explicit, scalar-isolated rigid-body intermediate-axis Euler updates.
        Manages boundary transitions across all spatial dimensions simultaneously.
        """
        status_report = "Stable Trajectory"
        boundary_wall = self.PLANCK_LIMIT - self.EPSILON
        
        # Scaling integration step size safely using time dilation metrics
        dt_physics = 0.01 * self.dt
        
        # LINEAR TO ANGULAR MOMENTUM COUPLED TRANSFER (The Skateboarder Halfpipe Ramp)
        local_stress = float(self.R_tensor[tracking_axis, tracking_axis])
        
        # ASYMPTOTIC DAMPENING: Diminish torque as time step approaches zero to prevent numerical blowouts
        coupling_torque = (self.PHI / (self.PLANCK_LIMIT - local_stress + self.EPSILON)) * 0.005 * self.dt
        
        if self.momentum_direction[tracking_axis] > 0:
            self.w2 += coupling_torque * dt_physics

        # TRUE EULER EQUATIONS: Explicit cross-axis scalar components
        dw1 = ((self.I2 - self.I3) / self.I1) * self.w2 * self.w3
        dw2 = ((self.I3 - self.I1) / self.I2) * self.w1 * self.w3
        dw3 = ((self.I1 - self.I2) / self.I3) * self.w1 * self.w2
        
        self.w1 += dw1 * dt_physics
        self.w2 += dw2 * dt_physics
        self.w3 += dw3 * dt_physics
        
        # Evaluate the chosen primary tracking axis status
        current_direction = self.momentum_direction[tracking_axis]
        
        if local_stress >= boundary_wall and current_direction > 0:
            status_report = "!!! DZHANIBEKOV FLIP (AXIAL INVERSION) !!!"
            
            # CRITICAL FIX: The internal micro-stepping buffer must scale directly with local time dilation (dt_physics)
            # This mitigates unphysical energy magnification near the coordinate limit boundary
            boundary_dt = 0.05 * dt_physics
            
            for _ in range(5):
                dw1_b = ((self.I2 - self.I3) / self.I1) * self.w2 * self.w3
                dw2_b = ((self.I3 - self.I1) / self.I2) * self.w1 * self.w3
                dw3_b = ((self.I1 - self.I2) / self.I3) * self.w1 * self.w2
                
                self.w1 += dw1_b * boundary_dt
                self.w2 += dw2_b * boundary_dt
                self.w3 += dw3_b * boundary_dt
                
            # Trigger direction reversal on all active highly stressed spatial lines
            for ax in range(1, 4):
                if self.R_tensor[ax, ax] >= boundary_wall:
                    self.momentum_direction[ax] = -1.0
                    self.I_tensor[ax, ax] = np.conj(self.I_tensor[ax, ax])
                    
        elif current_direction < 0:
            status_report = ">>> RAMP DOWN (ENERGY ESCAPE CYCLE) >>>"
            
            # Unitary complex phase rotation preserves tracking tensor modulus (Information Conservation)
            phase_angle = 1.0 / self.PHI
            unitary_rotation = np.exp(-1j * phase_angle * dt_physics)
            
            for ax in range(1, 4):
                if self.momentum_direction[ax] < 0:
                    self.I_tensor[ax, ax] *= unitary_rotation
                    
            # Continuous asymptotic velocity decay scaled to time dilation step
            decay_factor = 0.95 ** self.dt
            self.w1 *= decay_factor
            self.w2 *= decay_factor
            self.w3 *= decay_factor
            
        return status_report

    def step_mesh(self, tracking_axis=1):
        """Calculates tensor time dilation across total system stress states."""
        total_density_stress = float(self.R_tensor[1, 1] + self.R_tensor[2, 2] + self.R_tensor[3, 3])
        
        # Exact mathematical Rotational Kinetic Energy formula
        rot_ke = 0.5 * (self.I1 * (self.w1**2) + self.I2 * (self.w2**2) + self.I3 * (self.w3**2))
        total_energy_stress = total_density_stress + rot_ke
        
        compression_factor = 1.0 / (self.PHI ** 3)
        if total_energy_stress > 0.0:
            drag = 1.0 + (total_energy_stress / compression_factor)
            self.dt = 1.0 / drag
        else:
            self.dt = 1.0
            
        self.t_step += self.dt
        
        # Evaluate mechanics and boundary conditions
        status = self.run_dzhanibekov_flip_mesh(tracking_axis)
        
        snapshot = {
            "time": float(self.t_step),
            "density_x": float(self.R_tensor[1, 1]),
            "density_y": float(self.R_tensor[2, 2]),
            "metric_g_track": float(self.g_tensor[tracking_axis, tracking_axis]),
            "phase_imag_track": float(self.I_tensor[tracking_axis, tracking_axis].imag),
            "direction_track": float(self.momentum_direction[tracking_axis]),
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
        rx_series = [s["density_x"] for s in self.history]
        ry_series = [s["density_y"] for s in self.history]
        g_series = [s["metric_g_track"] for s in self.history]
        i_series = [s["phase_imag_track"] for s in self.history]
        ke_series = [s["rot_energy"] for s in self.history]
        
        try:
            with h5py.File(tmp_path, "w") as f:
                f.create_dataset("time", data=t_series)
                f.create_dataset("density_x", data=rx_series)
                f.create_dataset("density_y", data=ry_series)
                f.create_dataset("metric_g", data=g_series)
                f.create_dataset("phase_spin", data=i_series)
                f.create_dataset("kinetic_energy", data=ke_series)
                f.attrs["engine_version"] = "6.8 (Energy Stabilized Integration)"
                
            os.replace(tmp_path, target_path)
            print(f"[System] Telemetry smoothly exported to {target_path}")
        except Exception as e:
            if tmp_path.exists():
                tmp_path.unlink()
            print(f"[Error] Storage Write Failure: {str(e)}")
            raise e

if __name__ == "__main__":
    sim = NKST_Universe()
    print("\n[Sim] Beginning Coupled Multi-Axis Inversion Sequence...")
    
    for t in range(75):
        sim.inject_mass_mesh([0.025, 0.012, 0.006])
        data = sim.step_mesh(tracking_axis=1)
        
        if t % 3 == 0 or "!!!" in data['status'] or ">>>" in data['status']:
            print(f"Loop={t:02d} | Density_X={data['density_x']:.4f} | Rot_KE={data['rot_energy']:.6f} | Metric_G_X={data['metric_g_track']:.2f} | {data['status']}")
            
    sim.export_data()
