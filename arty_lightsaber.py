import time
import sys
import threading
import os

# ==============================================================================
# ARTY_LIGHTSABER v2.0 (Interactive)
# Logic: NKST Boundary Confinement with Variable Geometry
# ==============================================================================

class KyberCrystal:
    def __init__(self):
        self.active = False
        self.resonance = 1.618 
    
    def pulse(self):
        """Emits plasma only if active"""
        if self.active:
            return {"pos": 0.0, "vel": 1.0, "phase": 1.0 + 0j, "type": "PLASMA"}
        return None

class NKST_ContainmentField:
    def __init__(self, max_length=20):
        self.max_length = max_length
        self.current_limit = 0 # Starts collapsed
        self.target_limit = 0
        
    def update_field_integrity(self):
        """Smoothly expands or contracts the Event Horizon"""
        if self.current_limit < self.target_limit:
            self.current_limit += 1 # Extend
        elif self.current_limit > self.target_limit:
            self.current_limit -= 1 # Retract (Collapse the wall)
            
    def apply_boundary_logic(self, particle):
        """
        THE McTWIST PROTOCOL
        """
        # 1. Check if particle hit the current (moving) wall
        if particle["pos"] >= self.current_limit:
            
            # 2. Trigger Vector Inversion (Reflection)
            particle["vel"] = -1.0 # Bounce back
            
            # 3. Convert to Imaginary Phase (Containment)
            # Real Energy becomes Spin
            particle["phase"] = complex(0, -1.0)
            particle["type"] = "RECIRC"
            
            # 4. Clamp to the moving wall
            particle["pos"] = self.current_limit - 0.1
            return True
            
        # 5. Hilt Re-absorption (Energy Conservation)
        elif particle["pos"] <= 0 and particle["type"] == "RECIRC":
            particle["type"] = "ABSORBED" # Marked for deletion
            return False
            
        return False

class Lightsaber:
    def __init__(self):
        self.crystal = KyberCrystal()
        self.field = NKST_ContainmentField(max_length=25)
        self.particles = []
        self.running = True
        self.state_label = "OFFLINE"

    def toggle_power(self):
        if self.crystal.active:
            # RETRACT SEQUENCE
            self.crystal.active = False
            self.field.target_limit = 0 # Collapse the field
            self.state_label = "RETRACTING..."
        else:
            # IGNITION SEQUENCE
            self.crystal.active = True
            self.field.target_limit = self.field.max_length # Extend the field
            self.state_label = "IGNITING..."

    def physics_tick(self):
        # 1. Move the Wall (Extend/Retract)
        self.field.update_field_integrity()
        
        # 2. Emit New Energy (If Active)
        new_p = self.crystal.pulse()
        if new_p:
            self.particles.append(new_p)
            
        # 3. Update All Particles
        active_particles = []
        for p in self.particles:
            # Move
            p["pos"] += p["vel"]
            
            # Apply NKST Logic
            self.field.apply_boundary_logic(p)
            
            # Keep only if not absorbed
            if p["type"] != "ABSORBED":
                active_particles.append(p)
                
        self.particles = active_particles

    def render(self):
        # Clear Line (ANSI Escape)
        sys.stdout.write("\033[K") 
        
        # Buffer
        buffer = [" "] * (self.field.max_length + 10)
        
        # Draw Hilt
        buffer[0] = "H"
        buffer[1] = "]"
        
        # Draw Particles
        energy_sum = 0
        for p in self.particles:
            idx = int(p["pos"]) + 2
            if 2 <= idx < len(buffer):
                if p["type"] == "PLASMA":
                    buffer[idx] = "=" # Outbound (Real)
                else:
                    buffer[idx] = "~" # Inbound (Imaginary/Spin)
                energy_sum += 1

        # Draw The Tip (The Event Horizon)
        # Only visible if extended
        if self.field.current_limit > 0:
            tip_idx = self.field.current_limit + 2
            if tip_idx < len(buffer):
                buffer[tip_idx] = "|" # The Hard Deck

        visual = "".join(buffer)
        
        # Status Line
        status = f"\r{visual}  [Status: {self.state_label}] [L: {self.field.current_limit}]"
        sys.stdout.write(status)
        sys.stdout.flush()

def input_listener(saber):
    """Runs in background thread to catch keystrokes"""
    print("------------------------------------------------")
    print(" COMMANDS: [ENTER] = Toggle Power  |  [q] = Quit")
    print("------------------------------------------------")
    while saber.running:
        cmd = input()
        if cmd.lower() == 'q':
            saber.running = False
            print("\n Shutting down physics engine...")
        else:
            saber.toggle_power()

# ==============================================================================
# MAIN LOOP
# ==============================================================================
if __name__ == "__main__":
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Init
    saber = Lightsaber()
    
    # Start Input Thread
    t = threading.Thread(target=input_listener, args=(saber,))
    t.daemon = True
    t.start()
    
    # Start Physics Loop (Main Thread)
    try:
        while saber.running:
            saber.physics_tick()
            saber.render()
            time.sleep(0.04) # 25 FPS
            
            # Check idle state
            if not saber.crystal.active and len(saber.particles) == 0:
                 saber.state_label = "STANDBY"
                 
    except KeyboardInterrupt:
        print("\nForce Quit.")

