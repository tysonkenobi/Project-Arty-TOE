import numpy as np
import h5py
import time
import os

# ==============================================================================
# NKST SIMULATION ENGINE (v5.1 - FIXED DZHANIBEKOV AXIAL BUILD)
# Core Logic: Matter Freezes (Time Dilation) | Boundary Reversal (Dzhanibekov)
# Fix: Resolved Matrix-to-Scalar Dimension Flaw in Time Dilation Loop
# ==============================================================================

class NKST_Universe:
    def __init__(self):
        print("[System] Initializing Minkowski Vacuum (Planck Normalized)...")
        self.PHI = 1.6180339887
        self.PLANCK_LIMIT = 1.0
        self.EPSILON = 1e-9  
        
        # Space-Time Metric and Mass-Density Tensors
        self.g_tensor = np.zeros((4, 4))
        np.fill_diagonal(self.g_tensor, [-1.0, 1.0, 1.0, 1.0])
        self.R_tensor = np.zeros((4, 4))
        
        # State Vector: Angular Momentum mapping for Dzhanibekov modeling
        # Index 0 = Stable Axis, Index 1 = Intermediate (Unstable) Axis, Index 2 = Major Axis
        self.omega = np.array([0.1, 0.01, 0.0]) 
        
        # Quantum Phase Space
        self.I_tensor = np.zeros((4, 4), dtype=complex)
        self.I_tensor.fill(0 + 1j * self.PHI)
        
        # Simulation Parameters
        self.history = []
        self.t_step = 0.0
        self.dt = 1.0
        self.momentum_direction = 1.0  # 1.0 = Climbing up the ramp, -1.0 = Moving back down

    def _update_metric_geometry(self, axis=1):
        """Maps mass density directly to spatial curvature geometry."""
        denominator = 1.0 - self.R_tensor[axis, axis]
        if denominator < self.EPSILON:
            denominator = self.EPSILON
        self.g_tensor[axis, axis] = 1.0 / denominator

    def inject_mass(self, density_amount, axis=1):
        """
        Integrates mass along the direction of the momentum vector.
        The momentum_direction flips dynamically when a Dzhanibekov inversion triggers.
        """
        increment = density_amount * self.momentum_direction
        self.R_tensor[axis, axis] += increment
        
        # Floor safety handling to ensure mass never falls below absolute vacuum
        if self.R_tensor[axis, axis] < 0.0:
            self.R_tensor[axis, axis] = 0.0
            self.momentum_direction = 1.0  # Reset trajectory to climb again
            
        self._update_metric_geometry(axis)

    def run_dzhanibekov_flip_check(self):
        """
        DZHANIBEKOV AXIAL REVERSAL PROTOCOL
        Uses rigid body intermediate-axis Euler equations to drive the McTwist inversion.
        """
        status_report = "Stable Trajectory"
        boundary_wall = self.PLANCK_LIMIT - self.EPSILON
        
        for i in range(1, 4):
            local_density = self.R_tensor[i, i]
            
            # Boundary Condition Breach: System meets or exceeds the Planck limit
            if local_density >= boundary_wall and self.momentum_direction > 0:
                status_report = "!!! DZHANIBEKOV FLIP (AXIAL INVERSION) !!!"
                
                # Simulate the unstable intermediate axis flip using rigid body constants
                # Moments of Inertia: I1 < I2 < I3 (Forces intermediate axis I2 to be unstable)
                I1, I2, I3 = 1.0, 2.0, 3.0
                
                # Execute 3 quick micro-steps of Euler's rotation equations to resolve the physical flip
                for _ in range(3):
                    alpha1 = ((I2 - I3) / I1) * self.omega[1] * self.omega[2]
                    alpha2 = ((I3 - I1) / I2) * self.omega[0] * self.omega[2]
                    alpha3 = ((I1 - I2) / I3) * self.omega[0] * self.omega[1]
                    
                    self.omega += np.array([alpha1, alpha2, alpha3]) * 0.1
                
                # Invert the trajectory direction vector (Turns everything around)
                self.momentum_direction = -1.0
                
                # Complex-conjugate the quantum information phase topology
                self.I_tensor[i, i] = np.conj(self.I_tensor[i, i])
                
            # Recovery/Drain Phase: System is actively moving back down the ramp
            elif self.momentum_direction < 0:
                decay_factor = 1.0 / self.PHI
                
                # Process the Golden Ratio Energy Decay
                self.I_tensor[i, i] *= decay_factor
                status_report = ">>> RAMP DOWN (ENERGY ESCAPE CYCLE) >>>"
                
                # Safely balance the system rotation vector back to ground state metrics
                self.omega *= decay_factor
                
        return status_report

    def step(self):
        """Advances the universal simulation clock while processing time dilation."""
        # FIXED: Explicitly isolate the active spatial coordinate scalar (Axis 1) 
        # to prevent global matrix-to-scalar type errors.
        current_density = float(self.R_tensor[1, 1])
        compression_factor = 1.0 / (self.PHI ** 3)
        
        if current_density > 0.0:
            drag = 1.0 + (current_density / compression_factor)
            self.dt = 1.0 / drag
        else:
            self.dt = 1.0
            
        self.t_step += self.dt
        status = self.run_dzhanibekov_flip_check()
        
        # Isolate coordinate elements explicitly for h5py safe logging
        snapshot = {
            "time": float(self.t_step),
            "density_r": float(self.R_tensor[1, 1]),
            "metric_g": float(self.g_tensor[1, 1]),
            "phase_imag": float(self.I_tensor[1, 1].imag),
            "direction": float(self.momentum_direction),
            "status": status
        }
        self.history.append(snapshot)
        return snapshot

    def export_data(self, filename="nkst_telemetry.h5"):
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
                f.attrs["engine_version"] = "5.1 (Dzhanibekov Production Build)"
            os.replace(tmp_filename, clean_filename)
            print(f"[System] Telemetry exported successfully to {clean_filename}")
        except Exception as e:
            if os.path.exists(tmp_filename):
                os.remove(tmp_filename)
            print(f"[Error] Critical IO Failure: {str(e)}")
            raise e

if __name__ == "__main__":
    sim = NKST_Universe()
    print("\n[Sim] Beginning Dzhanibekov Inversion Sequence...")
    
    # 50 step lifecycle verification
    for t in range(50):
        sim.inject_mass(0.25, axis=1)
        data = sim.step()
        
        if t % 3 == 0 or "!!!" in data['status'] or ">>>" in data['status']:
            print(f"Loop={t:02d} | Density={data['density_r']:.4f} | Metric_G={data['metric_g']:.1f} | Vector_Dir={data['direction']:.1f} | {data['status']}")
            time.sleep(0.01)
            
    sim.export_data()
